import numpy as np
import time
# import tkinter as tk
# import tkinter.messagebox as mb
# from tkinter import filedialog as dialog
import matplotlib
import instruments

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

switchbox = instruments.SwitchBox()
pulsegenerator = instruments.K2461()
keithley = instruments.K2000()

pulse1_assignments = {"I+": "B", "I-": "F"}
pulse2_assignments = {"I+": "D", "I-": "H"}
measure_assignments = {"V1+": "A", "V1-": "E", "V2+": "H", "V2-": "B", "I+": "G", "I-": "C"}
pulse_current = 25e-3
pulse_width = 1e-3
measure_current = 1e-4
measure_number = 100
measure_delay = measure_number * 0.18

start_time = time.time()
switchbox.connect(5)
pulsegenerator.connect()
keithley.connect(3)

# pulse in one direction
switchbox.switch(pulse1_assignments)
plt.pause(200e-3)
pulse1_time = time.time()
pulsegenerator.pulse_current(pulse_current, pulse_width)
print('Pulse current: ', pulse_current)
plt.pause(200e-3)
switchbox.switch(measure_assignments)
pulsegenerator.measure_n(measure_current, measure_number, 2)
keithley.measure_n(measure_number, 0, 2)
plt.pause(200e-3)
keithley.trigger()
pulsegenerator.trigger()
plt.pause(measure_delay)
pos_time, pos_rxx = pulsegenerator.read_buffer(measure_number)
pos_rxy = keithley.read_buffer()

# pulse in other direction
switchbox.switch(pulse2_assignments)
plt.pause(200e-3)
pulse2_time = time.time()
pulsegenerator.pulse_current(pulse_current, pulse_width)
plt.pause(200e-3)
print('Pulse current: ', pulse_current)
switchbox.switch(measure_assignments)
pulsegenerator.measure_n(measure_current, measure_number, 2)
keithley.measure_n(measure_number, 0, 2)
plt.pause(200e-3)
keithley.trigger()
pulsegenerator.trigger()
plt.pause(measure_delay)
neg_time, neg_rxx = pulsegenerator.read_buffer(measure_number)
neg_rxy = keithley.read_buffer()
neg_time = neg_time

plt.figure()
plt.plot(pos_time + pulse1_time - start_time, pos_rxx/measure_current)
plt.plot(neg_time + pulse2_time - start_time, neg_rxx/measure_current)
plt.xlabel('Time (s)')
plt.ylabel('R_xx (Ohms)')
plt.figure()
plt.plot(pos_time + pulse1_time - start_time, pos_rxy/measure_current)
plt.plot(neg_time + pulse2_time - start_time, neg_rxy/measure_current)
plt.xlabel('Time (s)')
plt.ylabel('R_xy (Ohms)')
plt.show()