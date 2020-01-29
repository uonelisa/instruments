import numpy as np
import time
# import tkinter as tk
# import tkinter.messagebox as mb
# from tkinter import filedialog as dialog
import matplotlib
import instruments


switchbox = instruments.SwitchBox()

pulse1_assignments = {"I+": "B", "I-": "F"}
pulse2_assignments = {"I+": "D", "I-": "H"}
measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}


switchbox.connect(4)


# switch between example configs every second. Listen for clicking.
switchbox.switch(pulse1_assignments)
time.sleep(1)
switchbox.switch(measure_assignments)
time.sleep(1)
switchbox.switch(pulse2_assignments)
time.sleep(1)
switchbox.switch(pulse2_assignments)
time.sleep(1)
switchbox.reset_all()
