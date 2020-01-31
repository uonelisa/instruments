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
    # dataReady = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray)
    mutex = QtCore.QMutex()
    mutex.lock()
    is_stopped = False
    mutex.unlock()

    sb = instruments.SwitchBox()
    bb = instruments.BalanceBox()
    dmm = instruments.K2000()
    pg = instruments.K2461()
    pulse1_assignments = {"I+": "B", "I-": "F"}  # configuration for a pulse from B to F
    pulse2_assignments = {"I+": "D", "I-": "H"}  # configuration for a pulse from D to H
    measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}  # here V1 is Vxy
    resistance_assignments = {'A': 86, 'B': 64, 'C': 50, 'D': 53, 'E': 86, 'F': 64, 'G': 50, 'H': 53}

    @QtCore.pyqtSlot()
    def start_measurement(self, mode, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n):
        self.mutex.lock()
        self.is_stopped = False
        self.mutex.unlock()

        flag, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n = self.handle_inputs(
            sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n)
        # If flag is true then something failed in parsing the inputs or connecting and the loop will not continue.
        if flag:
            return

        self.bb.enable_all()
        self.bb.set_resistances(self.resistance_assignments)

        if mode == "Pulse Current":
            data = self.pulse_current(pulse_mag * 1e-3, pulse_width * 1e-3, meas_curr * 1e-6,
                                      meas_n, loop_n)
        elif mode == "Pulse Voltage":
            data = self.pulse_voltage(pulse_mag, pulse_width * 1e-3, meas_curr * 1e-6,
                                      meas_n, loop_n)
        else:
            error_sound()
            print("Error with pulsing method selection")
            sys.exit(1)
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
        self.sb.close()
        self.bb.close()
        self.dmm.close()
        self.pg.close()
        self.finished.emit()

    def pulse_voltage(self, pulse_mag, pulse_width, meas_curr, meas_n, loop_n):
        pos_time = np.array([])
        neg_time = np.array([])
        pos_rxx = np.array([])
        neg_rxx = np.array([])
        pos_rxy = np.array([])
        neg_rxy = np.array([])
        start_time = time.time()
        plt.figure(1)
        plt.xlabel('Time (s)')
        plt.ylabel('R_xx (Ohms)')
        plt.ticklabel_format(useOffset=False)
        plt.figure(2)
        plt.xlabel('Time (s)')
        plt.ylabel('R_xy (Ohms)')
        plt.ticklabel_format(useOffset=False)
        for i in range(loop_n):
            self.mutex.lock()
            if self.is_stopped:
                break
            self.mutex.unlock()
            self.sb.switch(self.pulse1_assignments)
            time.sleep(200e-3)
            pulse1_time = time.time()
            self.pg.pulse_voltage(pulse_mag, pulse_width)
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
            pos_time = np.append(pos_time, t + pulse1_time - start_time)
            pos_rxx = np.append(pos_rxx, vxx / curr)
            pos_rxy = np.append(pos_rxy, vxy / curr)
            plt.figure(1)
            plt.plot(pos_time, pos_rxx, 'k+')
            plt.draw()
            plt.figure(2)
            plt.plot(pos_time, pos_rxy, 'k+')
            plt.draw()

            self.mutex.lock()
            if self.is_stopped:
                break
            self.mutex.unlock()
            self.sb.switch(self.pulse2_assignments)
            time.sleep(200e-3)
            pulse2_time = time.time()
            self.pg.pulse_voltage(pulse_mag, pulse_width)
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
            neg_time = np.append(neg_time, t + pulse2_time - start_time)
            neg_rxx = np.append(neg_rxx, vxx / curr)
            neg_rxy = np.append(neg_rxy, vxy / curr)
            plt.figure(1)
            plt.plot(neg_time, neg_rxx, 'r+')
            plt.draw()
            plt.figure(2)
            plt.plot(neg_time, neg_rxy, 'r+')
            plt.draw()
            # self.dataReady.emit(pos_time, pos_rxx, pos_rxy, neg_time, neg_rxx, neg_rxy)
        data = np.column_stack((pos_time, pos_rxx, pos_rxy, neg_time, neg_rxx, neg_rxy))
        return data

    def pulse_current(self, pulse_mag, pulse_width, meas_curr, meas_n, loop_n):
        pos_time = np.array([])
        neg_time = np.array([])
        pos_rxx = np.array([])
        neg_rxx = np.array([])
        pos_rxy = np.array([])
        neg_rxy = np.array([])
        start_time = time.time()
        plt.figure(1)
        plt.xlabel('Time (s)')
        plt.ylabel('R_xx (Ohms)')
        plt.ticklabel_format(useOffset=False)
        plt.figure(2)
        plt.xlabel('Time (s)')
        plt.ylabel('R_xy (Ohms)')
        plt.ticklabel_format(useOffset=False)
        for i in range(loop_n):
            self.sb.switch(self.pulse1_assignments)
            plt.pause(200e-3)
            pulse1_time = time.time()
            self.pg.pulse_current(pulse_mag, pulse_width)
            plt.pause(200e-3)
            self.sb.switch(self.measure_assignments)
            self.pg.measure_n(meas_curr, meas_n)
            self.dmm.measure_n(meas_n)
            plt.pause(200e-3)
            self.dmm.trigger()
            self.pg.trigger()
            plt.pause(meas_n * 0.15)
            t, vxx, curr = self.pg.read_buffer(meas_n)
            vxy = self.dmm.read_buffer()
            pos_time = np.append(pos_time, t + pulse1_time - start_time)
            pos_rxx = np.append(pos_rxx, vxx / curr)
            pos_rxy = np.append(pos_rxy, vxy / curr)
            plt.figure(1)
            plt.plot(pos_time, pos_rxx, 'k+')
            plt.draw()
            plt.figure(2)
            plt.plot(pos_time, pos_rxy, 'k+')
            plt.draw()

            self.sb.switch(self.pulse2_assignments)
            plt.pause(200e-3)
            pulse2_time = time.time()
            self.pg.pulse_current(pulse_mag, pulse_width)
            plt.pause(200e-3)
            self.sb.switch(self.measure_assignments)
            self.pg.measure_n(meas_curr, meas_n)
            self.dmm.measure_n(meas_n)
            plt.pause(200e-3)
            self.dmm.trigger()
            self.pg.trigger()
            plt.pause(meas_n * 0.15)
            t, vxx, curr = self.pg.read_buffer(meas_n)
            vxy = self.dmm.read_buffer()
            neg_time = np.append(neg_time, t + pulse2_time - start_time)
            neg_rxx = np.append(neg_rxx, vxx / curr)
            neg_rxy = np.append(neg_rxy, vxy / curr)
            plt.figure(1)
            plt.plot(neg_time, neg_rxx, 'r+')
            plt.draw()
            plt.figure(2)
            plt.plot(neg_time, neg_rxy, 'r+')
            plt.draw()
        data = np.column_stack((pos_time, pos_rxx, pos_rxy, neg_time, neg_rxx, neg_rxy))
        return data

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

        return connection_flag or conversion_flag, sb_port, bb_port, dmm_port, pulse_mag, pulse_width,\
               meas_curr, meas_n, loop_n


class MyGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('switching_GUI_layoutfile.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # connect buttons and actions to functions.
        self.pulse_type_combobox.currentTextChanged.connect(self.on_mode_changed)
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        self.thread = QtCore.QThread()
        self.data_collector = DataCollector()
        self.data_collector.moveToThread(self.thread)
        self.data_collector.finished.connect(self.on_loop_over)
        self.thread.start()

    def on_start(self):
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
        print('Loop Finished')


# Starts the application running it's callback loops etc.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyGUI()
    window.resize(0, 0)
    app.exec_()
