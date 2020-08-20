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


error_sound = instruments.error_sound
alert_sound = instruments.alert_sound


class DataCollector(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    pos_data_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    pos_scope_data_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    neg_data_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    neg_scope_data_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    finished_res_measurement = QtCore.pyqtSignal(np.ndarray, np.ndarray)

    mutex = QtCore.QMutex()
    mutex.lock()
    is_stopped = False
    mutex.unlock()

    sb = instruments.SwitchBox()
    bb = instruments.BalanceBox()
    dmm = instruments.K2000()
    pg = instruments.K2461()
    scope = instruments.DS1104()
    scope_enabled = False

    # pulse1_assignments = {"I+": "B", "I-": "F"}  # configuration for a pulse from B to F
    # pulse2_assignments = {"I+": "D", "I-": "H"}  # configuration for a pulse from D to H
    # measure_assignments = {"I+": "A", "I-": "E", "V1+": "B", "V1-": "D", "V2+": "C", "V2-": "G"}  # here V1 is Vxy

    # pulse1_assignments = {"I+": "A", "I-": "E"}
    # pulse2_assignments = {"I+": "C", "I-": "G"}
    # measure_assignments = {"I+": "H", "I-": "D", "V1+": "A", "V1-": "C", "V2+": "B", "V2-": "F"}

    pulse1_assignments = {"I+": "D", "I-": "H"}  # configuration for a pulse from B to F
    pulse2_assignments = {"I+": "H", "I-": "D"}  # configuration for a pulse from D to H
    measure_assignments = {"I+": "A", "I-": "E", "V1+": "B", "V1-": "D", "V2+": "C", "V2-": "G"}  # here V1 is Vxy

    resistance_assignments = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}
    two_wire_assignments = ({"I+": "A", "I-": "E"},
                            {"I+": "B", "I-": "F"},
                            {"I+": "C", "I-": "G"},
                            {"I+": "D", "I-": "H"},
                            )
    four_wire_assignments = ({"I+": "A", "I-": "E", "V1+": "B", "V1-": "D"},
                             {"I+": "B", "I-": "F", "V1+": "C", "V1-": "E"},
                             {"I+": "C", "I-": "G", "V1+": "D", "V1-": "F"},
                             {"I+": "D", "I-": "H", "V1+": "E", "V1-": "G"},
                             {"I+": "E", "I-": "A", "V1+": "F", "V1-": "H"},
                             {"I+": "F", "I-": "B", "V1+": "G", "V1-": "A"},
                             {"I+": "G", "I-": "C", "V1+": "H", "V1-": "B"},
                             {"I+": "H", "I-": "D", "V1+": "A", "V1-": "C"},
                             )
    reference_resistance = 10.0154663186062
    two_wire = 1500

    @QtCore.pyqtSlot(str, str, str, str, str, str, str, str, str, tuple)
    def start_measurement(self, mode, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n,
                          checkboxes):
        bb_enabled, scope_enabled = checkboxes
        self.mutex.lock()
        self.is_stopped = False
        self.mutex.unlock()

        error_flag, pulse_volts, pulse_mag, pulse_width, meas_curr, meas_n, loop_n = self.handle_inputs(mode,
                                                                                                        sb_port,
                                                                                                        bb_port,
                                                                                                        dmm_port,
                                                                                                        pulse_mag,
                                                                                                        pulse_width,
                                                                                                        meas_curr,
                                                                                                        meas_n, loop_n,
                                                                                                        bb_enabled,
                                                                                                        scope_enabled)
        # If flag is true then something failed in parsing the inputs or connecting and the loop will not continue.
        if error_flag:
            return

        self.pulse_and_measure(pulse_volts, pulse_mag, pulse_width, meas_curr,
                               meas_n, loop_n)

        self.sb.close()
        if bb_enabled:
            self.bb.close()
        if scope_enabled:
            self.scope.close()
        self.dmm.close()
        self.pg.close()
        # plt.pause()(1)
        self.finished.emit()

    @QtCore.pyqtSlot(str, str, str, str, str, str, str, str, str, bool)
    def resistance_measurement(self, mode, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n,
                               loop_n, bb_enabled):
        self.mutex.lock()
        self.is_stopped = False
        self.mutex.unlock()

        # Converts the strings in the gui boxes into appropriate types and then connects and sets up instruments.
        error_flag, pulse_volts, pulse_mag, pulse_width, meas_curr, meas_n, loop_n = self.handle_inputs(mode,
                                                                                                        sb_port,
                                                                                                        bb_port,
                                                                                                        dmm_port,
                                                                                                        pulse_mag,
                                                                                                        pulse_width,
                                                                                                        meas_curr,
                                                                                                        meas_n, loop_n,
                                                                                                        bb_enabled)

        # If something fails to connect, the UI doesn't continue
        if error_flag:
            return

        # reset the resistances to measure two wires properly
        if bb_enabled:
            self.bb.reset_resistances()

        two_wires = np.zeros(len(self.two_wire_assignments))
        four_wires = np.zeros(len(self.four_wire_assignments))

        for i in range(len(self.two_wire_assignments)):
            self.sb.switch(self.two_wire_assignments[i])
            time.sleep(0.3)
            self.pg.enable_2_wire_probe(meas_curr)
            time.sleep(0.2)
            c, v = self.pg.read_one()
            two_wires[i] = v / c
            self.pg.disable_probe_current()
        print('Two Wires: ', two_wires)

        for i in range(len(self.four_wire_assignments)):
            self.sb.switch(self.four_wire_assignments[i])
            time.sleep(0.3)
            self.pg.enable_4_wire_probe(meas_curr)
            time.sleep(0.2)
            c, v = self.pg.read_one()
            four_wires[i] = v / c
            self.pg.disable_probe_current()
        print('Four Wires: ', four_wires)

        if bb_enabled:
            self.bb.close()
        self.dmm.close()
        self.pg.close()
        self.sb.close()
        self.finished_res_measurement.emit(two_wires, four_wires)

    def pulse_and_measure(self, volts, pulse_mag, pulse_width, meas_curr, meas_n, loop_n):
        # see footnote on 6-110 in k2461 manual

        # todo(stu) add all the code to retrieve and save the oscope data
        self.dmm.measure_one()

        start_time = time.time()
        for loop_count in range(loop_n):
            self.mutex.lock()
            if self.is_stopped:
                return
            self.mutex.unlock()
            print('Loop count:', loop_count + 1, 'Pulse: 1')
            self.sb.switch(self.pulse1_assignments)
            self.pg.set_ext_trig(3)
            if self.scope_enabled:
                self.scope.single_trig()
            if volts:
                self.pg.prepare_pulsing_voltage(pulse_mag, pulse_width)
            time.sleep(0.2)
            pulse_t = time.time()
            if volts:
                self.pg.pulse_voltage()
            else:
                self.pg.pulse_current(pulse_mag, pulse_width)
            time.sleep(200e-3)
            self.sb.switch(self.measure_assignments)

            time.sleep(200e-3)
            self.pg.enable_4_wire_probe(meas_curr)
            time.sleep(200e-3)
            t = np.zeros(meas_n)
            vxx = np.zeros(meas_n)
            vxy = np.zeros(meas_n)
            curr = np.zeros(meas_n)
            for meas_count in range(meas_n):
                t[meas_count] = time.time()
                self.pg.trigger_fetch()
                self.dmm.trigger()
                vxx[meas_count], curr[meas_count] = self.pg.fetch_one()
                vxy[meas_count] = self.dmm.fetch_one()
            self.pg.disable_probe_current()
            self.pos_data_ready.emit(t - start_time, vxx / curr, vxy / curr)
            if self.scope_enabled:
                scope_data = self.scope.get_data(15001, 30000)
                time_step = float(self.scope.get_time_inc())
                scope_time = np.array(range(0, len(scope_data))) * time_step + pulse_t - start_time
                self.pos_scope_data_ready.emit(scope_time, scope_data / self.reference_resistance)

            self.mutex.lock()
            if self.is_stopped:
                return
            self.mutex.unlock()

            print('Loop count:', loop_count + 1, 'Pulse: 2')
            self.sb.switch(self.pulse2_assignments)
            self.pg.set_ext_trig(3)
            if self.scope_enabled:
                self.scope.single_trig()
            if volts:
                self.pg.prepare_pulsing_voltage(pulse_mag, pulse_width)

            time.sleep(0.2)
            pulse_t = time.time()
            if volts:
                self.pg.pulse_voltage()
            else:
                self.pg.pulse_current(pulse_mag, pulse_width)

            time.sleep(200e-3)
            self.sb.switch(self.measure_assignments)
            self.pg.enable_4_wire_probe(meas_curr)
            time.sleep(500e-3)

            t = np.zeros(meas_n)
            curr = np.zeros(meas_n)
            vxx = np.zeros(meas_n)
            vxy = np.zeros(meas_n)
            for meas_count in range(meas_n):
                t[meas_count] = time.time()
                self.pg.trigger_fetch()
                self.dmm.trigger()
                vxx[meas_count], curr[meas_count] = self.pg.fetch_one()
                vxy[meas_count] = self.dmm.fetch_one()
            self.pg.disable_probe_current()
            self.neg_data_ready.emit(t - start_time, vxx / curr, vxy / curr)

            if self.scope_enabled:
                scope_data = self.scope.get_data(15001, 30000)
                time_step = float(self.scope.get_time_inc())
                scope_time = np.array(range(0, len(scope_data))) * time_step + pulse_t - start_time
                self.neg_scope_data_ready.emit(scope_time, scope_data / self.reference_resistance)

    def handle_inputs(self, mode, sb_port, bb_port, dmm_port, pulse_mag, pulse_width, meas_curr, meas_n, loop_n,
                      bb_enabled, scope_enabled):
        connection_flag = False
        conversion_flag = False

        if mode == 'Pulse Current':
            pulse_volts = False
        elif mode == 'Pulse Voltage':
            pulse_volts = True
        else:
            print('Pulse mode selection error?')
            pulse_volts = False
            conversion_flag = True

        try:
            sb_port = int(sb_port)
        except ValueError:
            error_sound()
            print('Invalid switchbox port please enter integer value.')
            conversion_flag = True

        if bb_enabled:
            try:
                bb_port = int(bb_port)
            except ValueError:
                error_sound()
                print('Invalid balance box port please enter integer value.')
                conversion_flag = True
            self.bb.enable_all()
            self.bb.set_resistances(self.resistance_assignments)

        try:
            dmm_port = int(dmm_port)
        except ValueError:
            error_sound()
            print('Invalid keithley port please enter integer value.')
            conversion_flag = True

        try:
            if pulse_volts:
                pulse_mag = float(pulse_mag)
            else:
                pulse_mag = float(pulse_mag) * 1e-3
        except ValueError:
            error_sound()
            print('Invalid pulse magnitude. Please enter a valid float')
            conversion_flag = True

        try:
            pulse_width = float(pulse_width) * 1e-3
        except ValueError:
            error_sound()
            print('Invalid pulse width. Please enter a valid float')
            conversion_flag = True

        try:
            meas_curr = float(meas_curr) * 1e-6
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

        if bb_enabled:
            try:
                self.bb.connect(bb_port)
            except serial.SerialException:
                error_sound()
                print(f"Could not connect to balance box on port COM{bb_port}.")
                connection_flag = True

        if scope_enabled & pulse_volts:
            try:
                self.scope.connect()
                self.scope.prepare_for_pulse(pulse_mag, self.reference_resistance, self.two_wire)
                self.scope.set_trig_chan(3)
                # self.scope.single_trig()
                self.scope_enabled = True
                time.sleep(12)
            except visa.VisaIOError:
                error_sound()
                print("Could not connect to RIGOL DS1104Z.")
                connection_flag = True
        else:
            self.scope_enabled = False

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

        return connection_flag or conversion_flag, pulse_volts, pulse_mag, pulse_width, meas_curr, meas_n, loop_n

# TODO: I need to figure out how to make the tabbing order of the boxes in the gui consistent with vertical placement.
#  Currently it jumps around from top to middle, to bottom and back to 2nd then 4th then the next box.
class MyGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('switching_GUI_layoutfile.ui', self)  # Load the .ui file
        self.show()  # Show the GUI
        self.connect_signals()  # this also creates a new thread.
        self.thread.start()  # start the thread created in "connect_signals()"

    def connect_signals(self):
        # Connect gui elements to slots.
        self.pulse_type_combobox.currentTextChanged.connect(self.on_mode_changed)
        self.start_button.clicked.connect(self.on_start)
        self.start_res_button.clicked.connect(self.on_res_measurement)
        self.stop_button.clicked.connect(self.on_stop)
        self.thread = QtCore.QThread()
        self.data_collector = DataCollector()
        self.data_collector.moveToThread(self.thread)
        self.data_collector.finished.connect(self.on_loop_over)
        self.data_collector.pos_data_ready.connect(self.on_pos_data_ready)
        self.data_collector.pos_scope_data_ready.connect(self.on_pos_scope_data_ready)
        self.data_collector.neg_data_ready.connect(self.on_neg_data_ready)
        self.data_collector.neg_scope_data_ready.connect(self.on_neg_scope_data_ready)
        self.data_collector.finished_res_measurement.connect(self.on_res_finished)

    def on_start(self):

        self.scope_enabled = False
        # Reset the data arrays to not append to previous measurements.
        self.pos_time = np.array([])
        self.neg_time = np.array([])
        self.pos_rxx = np.array([])
        self.neg_rxx = np.array([])
        self.pos_rxy = np.array([])
        self.neg_rxy = np.array([])

        if self.scope_checkbox.isChecked():
            self.scope_enabled = True
            self.pos_scope_time = np.array([])
            self.pos_scope_data = np.array([])
            self.neg_scope_time = np.array([])
            self.neg_scope_data = np.array([])

        self.create_plots()  # make figure axes and so on

        # maximum of 9 arguments
        QtCore.QMetaObject.invokeMethod(self.data_collector, 'start_measurement', QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, self.pulse_type_combobox.currentText()),
                                        QtCore.Q_ARG(str, self.sb_port_box.text()),
                                        QtCore.Q_ARG(str, self.bb_port_box.text()),
                                        QtCore.Q_ARG(str, self.dmm_port_box.text()),
                                        QtCore.Q_ARG(str, self.pulse_magnitude_box.text()),
                                        QtCore.Q_ARG(str, self.pulse_width_box.text()),
                                        QtCore.Q_ARG(str, self.probe_current_box.text()),
                                        QtCore.Q_ARG(str, self.measurement_count_box.text()),
                                        QtCore.Q_ARG(str, self.loop_count_box.text()),
                                        QtCore.Q_ARG(tuple, (self.bb_enable_checkbox.isChecked(),
                                                             self.scope_checkbox.isChecked()))
                                        )

    def on_res_measurement(self):
        QtCore.QMetaObject.invokeMethod(self.data_collector, 'resistance_measurement', QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, self.pulse_type_combobox.currentText()),
                                        QtCore.Q_ARG(str, self.sb_port_box.text()),
                                        QtCore.Q_ARG(str, self.bb_port_box.text()),
                                        QtCore.Q_ARG(str, self.dmm_port_box.text()),
                                        QtCore.Q_ARG(str, self.pulse_magnitude_box.text()),
                                        QtCore.Q_ARG(str, self.pulse_width_box.text()),
                                        QtCore.Q_ARG(str, self.probe_current_box.text()),
                                        QtCore.Q_ARG(str, self.measurement_count_box.text()),
                                        QtCore.Q_ARG(str, self.loop_count_box.text()),
                                        QtCore.Q_ARG(bool, self.bb_enable_checkbox.isChecked())
                                        )

    def create_plots(self):
        # creates plots and axes objects to be used to plot data.
        # try:
        #     plt.close(self.rxx_fig)
        #     plt.close(self.rxy_fig)
        # except:
        #     print("no plots to close")
        self.graph_fig = plt.figure("Resistance Plots")
        self.rxx_ax = plt.subplot(211)
        self.rxx_ax.clear()
        self.rxx_pos_line, = self.rxx_ax.plot(self.pos_time, self.pos_rxx, 'k.')
        self.rxx_neg_line, = self.rxx_ax.plot(self.neg_time, self.neg_rxx, 'r.')
        # self.rxx_ax.set_xlabel('Time (s)')
        self.rxx_ax.set_ylabel('R_xx (Ohms)')
        self.rxx_ax.ticklabel_format(useOffset=False)

        self.rxy_ax = plt.subplot(212)
        self.rxy_ax.clear()
        self.rxy_pos_line, = self.rxy_ax.plot(self.pos_time, self.pos_rxy, 'k.')
        self.rxy_neg_line, = self.rxy_ax.plot(self.neg_time, self.neg_rxy, 'r.')
        self.rxy_ax.set_xlabel('Time (s)')
        self.rxy_ax.set_ylabel('R_xy (Ohms)')
        self.rxy_ax.ticklabel_format(useOffset=False)
        plt.show(block=False)
        self.refresh_switching_graphs()

        if self.scope_enabled:
            self.scope_fig = plt.figure("scope plots")
            self.scope_ax = plt.axes()
            self.scope_ax.clear()
            self.pos_scope_line, = self.scope_ax.plot(self.pos_scope_time, self.pos_scope_data / 1e3, 'k-')
            self.neg_scope_line, = self.scope_ax.plot(self.neg_scope_time, self.neg_scope_data / 1e3, 'r-')
            self.scope_ax.set_xlabel('Time (s)')
            self.scope_ax.set_ylabel('Pulse Current (mA)')
            self.scope_ax.ticklabel_format(useOffset=False)
            self.refresh_scope_graphs()
            plt.show(block=False)

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
        print("Stopping")

    def on_loop_over(self):
        print("Finished Loop")
        # when finished is emitted, this will save the data (I hope).
        try:
            # alert_sound()
            data = np.column_stack(
                (self.pos_time, self.pos_rxx, self.pos_rxy, self.neg_time, self.neg_rxx, self.neg_rxy))
            prompt_window = QtWidgets.QWidget()

            if QtWidgets.QMessageBox.question(prompt_window, 'Save Data?',
                                              'Would you like to save your data?', QtWidgets.QMessageBox.Yes,
                                              QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
                save_window = QtWidgets.QWidget()
                name, _ = QtWidgets.QFileDialog.getSaveFileName(save_window, "Save Data", "",
                                                                "Text Files (*.txt);; Data Files (*.dat);; All Files (*)")
                if name:  # if a name was entered, don't save otherwise
                    np.savetxt(name, data, newline='\n', delimiter='\t')  # save
                    print(f'Data saved as {name}')

                    if self.scope_enabled:
                        scope_name = name.split('.')[0] + '_scope.' + name.split('.')[1]
                        scope_data = np.column_stack(
                            (self.pos_scope_time, self.pos_scope_data, self.neg_scope_time, self.neg_scope_data))
                        np.savetxt(scope_name, scope_data, newline='\n', delimiter='\t')  # save scope data
                        print(f'Scope data saved as {scope_name}')
                else:
                    print('No Filename: Data not saved')
            else:
                print('Data not saved')
        except ValueError:
            print("Could not stack. Please manually combine and save pos_temp_data and neg_temp_data "
                  "(and scope data if used).")
        except:
            print("Data not saved, something went wrong! Please check the temp data files")

    def on_pos_data_ready(self, t, rxx, rxy):
        # After pos pulse, plot and store the data then save a backup
        self.pos_time = np.append(self.pos_time, t)
        self.pos_rxx = np.append(self.pos_rxx, rxx)
        self.pos_rxy = np.append(self.pos_rxy, rxy)
        self.rxx_pos_line.set_data(self.pos_time, self.pos_rxx)
        self.rxy_pos_line.set_data(self.pos_time, self.pos_rxy)
        self.refresh_switching_graphs()
        data = np.column_stack((self.pos_time, self.pos_rxx, self.pos_rxy))
        np.savetxt('pos_temp_data.txt', data, newline='\n', delimiter='\t')

    def on_pos_scope_data_ready(self, t, current):
        print('pos scope data ready')
        self.pos_scope_time = np.append(self.pos_scope_time, t)
        self.pos_scope_data = np.append(self.pos_scope_data, current)
        self.pos_scope_line.set_data(self.pos_scope_time, self.pos_scope_data)
        self.refresh_scope_graphs()
        scope_data = np.column_stack((self.pos_scope_time, self.pos_scope_data))
        np.savetxt('pos_temp_scope_data.txt', scope_data, newline='\n', delimiter='\t')

    def on_neg_data_ready(self, t, rxx, rxy):
        # After neg pulse, plot and store the data then save a backup
        self.neg_time = np.append(self.neg_time, t)
        self.neg_rxx = np.append(self.neg_rxx, rxx)
        self.neg_rxy = np.append(self.neg_rxy, rxy)
        self.rxx_neg_line.set_data(self.neg_time, self.neg_rxx)
        self.rxy_neg_line.set_data(self.neg_time, self.neg_rxy)
        self.refresh_switching_graphs()
        data = np.column_stack((self.neg_time, self.neg_rxx, self.neg_rxy))
        np.savetxt('neg_temp_data.txt', data, newline='\n', delimiter='\t')

    def on_neg_scope_data_ready(self, t, current):
        print('neg scope data ready')
        self.neg_scope_time = np.append(self.neg_scope_time, t)
        self.neg_scope_data = np.append(self.neg_scope_data, current)
        self.neg_scope_line.set_data(self.neg_scope_time, self.neg_scope_data)
        self.refresh_scope_graphs()
        scope_data = np.column_stack((self.neg_scope_time, self.neg_scope_data))
        np.savetxt('neg_temp_scope_data.txt', scope_data, newline='\n', delimiter='\t')

    def on_res_finished(self, two_wires, four_wires):
        save_window = QtWidgets.QWidget()
        name, _ = QtWidgets.QFileDialog.getSaveFileName(save_window, "Save Resistance Data", "",
                                                        "Text Files (*.txt);; Data Files (*.dat);; All Files (*)")
        if name:  # if a name was entered, don't save otherwise
            name = name.replace('_2wires', '')
            name = name.replace('_4wires', '')
            name_two_wires = name.replace('.txt', '_2wires.txt')
            np.savetxt(name_two_wires, two_wires, newline='\n', delimiter='\t')  # save
            print(f'Two wires data saved as {name_two_wires}')

            name_four_wires = name.replace('.txt', '_4wires.txt')
            np.savetxt(name_four_wires, four_wires, newline='\n', delimiter='\t')  # save
            print(f'Four wires data saved as {name_four_wires}')
        else:
            print('No Filename: Data not saved')

    def refresh_switching_graphs(self):
        # Simply redraw the axes after changing data.
        self.rxx_ax.relim()
        self.rxx_ax.autoscale_view()
        self.rxy_ax.relim()
        self.rxy_ax.autoscale_view()
        self.graph_fig.canvas.draw()

    def refresh_scope_graphs(self):
        self.scope_ax.relim()
        self.scope_ax.autoscale_view()
        self.scope_fig.canvas.draw()


# Starts the application running it's callback loops etc.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyGUI()
    window.resize(0, 0)
    app.exec_()
