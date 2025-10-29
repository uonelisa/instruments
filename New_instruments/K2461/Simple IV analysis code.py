import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt



filepath = r"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Pulsing Devices Oct 2025\RC364 10um\20251027\IV_I(10_4)_V(1_7)_0.01mA.txt"

data = np.loadtxt(filepath)


fig = plt.figure(figsize=(10, 6))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_ylabel("Voltage (V)")
ax.set_xlabel("Current (A)")
ax.set_title("2 wire IV Curve")
ax.grid(True)


Imax = 0.01e-3
Imin = -0.01e-3
steps = 0.01e-3*1e-2

Current_arr = data[:,0]
Voltage_arr = data[:,1]

slope, intercept = np.polyfit(Current_arr, Voltage_arr, 1)
dummy_arr = np.arange(Imin,Imax + steps,steps)

ax.scatter(Current_arr, Voltage_arr, color="black")
ax.plot(dummy_arr, dummy_arr*slope + intercept, color="red")


print("Resistance = ",slope,"Ohms")


#%% comparing graphs
import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt



filepath1 = r"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Pulsing Devices Oct 2025\RC364 10um\20251027\IV_I(1_7)_V(4_10)_0.01mA.txt"
data1 = np.loadtxt(filepath1)
filepath2 = r"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Pulsing Devices Oct 2025\RC364 10um\20251027\IV_I(7_1)_V(4_10)_0.01mA.txt"
data2 = np.loadtxt(filepath2)


fig = plt.figure(figsize=(10, 6))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
ax.set_ylabel("Voltage (V)")
ax.set_xlabel("Current (A)")
ax.set_title("2 wire IV Curve")
ax.legend()
ax.grid(True)


Imax = 0.01e-3
Imin = -0.01e-3
steps = 0.01e-3*1e-2

Current_arr1 = data1[:,0]
Voltage_arr1 = data1[:,1]
Current_arr2 = data2[:,0]
Voltage_arr2 = data2[:,1]*-1

slope1, intercept1 = np.polyfit(Current_arr1, Voltage_arr1, 1)
slope2, intercept2 = np.polyfit(Current_arr2, Voltage_arr2, 1)
dummy_arr = np.arange(Imin,Imax + steps,steps)


ax.scatter(Current_arr1, Voltage_arr1, color="gray", label="Data set 1 RAW")
ax.scatter(Current_arr2, Voltage_arr2, color="lightblue", label="Data set 2 RAW")
ax.plot(dummy_arr, dummy_arr*slope1 + intercept1, color="black", label="Data set 1 BF")
ax.plot(dummy_arr, dummy_arr*slope2 + intercept2, color="blue", label="Data set 2 BF")


print("Resistance1 = ",slope1,"Ohms")
print("Resistance2 = ",slope2,"Ohms")



















