import instruments

import numpy as np
import matplotlib.pyplot as plt
import time

import tkinter as tk
import tkinter.messagebox as mb
from tkinter import filedialog as dialog

frequency = 1
start = -35e-3
stop = 35e-3
step = 1e-3
delay = 1
repeats = 1
channel = 1
volt_range = 100e-3

current = np.tile(np.linspace(start, stop, round((stop-start)/step)+1), repeats)
source = instruments.K6221_Ethernet()
source.connect()
source.set_compliance(60)
source.set_sense_chan_and_range(channel, volt_range)
source.configure_linear_sweep(start, stop, step, delay, repeats)
source.configure_pulse(300e-6, 1)

source.arm_pulse_sweep()
source.trigger_pulse_sweep()
time.sleep(5)
data = source.get_trace()
voltage = data[0::2]

my_scatter, = plt.plot(current, voltage, 'k.')

my_line, = plt.plot([min(current), max(current)], [min(voltage), max(voltage)], 'r-')
plt.ticklabel_format(useOffset=False)
plt.xlabel('Current (mA)')
plt.ylabel('Voltage (V)')

plt.pause(1)

save_data = np.column_stack((current, voltage))
name = dialog.asksaveasfilename(title='Save')
if name:  # if a name was entered, don't save otherwise
    if name[-4:] != '.txt':  # add .txt if not already there
        name = f'{name}.txt'
    np.savetxt(name, save_data, newline='\n', delimiter='\t')  # save
    print(f'Data saved as {name}')
else:
    print('Data not saved')

plt.show()




