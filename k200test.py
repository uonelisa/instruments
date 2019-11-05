# #
# # import numpy as np
# # import time
# # # import tkinter as tk
# # # import tkinter.messagebox as mb
# # # from tkinter import filedialog as dialog
# # # import paramiko
# # import visa
# # # import os
# # import winsound
# # # import matplotlib
# # import serial
# # # matplotlib.use('Qt5Agg')
# # # import matplotlib.pyplot as plt
#
#
#
# # class DMM:
# #     def __init__(self):
# #         self.buffer_length = 10
# #
# #     def connect(self, port):
# #         # self.k2000 = serial.Serial(f'COM{port}', 19200, 8, timeout=1)
# #         # self.k2000.open()
# #         rm = visa.ResourceManager('@vi')
# #
# #         self.k2000.write('*IDN?\n'.encode())
# #         time.sleep(0.1)
# #         print(self.k2000.read_all())
# #         self.k2000.write('*rst\n'.encode())
# #         self.k2000.write('*cls\n'.encode())
# #
# #         self.k2000.write('sens:func "volt"\n'.encode())
# #         self.k2000.write('sens:volt:nplc min\n'.encode())
# #         self.k2000.write('sens:volt:rang:auto on\n'.encode())
# #         self.k2000.write(f'trig:count {self.buffer_length}\n'.encode())
# #
# #
# #     def close(self):
# #         self.k2000.close()
# #
# #     def measure(self):
# #         self.k2000.write('trac:clear\n'.encode())
# #         self.k2000.write(f'trac:poin {self.buffer_length}\r\n'.encode())
# #         self.k2000.write('trac:feed sense\r\n'.encode())
# #         self.k2000.write('trac:feed:cont next\r\n'.encode())
# #         time.sleep(500)
# #         # try:
# #         self.k2000.write('trac:data?\r\n'.encode())
# #         output = self.k2000.read_all()
# #         print(output)
# #         data = float(str(output))
# #         print(data)
# #         return np.array(data)
# #         # except:
# #         #     print('Failed to read data from K2000')
# #         #     return np.array([])
# #
# # dmm = DMM()
# # dmm.connect(10)
# # dmm.measure()
# #
# # #\r\n
#
import visa
import time
import numpy as np
import matplotlib.pyplot as plt
# rm = visa.ResourceManager('@ni')
# port = 4
# num = 500
# k2000 = rm.open_resource(f'COM{port}', baud_rate=19200)
# k2000.close()
#
# k2000.open()
# k2000.baud_rate = 19200
# k2000.timeout = 12000
# k2000.write_termination = '\r\n'
# k2000.read_termination = '\r\n'
# print(k2000.query('*IDN?'))
#
# k2000.write('*rst') # reset
# # k2000.write('disp:enab off')
# k2000.write('*cls') #clear system
# k2000.write('sens:func "volt"') #measure volts
# k2000.write('sens:volt:nplc min') # level of averaginge min, 0.01 -> 10 ish Power line cycle: 50hz 2-> 25hz measurement
# k2000.write('sens:volt:rang:auto on') #auto-raging
# k2000.write(f'trig:count {num}') # number of points to measure
#
# k2000.write('trac:clear') # clear buffer
# k2000.write(f'trac:poin {num}') #size of buffer
# k2000.write('trac:feed sens') # what goes in buffer
# k2000.write('trac:feed:cont next') # doesn't overwrite previous data until full
# k2000.write('init')
# start = time.time()
# time.sleep(10)
# print(time.time() - start)
# print(np.array(k2000.query_ascii_values('trac:data?'))) # trigger the measurement
#
# # k2000.write('read?')
# # k2000.read() # read the data (wait long enough that it's finished ofcs
#

class DMM:
    def __init__(self):
        self.buffer_length = 500

    def connect(self, port):
        rm = visa.ResourceManager('@ni')
        self.k2000 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2000.close()

        self.k2000.open()
        self.k2000.baud_rate = 19200
        self.k2000.timeout = 12000
        self.k2000.write_termination = '\r\n'
        self.k2000.read_termination = '\r\n'
        print(self.k2000.query('*IDN?'))
        self.k2000.write('*rst')  # reset
        # k2000.write('disp:enab off')
        self.k2000.write('*cls')  # clear system
        self.k2000.write('sens:func "volt"')  # measure volts
        self.k2000.write(
            'sens:volt:nplc 0.1')  # level of averaging min, 0.01 -> 10 ish Power line cycle: 50hz 2-> 25hz measurement
        self.k2000.write('sens:volt:rang:auto on')# auto-raging



    def close(self):
        self.k2000.close()

    def measure(self, num):
        self.k2000.write(f'trig:count {num}')  # number of points to measure
        self.k2000.write('trac:clear')  # clear buffer
        self.k2000.write(f'trac:poin {num}')  # size of buffer
        self.k2000.write('trac:feed sens')  # what goes in buffer
        self.k2000.write('trac:feed:cont next')  # doesn't overwrite previous data until full
        # self.k2000.write('init')

    def trigger(self):
        self.k2000.write('init')

    def read(self):
        # self.k2000.write('form:data ASCII')  #  read doesn't work without this line ?
        data = self.k2000.query_ascii_values('trac:data?')

        data = np.array(data)

        return data
        # try:
        #     return np.array(self.k2000.query_ascii_values('trac:data?'))
        # except:
        #     print('failed to read data from k2000')
        #     return np.array([])

dmm = DMM()
dmm.connect(7)
data = np.array([])
for i in range(1,10):
    dmm.measure(100)
    dmm.trigger()
    time.sleep(2)
    data = np.append(data, dmm.read())

dmm.close()
plt.plot(data, 'r+')
plt.show()

