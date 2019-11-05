import numpy as np
import time
import tkinter as tk
import tkinter.messagebox as mb
from tkinter import filedialog as dialog
import paramiko
import visa
import os
import winsound
import matplotlib
import serial
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


class K2401:

    def __init__(self):
        self.constant_a = 'constant_a'

    def connect(self, port):
        rm = visa.ResourceManager('@ni')
        self.k2401 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2401.close()
        self.k2401.open()
        self.k2401.baud_rate = 9600
        self.k2401.timeout = 10000
        self.k2401.write_termination = '\r\n'
        self.k2401.read_termination = '\r\n'
        self.k2401.write('*rst')
        self.k2401.write('*cls')


    def pulse(self, current):

        self.k2401.write('*rst')
        self.k2401.write('trac:cle')
        self.k2401.write('*cls')
        self.k2401.write(':syst:rsen on')
        self.k2401.write('trig:coun 1')
        self.k2401.write('sour:func curr')
        self.k2401.write('sens:func:conc off')
        self.k2401.write('sens:volt:rang:auto on')
        self.k2401.write('sens:volt:nplc 0.08')  # approx 5m
        self.k2401.write('sens:volt:prot:lev 20')
        self.k2401.write(f'sour:curr:lev {current}')
        self.k2401.write('trig:del 0')
        self.k2401.write('sour:del 0')
        self.k2401.write('sour:cle:auto on')

    def measure(self, current, num):
        self.k2401.write('*rst')
        self.k2401.write('*cls')
        # self.k2401.write(':syst:rsen on')
        # self.k2401.write('sour:curr:rang 200e-6')
        self.k2401.write('sour:func curr')
        self.k2401.write(f'sour:curr {current}')
        self.k2401.write('sour:curr:rang:auto on')

        self.k2401.write('sens:volt:prot:lev 20')
        self.k2401.write('sens:func "volt"')
        self.k2401.write('sens:volt:dc:nplc 2')
        self.k2401.write('sens:volt:rang:auto on')
        self.k2401.write('syst:rsen on')
        self.k2401.write('form:elem time, volt, curr')

        self.k2401.write('trac:cle')  # clear buffer
        self.k2401.write(f'trig:count {num}')  # number of p
        self.k2401.write(f'trac:poin {num}')  # size of buff
        self.k2401.write('trac:feed sens')  # what goes in b
        self.k2401.write('trac:feed:cont next')  # doesn't o
        self.k2401.write('trac:tst:form abs')

        self.k2401.write('outp on')

    def trigger(self):
        self.k2401.write('init')
        self.k2401.write('*wai')

    def read(self):
        # self.k2000.write('form:data ASCII')  #  read doesn
        self.k2401.write('outp off')

        data = self.k2401.query_ascii_values('trac:data?')
        data = np.array(data)

        return data

    def close(self):
        self.k2401.write('outp off')
        self.k2401.close()


number = 100

pg = K2401()
pg.connect(16)
pg.pulse(15e-3)
pg.trigger()
time.sleep(0.01)
pg.measure(0.5e-3, number)
pg.trigger()
time.sleep(20)
data = pg.read()
print(data)

plt.plot(data[2::3], data[0::3]/data[1::3], 'k+')
plt.show()