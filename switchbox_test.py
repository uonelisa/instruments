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
kiethley = instruments.K2000()

pulse1_assignments = {"I+": "B", "I-": "F"}
pulse2_assignments = {"I+": "D", "I-": "H"}
measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}
pulse_current = 15e-3
pulse_width = 1e-3
measure_current = 100e-6
measure_number = 100
measure_delay = measure_number * 0.18

# pos_rxx = np.array([])
# pos_rxy = np.array([])
# pos_time = np.array([])
#
# neg_rxx = np.array([])
# neg_rxy = np.array([])
# neg_time = np.array([])


start_time = time.time()
switchbox.connect(5)

while True:
    # pulse in one direction
    switchbox.switch(pulse1_assignments)
    plt.pause(0.1)
    switchbox.switch(measure_assignments)
    plt.pause(0.1)
    switchbox.switch(pulse2_assignments)
    plt.pause(0.1)
    switchbox.switch(pulse2_assignments)
    plt.pause(0.1)