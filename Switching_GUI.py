import time
import numpy as np
import matplotlib
import winsound
import instruments
import matplotlib.pyplot as plt
import sys
from tkinter import filedialog as dialog
import tkinter.messagebox as mb
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# Todo: replace tkinter boxes with qt

matplotlib.use('Qt5Agg')


def error_sound():
    winsound.PlaySound('C:\Windows\Media\Windows Background.wav', winsound.SND_FILENAME)


def alert_sound():
    winsound.PlaySound('C:\Windows\Media\Windows Notify System Generic.wav', winsound.SND_FILENAME)


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    # dataReady = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray)
    is_stopped = False

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
        self.data = np.array([])
        self.is_stopped = False

        try:
            sb_port = int(sb_port)
        except ValueError:
            error_sound()
            print('Invalid port please enter integer value.')
        self.sb.connect(sb_port)
        self.bb.connect(bb_port)
        self.dmm.connect(dmm_port)
        self.pg.connect()
        self.bb.enable_all()
        self.bb.set_resistances(self.resistance_assignments)

        if mode == "Pulse Current":
            data = self.pulse_current(float(pulse_mag) * 1e-3, float(pulse_width) * 1e-3, float(meas_curr) * 1e-6,
                                      int(meas_n), int(loop_n))
        elif mode == "Pulse Voltage":
            data = self.pulse_voltage(float(pulse_mag), float(pulse_width) * 1e-3, float(meas_curr) * 1e-6,
                                      int(meas_n), int(loop_n))
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
            if self.is_stopped:
                break
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

            if self.is_stopped:
                break
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
            time.sleep(200e-3)
            pulse1_time = time.time()
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
            time.sleep(200e-3)
            pulse2_time = time.time()
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


def on_start():
    # QtCore.QMetaObject.invokeMethod(obj, 'connect_instruments', Qt.QueuedConnection)
    data_collection_class.start_measurement(
        pulse_type_combobox.currentText(),
        sb_port_box.text(),
        bb_port_box.text(),
        dmm_port_box.text(),
        pulse_magnitude_box.text(),
        pulse_width_box.text(),
        probe_current_box.text(),
        measurement_count_box.text(),
        loop_count_box.text()
    )


def on_mode_changed(string):
    if string == "Pulse Current":
        pulse_magnitude_units_label.setText("mA")
        pulse_magnitude_box.setText("15")
        print("pulsing_current")
    elif string == "Pulse Voltage":
        pulse_magnitude_units_label.setText("V")
        pulse_magnitude_box.setText("5")
        print("pulsing_voltage")
    else:
        error_sound()
        print("Something went wrong with the combobox.")


def on_stop():
    data_collection_class.is_stopped = True


def on_loop_over():
    print('Loop Finished')


# Creates an application. Formality of QT
app = QtWidgets.QApplication(sys.argv)
thread = QtCore.QThread()
data_collection_class = Worker()
# data_collection_class.DataReady.connect(onDataReady())

data_collection_class.moveToThread(thread)
data_collection_class.finished.connect(on_loop_over)

thread.start()

# This large section creates the GUI and connects all the active elements to callback fucntions
window = QtWidgets.QWidget()
window.setWindowTitle("Current Pulsing")

# Create the layouts
main_layout = QtWidgets.QHBoxLayout(window)
input_grid_layout = QtWidgets.QGridLayout()
lhs_layout = QtWidgets.QVBoxLayout()
rhs_layout = QtWidgets.QVBoxLayout()
ports_layout = QtWidgets.QGridLayout()
buttons_layout = QtWidgets.QVBoxLayout()

# create the inputs group and assign it to the layout and pop it onto the lhs layout which allows the screen to be
# split evenly in half despite having two groups on RHS. This is then added to the the main layout.
input_group = QtWidgets.QGroupBox("Inputs")
pulse_type_combobox = QtWidgets.QComboBox(input_group)
pulse_type_combobox.addItem("Pulse Current")
pulse_type_combobox.addItem("Pulse Voltage")
pulse_type_combobox.currentTextChanged.connect(on_mode_changed)
pulse_magnitude_box = QtWidgets.QLineEdit('15', input_group)
pulse_magnitude_units_label = QtWidgets.QLabel('mA', input_group)
pulse_width_label = QtWidgets.QLabel('Pulse Width', input_group)
pulse_width_box = QtWidgets.QLineEdit('1', input_group)
pulse_width_units_label = QtWidgets.QLabel('ms', input_group)
probe_current_label = QtWidgets.QLabel('Probe Current', input_group)
probe_current_box = QtWidgets.QLineEdit('200', input_group)
probe_current_units_label = QtWidgets.QLabel('uA', input_group)
measurement_count_label = QtWidgets.QLabel('n per loop', input_group)
measurement_count_box = QtWidgets.QLineEdit('100', input_group)
loop_count_label = QtWidgets.QLabel('Loop Count', input_group)
loop_count_box = QtWidgets.QLineEdit('2', input_group)
input_grid_layout.addWidget(pulse_type_combobox, 0, 0)
input_grid_layout.addWidget(pulse_magnitude_box, 0, 1)
input_grid_layout.addWidget(pulse_magnitude_units_label, 0, 2)
input_grid_layout.addWidget(pulse_width_label, 1, 0)
input_grid_layout.addWidget(pulse_width_box, 1, 1)
input_grid_layout.addWidget(pulse_width_units_label, 1, 2)
input_grid_layout.addWidget(probe_current_label, 2, 0)
input_grid_layout.addWidget(probe_current_box, 2, 1)
input_grid_layout.addWidget(probe_current_units_label, 2, 2)
input_grid_layout.addWidget(measurement_count_label, 3, 0)
input_grid_layout.addWidget(measurement_count_box, 3, 1)
input_grid_layout.addWidget(loop_count_label, 4, 0)
input_grid_layout.addWidget(loop_count_box, 4, 1)
input_group.setLayout(input_grid_layout)
lhs_layout.addWidget(input_group)
main_layout.addLayout(lhs_layout)

# Create ports group and populate the associated layout and add this to the ports layout grid
ports_group = QtWidgets.QGroupBox("Ports")
sb_port_label = QtWidgets.QLabel('Switch Box Port', ports_group)
sb_port_box = QtWidgets.QLineEdit('3', ports_group)
bb_port_label = QtWidgets.QLabel('Balance Box Port', ports_group)
bb_port_box = QtWidgets.QLineEdit('4', ports_group)
dmm_port_label = QtWidgets.QLabel('Keithley 2000 Port', ports_group)
dmm_port_box = QtWidgets.QLineEdit('5', ports_group)
ports_layout.addWidget(sb_port_label, 0, 0)
ports_layout.addWidget(sb_port_box, 0, 1)
ports_layout.addWidget(bb_port_label, 1, 0)
ports_layout.addWidget(bb_port_box, 1, 1)
ports_layout.addWidget(dmm_port_label, 2, 0)
ports_layout.addWidget(dmm_port_box, 2, 1)
ports_group.setLayout(ports_layout)

# Create buttons group and add to vstack
buttons_group = QtWidgets.QGroupBox("")
start_button = QtWidgets.QPushButton('Start', buttons_group)
start_button.clicked.connect(on_start)
stop_button = QtWidgets.QPushButton('Stop', buttons_group)
stop_button.clicked.connect(on_stop)
buttons_layout.addWidget(start_button, 0)
buttons_layout.addWidget(stop_button, 1)
buttons_group.setLayout(buttons_layout)

# construct the vstack of port group then buttons group on RHS and add to main layout (which is a vertical split)
rhs_layout.addWidget(ports_group, 0)
rhs_layout.addWidget(buttons_group, 1)
main_layout.addLayout(rhs_layout)

# set the window as small as it can be. looks best.
window.resize(0, 0)
window.show()
# Starts the application running it's callback loops etc.
if __name__ == '__main__':
    app.exec_()
