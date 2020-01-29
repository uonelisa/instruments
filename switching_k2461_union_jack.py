import numpy as np
import time
import matplotlib
import instruments
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


pulse1_assignments = {"I+": "B", "I-": "F"}  # configuration for a pulse from B to F
pulse2_assignments = {"I+": "D", "I-": "H"}  # configuration for a pulse from D to H
measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}  # here V1 is Vxy
pulse_current = 25e-3  # set current
pulse_width = 1e-3  # set pulse duration
measure_current = 1e-3  # measurement current
measure_number = 100  # number of measurements to store in buffer when calling measure_n and read_buffer
measure_delay = measure_number * 0.18  # Not strictly necessary.

switchbox = instruments.SwitchBox()  # make a sb object
pulsegenerator = instruments.K2461()  # make a k2461 object
kiethley = instruments.K2000()  # make a k2000 object
start_time = time.time()  # use this for the graphing only

# actually connect to the instruments
switchbox.connect(5)
pulsegenerator.connect()
kiethley.connect(3, 0)

# pulse in one direction
switchbox.switch(pulse1_assignments)
plt.pause(100e-3)  # pauses to allow changes to apply before telling them to do something else.
pulse1_time = time.time()
pulsegenerator.pulse(pulse_current, pulse_width)  # sends a pulse with given params
# print('Pulse current: ', pulse_current)  # just to show the set value.
plt.pause(100e-3)
switchbox.switch(measure_assignments)  # tells the switchbox to switch to a measurement assignment
pulsegenerator.measure_n(measure_current, measure_number)  # tells the k2461 to prepare a vxx measurement
kiethley.measure_n(measure_number)  # tells the k2000 to prepare a vxy measurement
plt.pause(100e-3)
kiethley.trigger()  # actually starts measuring
pulsegenerator.trigger()  # actually starts the measuring
# the instruments will wait for their "timeout" duration anyway but for large N manually waiting is necesasry
plt.pause(measure_delay)

# reads the values
pos_time, pos_rxx = pulsegenerator.read_buffer(measure_number)
pos_rxy = kiethley.read_buffer()

# repeat of above in reverse
switchbox.switch(pulse2_assignments)
plt.pause(100e-3)
pulse2_time = time.time()
pulsegenerator.pulse(pulse_current, pulse_width)
plt.pause(100e-3)
print('Pulse current: ', pulse_current)
switchbox.switch(measure_assignments)
pulsegenerator.measure_n(measure_current, measure_number)
kiethley.measure_n(measure_number)
plt.pause(100e-3)
kiethley.trigger()
pulsegenerator.trigger()
plt.pause(measure_delay)
neg_time, neg_rxx = pulsegenerator.read_buffer(measure_number)
neg_rxy = kiethley.read_buffer()
neg_time = neg_time


# plotting
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