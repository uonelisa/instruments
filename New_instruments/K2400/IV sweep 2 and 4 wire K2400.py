#IV Sweep 4 wire
import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt

# sb = instruments.SwitchBox()
sm = instruments.K2400()

# sb.connect(6)
sm.connect(4)

meas_4Wire = {"I+": "F", "I-": "H", "V1+": "E", "V1-": "G"}
meas_2Wire = {"I+": "H", "I-": "F"}

#Current perams
Imax = 1e-6
Imin = -1e-6
steps = 0.1e-6

nplc = 2
vlim = 1

Zero_Imax = np.arange(0, Imax , steps)
Imax_Zero = np.arange(Imax, 0, -steps)
Zero_Imin = np.arange(0, Imin , -steps)
Imin_Zero = np.arange(Imin, 0, steps)

Isweep = np.append(Zero_Imax,[Imax_Zero, Zero_Imin, Imin_Zero])

# array setup
Current_arr = []
Voltage_arr = []

# sb.switch(meas_4Wire)

Failed = "No"

# Figure
fig = plt.figure(figsize=(10, 6))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_ylabel("Voltage (V)")
ax.set_xlabel("Current (A)")
ax.set_title("4 wire IV Curve")
ax.grid(True)

# loop for sweep
try:
    
    for i, n in enumerate(Isweep):
        
        sm.enable_output_current()
        sm.prepare_measure_n(n,1,four_wire=False)
        sm.trigger()
        plt.pause(0.01)
        time, v, c = sm.read_one()
        plt.pause(0.001)
        sm.disable_output_current()
        
        Current_arr.append(c)
        Voltage_arr.append(v)

        ax.scatter(c,v, color="blue")
        plt.pause(0.01)
    
except:
    
    sm.close()
    
    print("Something went wrong")
    
    Failed = "Yes"
    

if Failed == "No":

    sm.close()


# collectiong and plotting data
slope, intercept = np.polyfit(Current_arr, Voltage_arr, 1)
dummy_arr = np.arange(Imin,Imax + steps,steps)
ax.plot(dummy_arr, dummy_arr*slope + intercept)

print("Resistance = ",slope,"Ohms")

# saving
name = "05_IV_I(3-11)_V(3-11)_1uA"
data = np.column_stack([Current_arr,Voltage_arr])
np.savetxt(rf"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Micro Devices Nov 2025\RC367\3um Device\20251110\{name}.txt", data)

    

























