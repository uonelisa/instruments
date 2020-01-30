import time
import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# Creates an application. Formality of QT
app = QtWidgets.QApplication(sys.argv)
# make a thread for the serial stuff to occur in
thread = QtCore.QThread()
# create a Qthread worker class which contains all possible methods
# obj = Worker()
# Connect the data ready signal to the data onDataReady plotting function
# obj.dataReady.connect(onDataReady)
# Move the worker class onto it's own thread
# obj.moveToThread(thread)
# Connect the finished signal to a quit function to end the thread. (not used in this example)
# obj.finished.connect(thread.quit)

# starts the worker thread.
thread.start()

# Draws a window, displays it, adds 2 buttons with callbacks and then resizes the window.
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
pulse_current_label = QtWidgets.QLabel('Pulse Current', input_group)
pulse_current_box = QtWidgets.QLineEdit('15', input_group)
pulse_current_units_label = QtWidgets.QLabel('mA', input_group)
pulse_width_label = QtWidgets.QLabel('Pulse Width', input_group)
pulse_width_box = QtWidgets.QLineEdit('1', input_group)
pulse_width_units_label = QtWidgets.QLabel('ms', input_group)
probe_current_label = QtWidgets.QLabel('Probe Current', input_group)
probe_current_box = QtWidgets.QLineEdit('100', input_group)
probe_current_units_label = QtWidgets.QLabel('uA', input_group)
loop_count_label = QtWidgets.QLabel('Loop Count', input_group)
loop_count_box = QtWidgets.QLineEdit('5', input_group)
measurement_count_label = QtWidgets.QLabel('n per loop', input_group)
measurement_count_box = QtWidgets.QLineEdit('100', input_group)
input_grid_layout.addWidget(pulse_current_label, 0, 0)
input_grid_layout.addWidget(pulse_current_box, 0, 1)
input_grid_layout.addWidget(pulse_current_units_label, 0, 2)
input_grid_layout.addWidget(pulse_width_label, 1, 0)
input_grid_layout.addWidget(pulse_width_box, 1, 1)
input_grid_layout.addWidget(pulse_width_units_label, 1, 2)
input_grid_layout.addWidget(probe_current_label, 2, 0)
input_grid_layout.addWidget(probe_current_box, 2, 1)
input_grid_layout.addWidget(probe_current_units_label, 2, 2)
input_grid_layout.addWidget(loop_count_label, 3, 0)
input_grid_layout.addWidget(loop_count_box, 3, 1)
input_grid_layout.addWidget(measurement_count_label, 4, 0)
input_grid_layout.addWidget(measurement_count_box, 4, 1)
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
stop_button = QtWidgets.QPushButton('Stop', buttons_group)
buttons_layout.addWidget(start_button, 0)
buttons_layout.addWidget(stop_button, 1)
buttons_group.setLayout(buttons_layout)

# construct the vstack of port group then buttons group on RHS and add to main layout (which is a vertical split)
rhs_layout.addWidget(ports_group, 0)
rhs_layout.addWidget(buttons_group, 1)
main_layout.addLayout(rhs_layout)

# set the window as small as it can be. looks best.
window.resize(365, 205)
window.show()
# Starts the application running it's callback loops etc.
app.exec_()
