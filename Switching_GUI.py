import time
import numpy as np
import matplotlib
import winsound
import instruments
import matplotlib.pyplot as plt
import sys
import serial
import visa
from PyQt5 import QtCore, QtWidgets, uic

# Todo: replace tkinter boxes with qt

matplotlib.use('Qt5Agg')


def error_sound():
    winsound.PlaySound('C:\Windows\Media\Windows Background.wav', winsound.SND_FILENAME)


def alert_sound():
    winsound.PlaySound('C:\Windows\Media\Windows Notify System Generic.wav', winsound.SND_FILENAME)


class DataCollector(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    pos_data_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    neg_data_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    mutex = QtCore.QMutex()
    mutex.lock()
    is_stopped = False
    mutex.unlock()

    sb = instruments.SwitchBox()
    bb = instruments.BalanceBox()
    dmm = instruments.K2000()
    pg = instruments.K2461()
    pulse_assignments = {"I+": "B", "I-": "F"}  # configuration for a pulse from B to F
    pulse2_assignments = {"I+": "D", "I-": "H"}  # configuration for a pulse from D to H
    measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}  # here V1 is Vxy
    resistance_assignments = {'A': 86, 'B': 64, 'C': 50, 'D': 53, 'E': 86, 'F': 64, 'G': 50, 'H': 53}

    @QtCore.pyqtSlot()
    def start_measurement(self, mode, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n):
        self.mutex.lock()
        self.is_stopped = False
        self.mutex.unlock()

        error_flag, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n = self.handle_inputs(
            sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n)
        # If flag is true then something failed in parsing the inputs or connecting and the loop will not continue.
        if error_flag:
            return

        self.bb.enable_all()
        self.bb.set_resistances(self.resistance_assignments)

        if mode == "Pulse Current":
            self.pulse_and_measure(False, pulse_mag * 1e-3, pulse_width * 1e-3, meas_curr * 1e-6,
                                      meas_n, loop_n)
        elif mode == "Pulse Voltage":
            self.pulse_and_measure(True, pulse_mag, pulse_width * 1e-3, meas_curr * 1e-6,
                                   meas_n, loop_n)
        else:
            error_sound()
            print("Error with pulsing method selection")
            sys.exit(1)
        self.sb.close()
        self.bb.close()
        self.dmm.close()
        self.pg.close()
        self.finished.emit()

    def pulse_and_measure(self, volts, pulse_mag, pulse_width, meas_curr, meas_n, loop_n):
        # there is enough different between pos and neg pulses to keep these as "repeated code segments" IMO.
        start_time = time.time()
        for i in range(loop_n):
            self.mutex.lock()
            if self.is_stopped:
                break
            self.mutex.unlock()
            self.sb.switch(self.pulse1_assignments)
            time.sleep(200e-3)
            pulse1_time = time.time()
            if volts:
                self.pg.pulse_voltage(pulse_mag, pulse_width)
            else:
                self.pg.pulse_current(pulse_mag, pulse_width)
            time.sleep(200e-3)
            self.sb.switch(self.measure_assignments)
            self.pg.measure_n(meas_curr, meas_n)
            self.dmm.measure_n(meas_n)
            time.sleep(200e-3)
            self.dmm.trigger()
            self.pg.trigger()
            time.sleep(meas_n * 0.15)
            t, vxx, curr = self.pg.read_buffer(meas_n)
            vxy = self.dmm.read_buffer()
            self.pos_data_ready.emit(t + pulse1_time - start_time, vxx / curr, vxy / curr)

            self.mutex.lock()
            if self.is_stopped:
                break
            self.mutex.unlock()
            self.sb.switch(self.pulse2_assignments)
            time.sleep(200e-3)
            pulse2_time = time.time()
            if volts:
                self.pg.pulse_voltage(pulse_mag, pulse_width)
            else:
                self.pg.pulse_current(pulse_mag, pulse_width)
            time.sleep(200e-3)
            self.sb.switch(self.measure_assignments)
            self.pg.measure_n(meas_curr, meas_n)
            self.dmm.measure_n(meas_n)
            time.sleep(200e-3)
            self.dmm.trigger()
            self.pg.trigger()
            plt.pause(meas_n * 0.15)
            t, vxx, curr = self.pg.read_buffer(meas_n)
            vxy = self.dmm.read_buffer()
            self.neg_data_ready.emit(t + pulse2_time - start_time, vxx / curr, vxy / curr)
        self.finished.emit()

    def handle_inputs(self, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n):
        connection_flag = False
        conversion_flag = False

        try:
            sb_port = int(sb_port)
        except ValueError:
            error_sound()
            print('Invalid switchbox port please enter integer value.')
            conversion_flag = True

        try:
            bb_port = int(bb_port)
        except ValueError:
            error_sound()
            print('Invalid balance box port please enter integer value.')
            conversion_flag = True

        try:
            dmm_port = int(dmm_port)
        except ValueError:
            error_sound()
            print('Invalid keithley port please enter integer value.')
            conversion_flag = True

        try:
            pulse_mag = float(pulse_mag)
        except ValueError:
            error_sound()
            print('Invalid pulse magnitude. Please enter a valid float')
            conversion_flag = True

        try:
            pulse_width = float(pulse_width)
        except ValueError:
            error_sound()
            print('Invalid pulse width. Please enter a valid float')
            conversion_flag = True

        try:
            meas_curr = float(meas_curr)
        except ValueError:
            error_sound()
            print('Invalid probe current. Please enter a valid float')
            conversion_flag = True

        try:
            meas_n = int(meas_n)
        except ValueError:
            error_sound()
            print('Invalid measurement count per loop. Please enter an integer value')
            conversion_flag = True

        try:
            loop_n = int(loop_n)
        except ValueError:
            error_sound()
            print('Invalid number of loops. Please enter an integer value')
            conversion_flag = True

        try:
            self.sb.connect(sb_port)
        except serial.SerialException:
            error_sound()
            print(f"Could not connect to switch box on port COM{sb_port}.")
            connection_flag = True

        try:
            self.bb.connect(bb_port)
        except serial.SerialException:
            error_sound()
            print(f"Could not connect to balance box on port COM{bb_port}.")
            connection_flag = True

        try:
            self.dmm.connect(dmm_port)
        except visa.VisaIOError:
            error_sound()
            print(f"Could not connect to Keithley2000 on port COM{dmm_port}.")
            connection_flag = True

        try:
            self.pg.connect()
        except visa.VisaIOError:
            error_sound()
            print("Could not connect to keithley 2461.")
            connection_flag = True

        return connection_flag or conversion_flag, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, \
               meas_curr, meas_n, loop_n


class MyGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('switching_GUI_layoutfile.ui', self)  # Load the .ui file
        self.show()  # Show the GUI
        self.connect_signals()  # this also creates a new thread.
        self.create_plots()  # make figure axes and so on
        self.thread.start()  # start the thread created in "connect_signals()"

    def create_plots(self):
        # creates plots and axes objects to be used to plot data.
        self.rxx_fig = plt.figure(1)
        self.rxx_ax = plt.gca()
        self.rxx_pos_line, = self.rxx_ax.plot(self.pos_time, self.pos_rxx, 'b.')
        self.rxx_neg_line, = self.rxx_ax.plot(self.neg_time, self.neg_rxx, 'k.')
        self.rxx_ax.xlabel('Time (s)')
        self.rxx_ax.ylabel('R_xx (Ohms)')
        self.rxx_ax.ticklabel_format(useOffset=False)

        self.rxy_fig = plt.figure(2)
        self.rxy_ax = plt.gca()
        self.rxy_pos_line, = self.rxy_ax.plot(self.pos_time, self.pos_rxy, 'b.')
        self.rxy_neg_line, = self.rxy_ax.plot(self.neg_time, self.neg_rxy, 'k.')
        self.rxy_ax.xlabel('Time (s)')
        self.rxy_ax.ylabel('R_xy (Ohms)')
        self.rxy_ax.ticklabel_format(useOffset=False)

    def connect_signals(self):
        # Connect gui elements to slots.
        self.pulse_type_combobox.currentTextChanged.connect(self.on_mode_changed)
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        self.thread = QtCore.QThread()
        self.data_collector = DataCollector()
        self.data_collector.moveToThread(self.thread)
        self.data_collector.finished.connect(self.on_loop_over)
        self.data_collector.pos_data_ready.connect(self.on_pos_data_ready)
        self.data_collector.neg_data_ready.connect(self.on_neg_data_ready)

    def on_start(self):
        # Reset the data arrays to not append to previous measurements.
        self.pos_time = np.array([])
        self.neg_time = np.array([])
        self.pos_rxx = np.array([])
        self.neg_rxx = np.array([])
        self.pos_rxy = np.array([])
        self.neg_rxy = np.array([])
        # start the data collector method (can't use invoke method because can't pass arguments)
        self.data_collector.start_measurement(
            self.pulse_type_combobox.currentText(),
            self.sb_port_box.text(),
            self.bb_port_box.text(),
            self.dmm_port_box.text(),
            self.pulse_magnitude_box.text(),
            self.pulse_width_box.text(),
            self.probe_current_box.text(),
            self.measurement_count_box.text(),
            self.loop_count_box.text()
        )

    def on_mode_changed(self, string):
        # Redraw a few things when changing pulse mode.
        if string == "Pulse Current":
            self.pulse_magnitude_units_label.setText("mA")
            self.pulse_magnitude_box.setText("15")
            print("pulsing_current")
        elif string == "Pulse Voltage":
            self.pulse_magnitude_units_label.setText("V")
            self.pulse_magnitude_box.setText("5")
            print("pulsing_voltage")
        else:
            error_sound()
            print("Something went wrong with the combobox.")

    def on_stop(self):
        # Allows the collector to finish this half-loop (pulse) and for it to offload it's data etc and then to wait.
        mutex = QtCore.QMutex()
        try:
            mutex.lock()
            self.data_collector.is_stopped = True
            mutex.unlock()
        except:
            print("Failed to write due to mutex lock. Trying again.")
            mutex.lock()
            self.data_collector.is_stopped = True
            mutex.unlock()

    def on_loop_over(self):
        # when finished is emitted, this will save the data (I hope).
        data = np.column_stack((self.pos_time, self.pos_rxx, self.pos_rxy, self.neg_time, self.neg_rxx, self.neg_rxy))
        alert_sound()
        prompt_window = QtWidgets.QWidget()
        if QtWidgets.QMessageBox.question(prompt_window, 'Save Data?',
                                          'Would you like to save your data?', QtWidgets.QMessageBox.Yes,
                                          QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
            save_window = QtWidgets.QWidget()
            name, _ = QtWidgets.QFileDialog.getSaveFileName(save_window, "Save Data", "",
                                                            "Text Files (*.txt);; Data Files (*.dat);; All Files (*)")
            if name:  # if a name was entered, don't save otherwise
                np.savetxt(name, data, newline='\r\n', delimiter='\t')  # save
                print(f'Data saved as {name}')
            else:
                print('No Filename: Data not saved')
        else:
            print('Data not saved')

    def on_pos_data_ready(self, t, rxx, rxy):
        # After pos pulse, plot and store the data then save a backup
        self.pos_time = np.append(self.pos_time, t)
        self.pos_rxx = np.append(self.pos_rxx, rxx)
        self.pos_rxy = np.append(self.pos_rxy, rxy)
        self.rxx_pos_line.set_data(self.pos_time, self.pos_rxx)
        self.rxy_pos_line.set_data(self.pos_time, self.pos_rxy)
        self.refresh_graphs()
        data = np.column_stack((self.pos_time, self.pos_rxx, self.pos_rxy, self.neg_time, self.neg_rxx, self.neg_rxy))
        np.savetxt('temp_data.txt', data, newline='\r\n', delimiter='\t')

    def on_neg_data_ready(self, t, rxx, rxy):
        # After neg pulse, plot and store the data then save a backup
        self.neg_time = np.append(self.neg_time, t)
        self.neg_rxx = np.append(self.neg_rxx, rxx)
        self.neg_rxy = np.append(self.neg_rxy, rxy)
        self.rxx_neg_line.set_data(self.neg_time, self.neg_rxx)
        self.rxy_neg_line.set_data(self.neg_time, self.neg_rxy)
        self.refresh_graphs()
        data = np.column_stack((self.pos_time, self.pos_rxx, self.pos_rxy, self.neg_time, self.neg_rxx, self.neg_rxy))
        np.savetxt('temp_data.txt', data, newline='\r\n', delimiter='\t')

    def refresh_graphs(self):
        # Simply redraw the axes after changing data.
        self.rxx_ax.relim()
        self.rxx_ax.autoscale_view()
        self.rxx_fig.canvas.flush_events()
        self.rxy_ax.relim()
        self.rxy_ax.autoscale_view()
        self.rxy_fig.canvas.flush_events()
        # todo: test using plt.draw() instead. probably won't work tho.

# Starts the application running it's callback loops etc.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyGUI()
    window.resize(0, 0)
    app.exec_()
