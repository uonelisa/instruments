import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt


sb = instruments.SwitchBox()
sm = instruments.K2461()

sb.connect(5)
sm.connect()

meas = {"I+": "E", "I-": "G", "V1+": "F", "V1-": "H"}
puls1 = {"I+": "E", "I-": "G"}
puls2 =  {"I+": "G", "I-": "G"}

# Pulse                                         
pulse_width = 1e-3
number_of_pulses = 40 # use even number
number_of_sweeps = 3

pulse_min, pulse_max = -10e-3, 10e-3

pulse_0toMax = np.linspace(0, pulse_max, int(0.5*number_of_pulses))
pulse_MaxtoMin = np.linspace(pulse_max, pulse_min, number_of_pulses)
pulse_Minto0 = np.linspace(pulse_min, 0, int(0.5*number_of_pulses))

pulse_arr = np.concatenate((pulse_0toMax, pulse_MaxtoMin, pulse_Minto0))

pulse_arr_n = np.tile(pulse_arr, number_of_sweeps)

# Probe
probe_current = 200e-6
nplc = 2
number_of_measurments = 1
vlim = 2

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
        plt.pause(1)
        # sm.prepare_measure_one(probe_current, nplc)
        sm.enable_4_wire_probe(probe_current, nplc, vlim)
        print("enabaling probe")
        plt.pause(1)
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
    
    sb.close()
    sm.close()
    

pulse_data = pulse_arr
probe_data = probe_current*np.ones(number_of_pulses)

voltage_arr = np.array(voltage_arr,dtype="float64")
current_arr = np.array(current_arr,dtype="float64")

resistance_arr = voltage_arr/current_arr

current_resistance_data = np.column_stack((current_arr, resistance_arr))

plt.plot(pulse_arr_n, resistance_arr)


# time_arr_0 = pulse_data[0][0]


# for n in n_pulses:
    
#     time_n = pulse_data[n][0]
#     time_arr_matrix[:,n] = time_n
    
#     v = pulse_data[n][1]
#     voltage_matrix[:, n] = v 

# for n in np.arange(number_of_measurments):
    
#     t_n = time_arr_matrix[n,:]
#     t_std = np.std(t_n)
#     t_av = np.average(t_n)
    
#     time_arr_av[n,:] = t_av
#     time_arr_std[n,:] = t_std
    
    
# final_data = np.column_stack((time_arr_av, time_arr_std, voltage_matrix))

# final_data_single_measurment = np.zeros((number_of_pulses, 2))
 

# print(final_data.shape)
# print(final_data[:10])  # preview first 5 rows

# np.savetxt("pulse_data.csv", final_data, delimiter=",", header="Time," + ",".join([f"Pulse{i+1}" for i in range(number_of_pulses)]), comments="")








sb.close()
sm.close()
