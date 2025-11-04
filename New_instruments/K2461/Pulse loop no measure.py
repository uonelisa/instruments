import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt


sb = instruments.SwitchBox()
sm = instruments.K2461()

sb.connect(6)
sm.connect()

meas = {"I+": "H", "I-": "G", "V1+": "F", "V1-": "H"}
puls1 = {"I+": "H", "I-": "G"}
puls2 =  {"I+": "H", "I-": "G"}

# Pulse
pulse_current = 2e-3                                              
pulse_width = 0.15e-3
number_of_pulses = 6

# Probe
probe_current = 10e-6
nplc = 2
number_of_measurments = 10


# Pre set matrix and arrays
n_pulses = np.arange(number_of_pulses)
pulse_data = []
voltage_matrix = np.zeros((number_of_measurments,number_of_pulses))
time_arr_matrix = np.zeros((number_of_measurments,number_of_pulses))
time_arr_av = np.zeros((number_of_measurments,1))
time_arr_std = np.zeros((number_of_measurments,1))
print("About to start pulses")

Failed = "No"

try:
    
    sb.switch(puls1)
    
    plt.pause(5)
    
    sm.BEEP(400,0.2)
    
    for n in n_pulses:
    
        plt.pause(1)
        sm.prepare_pulsing_current(pulse_current,pulse_width)
        sm.send_pulse()
        plt.pause(200e-3)
        
        print("Pulse #",n+1)

except:
    
    print("There was an Error and had to close loop")
    
    sm.BEEP(311, 0.25)
    plt.pause(0.15)
    sm.BEEP(294, 0.25)
    plt.pause(0.15)
    sm.BEEP(262, 0.5)
    plt.pause(0.15)
    
    sb.close()
    sm.close()
    
    Failed = "Yes"


if Failed == "No":
    
    sm.BEEP(440, 0.6)
    plt.pause(0.1)
    sm.BEEP(466, 0.6)
    plt.pause(0.1)
    sm.BEEP(494, 0.6)
    plt.pause(0.1)
    sm.BEEP(523, 0.6)
    plt.pause(0.1)
    sm.BEEP(784, 1.2)
    plt.pause(0.1)

sb.close()
sm.close()

