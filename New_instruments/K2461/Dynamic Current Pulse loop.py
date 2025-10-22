import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt


sb = instruments.SwitchBox()
sm = instruments.K2461()

sb.connect(5)
sm.connect()

meas = {"I+": "H", "I-": "G", "V1+": "F", "V1-": "E"}
puls1 = {"I+": "H", "I-": "G"}
puls2 =  {"I+": "G", "I-": "G"}

# Pulse                                         
pulse_width = 1e-3
number_of_pulses = 16 # use even number
number_of_sweeps = 3

pulse_min, pulse_max = -0.1e-3, 0.1e-3

pulse_0toMax = np.linspace(0, pulse_max, int(0.5*number_of_pulses))
pulse_MaxtoMin = np.linspace(pulse_max, pulse_min, number_of_pulses)
pulse_Minto0 = np.linspace(pulse_min, 0, int(0.5*number_of_pulses))

pulse_arr = np.concatenate((pulse_0toMax, pulse_MaxtoMin, pulse_Minto0))

pulse_arr_n = np.tile(pulse_arr, number_of_sweeps)

# Probe
probe_current = 20e-6
nplc = 2
number_of_measurments = 1
vlim = 4

# Pre set matrix and arrays
n_pulses = np.arange(number_of_pulses)
pulse_data = []
# voltage_matrix = np.zeros((number_of_measurments,number_of_pulses))
voltage_arr = []
current_arr = []

time_arr_matrix = np.zeros((number_of_measurments,number_of_pulses))
time_arr_av = np.zeros((number_of_measurments,1))
time_arr_std = np.zeros((number_of_measurments,1))
final_data_single_measurment = np.zeros((number_of_pulses, 2))
print("About to start pulses")

Cur_arr = np.zeros(2) # this is going to save current and previous value

Failed = "No"

# Loop that goes though every current value in array pulse_arr_n and pulses it
try:

    for n, Cur in enumerate(pulse_arr_n):
        
        Cur_arr[0] = Cur
        
        
        sb.switch(puls1)
        plt.pause(1)
        sm.prepare_pulsing_current(Cur, pulse_width)
        print("prepare pulse",n+1)
        sm.send_pulse()
        print("send pulse",n+1) 
        plt.pause(200e-3)
        sb.switch(meas)
        plt.pause(0.75)
        # sm.prepare_measure_one(probe_current, nplc)
        sm.enable_4_wire_probe(probe_current, nplc, vlim)
        print("enabaling probe")
        plt.pause(0.75)
        c, v = sm.read_one()
        print("Read")
        sm.disable_probe_current()
        print("disable probe")
        P = np.array([c, v])
        pulse_data.append(P)
        
        voltage_arr.append(v)
        current_arr.append(c)
        
        r = v/c
        
        if Cur_arr[0] >= Cur_arr[1]:
            plt.scatter(Cur,v/c,color="orange")
            
        else:
            plt.scatter(Cur,v/c,color="purple")
            
        
        print("Pulse #", n+1, "Pulse Current =", Cur, "Amps")
        print("Probed voltage =",v," Probed current =",c," Resistance =",r)
        
        Cur_arr[1] = Cur
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


# Added sound effects
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



pulse_data = pulse_arr
probe_data = probe_current*np.ones(number_of_pulses)

voltage_arr = np.array(voltage_arr,dtype="float64")
current_arr = np.array(current_arr,dtype="float64")

resistance_arr = voltage_arr/current_arr

current_resistance_data = np.column_stack((current_arr, resistance_arr))

plt.plot(pulse_arr_n, resistance_arr)

np.savetxt(r"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Test.txt", current_resistance_data)








sb.close()
sm.close()

