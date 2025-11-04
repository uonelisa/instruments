import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt


sb = instruments.SwitchBox()
sm = instruments.K2461()



n_loops = 10

# Pulse peramiters                                        
pulse_width = 1e-3
number_of_pulses = 10 # use even number

pulse_min, pulse_max = -6e-3, 6e-3


# making array
pulse_0toMax = np.arange(0, pulse_max, pulse_max*2e-2)
pulse_MaxtoMin = np.arange(pulse_max, pulse_min, -pulse_max*2e-2)
pulse_Minto0 = np.arange(pulse_min, 0 + pulse_max*1e-1, pulse_max*2e-2)
pulse_arr = np.concatenate((pulse_0toMax, pulse_MaxtoMin, pulse_Minto0))

# probe peramiters
probe_current = 100e-6
nplc = 2
vlim = 4


meas = {"I+": "E", "I-": "G", "V1+": "H", "V1-": "F"}
puls1 = {"I+": "E", "I-": "G"}



def Current_Pulse_Sweep(pulse_width, probe_current, nplc, vlim, meas, puls1, pulse_arr):
    
    sb.connect(6)
    sm.connect()
    
    # Pre set matrix and arrays
    pulse_data = []
    voltage_arr = []
    current_arr = []
    
    print("About to start pulses")
    
    Cur_arr = np.zeros(2) # this is going to save current and previous value
    
    Failed = "No"
    
    # Loop that goes though every current value in array pulse_arr_n and pulses it
    try:
    
        for n, Cur in enumerate(pulse_arr):
            
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
            
            plt.pause(0.001)
            
            if Cur_arr[0] >= Cur_arr[1]:
                ax.scatter(Cur,v/c,color="orange")
                
            else:
                ax.scatter(Cur,v/c,color="purple")
                
            
            print("Pulse #", n+1, "Pulse Current =", Cur, "Amps")
            print("Probed voltage =",v," Probed current =",c," Resistance =",r)
            
            Cur_arr[1] = Cur
    except:
        # If failed
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
    
    ax.plot(pulse_arr_n, resistance_arr)
    
    # np.savetxt(r"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Test.txt", current_resistance_data)
    
    sb.close()
    sm.close()
    
    ax.clear()
    
    return resistance_arr, pulse_arr_n

plt.ion()
fig = plt.figure(figsize=(10, 6))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_ylabel("Resistance (Ohms)")
ax.set_xlabel("Current Pulse (A)")
ax.set_title("Pulse Sweep")
ax.grid(True)


n_loops = 10

n_loops_arr = np.arange(n_loops)

R_arr_2D = np.zeros(205)

for n in range(n_loops):
    
    print("Sweep",n)
    R_arr, pulse_arr_n = Current_Pulse_Sweep(pulse_width, probe_current, nplc, vlim, meas, puls1, pulse_arr)
    
    R_arr_2D = np.column_stack((R_arr_2D, R_arr))
    

R_arr_2D_no_zero = np.delete(R_arr_2D,0,1)

R_arr_sum = np.sum(R_arr_2D_no_zero, axis=1)

R_arr_av = R_arr_sum/n_loops


plt.ioff()
fig2 = plt.figure(figsize=(10, 6))
ax2 = fig2.add_axes([0.1, 0.1, 0.8, 0.8])
ax2.set_ylabel("Resistance (Ohms)")
ax2.set_xlabel("Current Pulse (A)")
ax2.set_title("Pulse Sweep")
ax2.grid(True)

ax2.plot(pulse_arr_n, R_arr_av)

name = "05_Psweep_I(4_10)_V(1_7)_6mA(4_10)_xy"
data = np.column_stack([pulse_arr_n, R_arr_av, R_arr_2D_no_zero])
np.savetxt(rf"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Pulsing Devices Oct 2025\RC364 10um\20251103\{name}.txt", data)
    






    
    
    
    