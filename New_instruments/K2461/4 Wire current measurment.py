import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt

sb = instruments.SwitchBox()
sm = instruments.K2461()

sb.connect(5)
sm.connect()

probe_current = 0.1e-3
nplc = 2
vlim = 4

meas = {"I+": "G", "I-": "E", "V1+": "F", "V1-": "H"}

sb.switch(meas)
plt.pause(0.5)
sm.enable_4_wire_probe(probe_current, nplc, vlim)
time.sleep(2)

c, v = sm.read_one()
R = v / probe_current
sm.disable_probe_current()

print("Current =",probe_current*10**(3),"mA")
print("Recorded: Voltage =",v,"V","  Resistance =",R,"Ohms")

sm.BEEP(300,0.5)
plt.pause(0.5)
sm.BEEP(400,0.5)
plt.pause(0.5)
sm.BEEP(500,0.5)

sb.close()
sm.close()





















