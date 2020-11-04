import instruments

import numpy as np
import matplotlib.pyplot as plt
import time

import tkinter as tk
import tkinter.messagebox as mb
from tkinter import filedialog as dialog

voltage = 1
width = 1e-3

num_points = 100
num_loops = 2
current = 2
frequency = 1000

pulse1_assignments = {"I+": "A", "I-": "E"}  # configuration for a pulse from B to F
pulse2_assignments = {"I+": "E", "I-": "A"}  # configuration for a pulse from D to H
measure_assignments = {"I+": "A", "I-": "E", "V1+": "A", "V1-": "E", "V2+": "C", "V2-": "G"}
# measure_assignments = {"I+": "C", "I-": "G", "V1+": "C", "V1-": "G", "V2+": "E", "V2-": "A"}

top_lockin = instruments.SR830_RS232()
bot_lockin = instruments.SR830_RS232()
source = instruments.K6221()
sb = instruments.SwitchBox()
pg = instruments.K2461()

sb.connect(15)
source.connect(16)
top_lockin.connect(6)
bot_lockin.connect(10)
pg.connect()
sb.switch(measure_assignments)

source.sine_wave(frequency, current)
source.set_phase_marker()
source.wave_output_on()

time.sleep(2)

top_lockin.set_harmonic(1)
top_lockin.set_time_constant(0.1)
top_lockin.auto_phase()
# top_lockin.set_harmonic(2)
top_lockin.auto_range()
top_lockin.set_filter(12)

bot_lockin.set_harmonic(1)
bot_lockin.set_time_constant(0.1)
bot_lockin.auto_phase()
bot_lockin.set_harmonic(2)
bot_lockin.auto_range()
bot_lockin.set_filter(12)

t_pos = np.empty(num_points * num_loops)

rxx_pos_r = np.empty(num_points * num_loops)
rxx_pos_theta = np.empty(num_points * num_loops)

rxy_pos_r = np.empty(num_points * num_loops)
rxy_pos_theta = np.empty(num_points * num_loops)

t_neg = np.empty(num_points * num_loops)

rxx_neg_r = np.empty(num_points * num_loops)
rxx_neg_theta = np.empty(num_points * num_loops)

rxy_neg_r = np.empty(num_points * num_loops)
rxy_neg_theta = np.empty(num_points * num_loops)

fig = plt.figure(1)
rxx_ax = plt.subplot(211)
rxy_ax = plt.subplot(212)

rxx_pos_line, = rxx_ax.plot(t_pos, rxx_pos_r, 'k.')
rxx_neg_line, = rxx_ax.plot(t_neg, rxx_neg_r, 'k.')
rxx_ax.set_ylabel('R_xx (Ohms)')
rxx_ax.ticklabel_format(useOffset=False)

rxy_pos_line, = rxy_ax.plot(t_pos, rxy_pos_r, 'k.')
rxy_neg_line, = rxy_ax.plot(t_neg, rxy_neg_r, 'k.')
rxy_ax.set_ylabel('R_xy (Ohms)')
rxy_ax.set_xlabel('Time (s)')
rxy_ax.ticklabel_format(useOffset=False)
# plt.show(block=False)
plt.pause(0.001)
time.sleep(10)

start_time = time.time()
pg.prepare_pulsing_voltage(voltage, width)
for j in range(0, num_loops):
    source.wave_output_off()
    sb.switch(pulse1_assignments)
    time.sleep(500e-3)
    pg.send_pulse()
    time.sleep(500e-3)
    sb.switch(measure_assignments)
    time.sleep(200e-3)
    source.wave_output_on()
    for i in range(0, num_points):
        t_pos[i] = time.time() - start_time
        rxx_pos_r[i] = top_lockin.get_radius()
        rxx_pos_theta[i] = top_lockin.get_angle()
        rxy_pos_r[i] = bot_lockin.get_radius()
        rxy_pos_theta[i] = bot_lockin.get_angle()

    rxx_pos_line.set_data(t_pos, rxx_pos_r / (current * 1e-3))
    rxy_pos_line.set_data(t_pos, rxy_pos_r / (current * 1e-3))
    rxx_ax.relim()
    rxx_ax.autoscale_view()
    rxy_ax.relim()
    rxy_ax.autoscale_view()
    plt.pause(0.01)

    source.wave_output_off()
    sb.switch(pulse2_assignments)
    time.sleep(500e-3)
    pg.send_pulse()
    time.sleep(500e-3)
    sb.switch(measure_assignments)
    time.sleep(200e-3)
    source.wave_output_on()
    for i in range(0, num_points):
        t_neg[i] = time.time() - start_time
        rxx_neg_r[i] = top_lockin.get_radius()
        rxx_neg_theta[i] = top_lockin.get_angle()
        rxy_neg_r[i] = bot_lockin.get_radius()
        rxy_neg_theta[i] = bot_lockin.get_angle()

    rxx_neg_line.set_data(t_neg, rxx_neg_r / (current * 1e-3))
    rxy_neg_line.set_data(t_neg, rxy_neg_r / (current * 1e-3))
    rxx_ax.relim()
    rxx_ax.autoscale_view()
    rxy_ax.relim()
    rxy_ax.autoscale_view()
    plt.pause(0.01)

source.wave_output_off()
source.close()
sb.reset_all()

root = tk.Tk()
root.withdraw()
data = np.column_stack((t_pos, rxx_pos_r, rxx_pos_theta, rxy_pos_r, rxy_pos_theta, t_neg, rxx_neg_r, rxx_neg_theta,
                        rxy_neg_r, rxy_neg_theta))
name = dialog.asksaveasfilename(title='Save')
if name:  # if a name was entered, don't save otherwise
    if name[-4:] != '.txt':  # add .txt if not already there
        name = f'{name}.txt'
    np.savetxt(name, data, newline='\r\n', delimiter='\t')  # save
    print(f'Data saved as {name}')
else:
    print('Data not saved')

plt.show()
