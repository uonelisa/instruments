import instruments

import numpy as np
import matplotlib.pyplot as plt
import time

import tkinter as tk
import tkinter.messagebox as mb
from tkinter import filedialog as dialog

num = 100
current = 0.01
frequency = 1000
pulse1_assignments = {"I+": "AG", "I-": "CE"}  # configuration for a pulse from B to F
pulse2_assignments = {"I+": "AC", "I-": "GE"}  # configuration for a pulse from D to H
measure_assignments = {"I+": "A", "I-": "E", "V1+": "A", "V1-": "E", "V2+": "C", "V2-": "G"}  # here V1 is Vxx


first_harm = instruments.SR830_RS232()
second_harm = instruments.SR830_RS232()
source = instruments.K6221()
sb = instruments.SwitchBox()

sb.connect(15)
source.connect(16)
first_harm.connect(6)
second_harm.connect(10)

source.sine_wave(frequency, current)
source.set_phase_marker()
source.wave_output_on()



first_harm.set_harmonic(1)
first_harm.set_time_constant(0.1)
first_harm.auto_phase()
first_harm.auto_range()
first_harm.set_filter(12)

second_harm.set_harmonic(1)
second_harm.set_time_constant(0.1)
second_harm.auto_phase()
second_harm.set_harmonic(2)
second_harm.auto_range()
second_harm.set_filter(12)

rxx_r = np.zeros(num)
rxx_theta = np.zeros(num)

rxy_r = np.zeros(num)
rxy_theta = np.zeros(num)

fig = plt.figure(1)
rxx_ax = plt.subplot(211)
rxy_ax = plt.subplot(212)
t = np.zeros(num)

rxx_pos_line, = rxx_ax.plot(t, rxx_r, 'k.')
rxx_ax.set_ylabel('R_xx (Ohms)')
rxx_ax.ticklabel_format(useOffset=False)

rxy_pos_line, = rxy_ax.plot(t, rxy_r, 'k.')
rxy_ax.set_ylabel('R_xy (Ohms)')
rxy_ax.set_xlabel('Time (s)')
rxy_ax.ticklabel_format(useOffset=False)
# plt.show(block=False)
plt.pause(0.001)
time.sleep(10)

start_time = time.time()
for i in range(0, num):
    t[i] = time.time() - start_time
    rxx_r[i] = first_harm.get_radius()
    rxx_theta[i] = first_harm.get_angle()
    rxy_r[i] = second_harm.get_radius()
    rxy_theta[i] = second_harm.get_angle()
    rxx_pos_line.set_data(t, rxx_r/current)
    rxy_pos_line.set_data(t, rxy_r/current)
    rxx_ax.relim()
    rxx_ax.autoscale_view()
    rxy_ax.relim()
    rxy_ax.autoscale_view()

    plt.pause(0.01)

source.wave_output_off()
source.close()
plt.show()
