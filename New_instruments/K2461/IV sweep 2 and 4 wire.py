#IV Sweep 4 wire
import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt

sb = instruments.SwitchBox()
sm = instruments.K2461()

sb.connect(5)
sm.connect()

meas_4Wire = {"I+": "H", "I-": "G", "V1+": "E", "V1-": "F"}
meas_2Wire = {"I+": "H", "I-": "F"}

#Current perams
Imax = 0.01e-3
Imin = -0.01e-3
steps = 0.01e-3*2e-2

nplc = 2
vlim = 1

Zero_Imax = np.arange(0, Imax , steps)
Imax_Zero = np.arange(Imax, 0, -steps)
Zero_Imin = np.arange(0, Imin , -steps)
Imin_Zero = np.arange(Imin, 0, steps)

Isweep = np.append(Zero_Imax,[Imax_Zero, Zero_Imin, Imin_Zero])

Current_arr = []
Voltage_arr = []

sb.switch(meas_4Wire)

Failed = "No"

# Figure
fig = plt.figure(figsize=(10, 6))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_ylabel("Voltage (V)")
ax.set_xlabel("Current (A)")
ax.set_title("4 wire IV Curve")
ax.grid(True)

try:
    
    for i, n in enumerate(Isweep):
    
        sm.enable_4_wire_probe(n, nplc, vlim)
        plt.pause(0.001)
        c, v = sm.read_one()
        plt.pause(0.001)
        
        Current_arr.append(c)
        Voltage_arr.append(v)
        
        # ax.scatter(Voltage_arr, Current_arr)
        ax.scatter(c,v, color="blue")
        # print(v,c)
        # ax.show()
        plt.pause(0.01)
        # ax.close()

except:
    
    sb.close()
    sm.close()
    
    print("Something went wrong")
    
    sm.BEEP(311, 0.25)
    plt.pause(0.15)
    sm.BEEP(294, 0.25)
    plt.pause(0.15)
    sm.BEEP(262, 0.5)
    plt.pause(0.15)
    
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

slope, intercept = np.polyfit(Current_arr, Voltage_arr, 1)
dummy_arr = np.arange(Imin,Imax + steps,steps)
ax.plot(dummy_arr, dummy_arr*slope + intercept)

print("Resistance = ",slope,"Ohms")

# name = "IV_I(4_1)_V(7_10)_0.01mA"
# data = np.column_stack([Current_arr,Voltage_arr])
# np.savetxt(rf"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Pulsing Devices Oct 2025\RC364 10um\20251028\{name}.txt", data)
    
    
#%% 2 Wire
import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt

sb = instruments.SwitchBox()
sm = instruments.K2461()

sb.connect(5)
sm.connect()

meas_4Wire = {"I+": "F", "I-": "H", "V1+": "E", "V1-": "G"}
meas_2Wire = {"I+": "E", "I-": "G"}

#Current perams
Imax = 0.01e-3
Imin = -0.01e-3
steps = 0.01e-3*2e-2

nplc = 2
vlim = 1

Zero_Imax = np.arange(0, Imax , steps)
Imax_Zero = np.arange(Imax, 0, -steps)
Zero_Imin = np.arange(0, Imin , -steps)
Imin_Zero = np.arange(Imin, 0, steps)

Isweep = np.append(Zero_Imax,[Imax_Zero, Zero_Imin, Imin_Zero])

Current_arr = []
Voltage_arr = []

sb.switch(meas_2Wire)

Failed = "No"

# Figure
fig = plt.figure(figsize=(10, 6))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_ylabel("Voltage (V)")
ax.set_xlabel("Current (A)")
ax.set_title("2 wire IV Curve")
ax.grid(True)

try:
    
    for i, n in enumerate(Isweep):
    
        sm.enable_2_wire_probe(n, nplc, vlim)
        plt.pause(0.001)
        c, v = sm.read_one()
        plt.pause(0.001)
        
        Current_arr.append(c)
        Voltage_arr.append(v)
        
        # ax.scatter(Voltage_arr, Current_arr)
        ax.scatter(c,v, color="blue")
        # print(v,c)
        # ax.show()
        plt.pause(0.01)
        # ax.close()

except:
    
    sb.close()
    sm.close()
    
    print("Something went wrong")
    
    sm.BEEP(311, 0.25)
    plt.pause(0.15)
    sm.BEEP(294, 0.25)
    plt.pause(0.15)
    sm.BEEP(262, 0.5)
    plt.pause(0.15)
    
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

slope, intercept = np.polyfit(Current_arr, Voltage_arr, 1)
dummy_arr = np.arange(Imin,Imax + steps,steps)
ax.plot(dummy_arr, dummy_arr*slope + intercept)

print("Resistance = ",slope,"Ohms")

name = "IV_I(4_10)_0.01mA"
data = np.column_stack([Current_arr,Voltage_arr])
np.savetxt(rf"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Pulsing Devices Oct 2025\RC364 10um\20251027\{name}.txt", data)




































