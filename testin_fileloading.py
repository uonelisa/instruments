import numpy as np
import time
# import tkinter as tk
# import tkinter.messagebox as mb
# from tkinter import filedialog as dialog
# import paramiko
import os
# import winsound
# import pandas as pd
# import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
# from numba import jit
#
# data_array = np.zeros((1250,2000))
# raw = open('data', 'rb').read()
# for i in range(1250):
#     for j in range(2000):
#         data_array[i,j] = np.short(raw[2*i:2*i +1])
#         f = open("file.bin", "r")
#         a = np.fromfile(f, dtype=np.uint16)


f = open("data", "rb")
t = time.time()
a = np.mean(np.fromfile(f, dtype=np.int16).reshape(1250, 2000), 0).astype(float)
print(time.time()-t)
plt.plot(a)
plt.show()
