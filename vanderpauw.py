"""

Created on Mon 29th Apr 09:00 2019

@author: Stuart Poole - stuart.poole@nottingham.ac.uk or stuart.f.poole@gmail.com

Developed for Python 3.7

"""

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


# from numba import jit


# import warnings
# stops false warning showing when plotting
# warnings.filterwarnings("ignore", ".*GUI is implemented.*")


def error_sound():
    winsound.Beep(880, 200)
    winsound.Beep(440, 200)


def alert_sound():
    winsound.Beep(440, 200)
    winsound.Beep(660, 200)
    winsound.Beep(880, 200)


class PulseGenerator:

    def connect(self):
        rm = visa.ResourceManager('@ni')
        # self.k2400 = serial.Serial("COM%d" % port, 38400, 8, timeout=1)
        self.k2400 = rm.open_resource('USB0::0x05E6::0x2461::04121022::INSTR')
        self.k2400.timeout = 12000
        print(self.k2400.query('*IDN?'))
        # self.k2400.write(':SYST:BEEP:STAT OFF')
        self.k2400.write(':*RST')
        self.k2400.write('sour:func curr')
        self.k2400.write('sens:func "volt"')
        self.k2400.write('sens:volt:rang:auto on')
        self.k2400.write(f'trac:make "defBuffer1", {10000}')

    def pulse(self, current, width, delay):
        # self.k2400.write('sour:func "curr"')
        # self.k2400.write('sens:func "volt"')
        # self.k2400.write('sens:volt:rang:auto on')
        # self.k2400.write('sour:curr:vlim ')
        self.k2400.write('sens:volt:rsen off')
        self.k2400.write(':FORM:ASC:PREC 16')
        # self.k2400.write(f'sour:puls:tr:curr 0, {current}, {width}, 1, off, "defbuffer1", {delay}, 0, 5, 5')
        self.k2400.write(f'SOUR:PULS:SWE:CURR:LIN 0, 0, {current}, 2, {width}, off, "defbuffer1", 0, 0, 1, 30, 30, off, off')
        self.k2400.write('INIT')        # self.k2400.write(f':READ?')
        self.k2400.write('*WAI')


    def measure(self, current, num):
        # self.k2400.write('sour:func curr')
        self.k2400.write('sour:curr:rang 200e-6')
        self.k2400.write(f'sour:curr {current}')

        # self.k2400.write('sour:curr:vlim 1')
        self.k2400.write('sens:volt:rsen on')
        self.k2400.write(f'sens:volt:nplc 2')
        self.k2400.write('sens:volt:rang:auto on')

        self.k2400.write(f'trig:load "SimpleLoop", {num}, 0, "defBuffer1"')
        self.k2400.write('outp on')

    def trigger(self):
        self.k2400.write('init')
        self.k2400.write('*wai')

    def read(self, num):
        self.k2400.write('outp off')
        print(self.k2400.query('trac:act? "defBuffer1"'))
        try:
            data = np.array(self.k2400.query_ascii_values(f'trac:data? 1, {num}, "defBuffer1", read, rel'))
            t = data[1::2]
            d = data[0::2]
            return t, d
        except:
            print('could not read data from k2400')
            return np.array([]), np.array([])

    def close(self):
        self.k2400.write('*RST')
        self.k2400.write('*SRE 0')
        self.k2400.write('outp off')
        self.k2400.close()


class SwitchBox:
    def __init__(self):
        self.start_byte = 'FE'
        self.clear_byte = '10'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'
        self.binary_dictionary = {"A": '00', "B": '01', "C": '02', "D": '03', "E": '04', "F": '05', "G": '06', "H": '07',
                                  "V1+": '20', "V1-": '10', "V2+": '08', "V2-": '04', "I+": '02', "I-": '01', "0": '00',
                                  "": '00'}

    def connect(self, port):
        self.sb = serial.Serial(f'COM{port}', 57600, 8)
        self.sb.close()
        self.sb.open()
        self.clear()

    def switch(self, assignments):

        #     this will be called with a desired arrangement and will call make_command if it seems necessary
        self.clear()
        for x, y in assignments.items():
            for char in y:
                self.sb.write(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                               self.stop_byte))
                # print(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                #                self.stop_byte))
        self.refresh()

    def close(self):
        self.clear()
        self.refresh()
        self.sb.close()

    def refresh(self):
        # sends command to turn off all channels
        self.sb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def clear(self):
        self.sb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()

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
        self.k2000.write('*rst')
        self.k2000.write('*cls')

        print(self.k2000.query('*IDN?'))
        # self.k2000.write('*rst')  # reset
        # k2000.write('disp:enab off')
         # clear system
        self.k2000.write('sens:func "volt"')  # measure volts
        self.k2000.write(
            'sens:volt:nplc 2')  # level of averaging min, 0.01 -> 10 ish Power line cycle: 50hz 2-> 25hz measurement
        self.k2000.write('sens:volt:rang 0')# auto-raging


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
        self.k2000.write('*wai')

    def read(self):
        # self.k2000.write('form:data ASCII')  #  read doesn't work without this line ?
        data = self.k2000.query_ascii_values('trac:data?')

        data = np.array(data)

        return data



sb = SwitchBox()
sb.connect(12)
pg = PulseGenerator()
pg.connect()
vert1_ass = {"I+": "B", "I-": "D", "V2+": "F", "V2-": "H"}
vert2_ass = {"I+": "F", "I-": "H", "V2+": "B", "V2-": "D"}
vert3_ass = {"I+": "D", "I-": "B", "V2+": "H", "V2-": "F"}
vert4_ass = {"I+": "H", "I-": "F", "V2+": "D", "V2-": "B"}
hor1_ass = {"I+": "B", "I-": "H", "V2+": "F", "V2-": "D"}
hor2_ass = {"I+": "F", "I-": "D", "V2+": "B", "V2-": "H"}
hor3_ass = {"I+": "H", "I-": "B", "V2+": "D", "V2-": "F"}
hor4_ass = {"I+": "D", "I-": "F", "V2+": "H", "V2-": "B"}

sb.switch(vert1_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
tvert1, Vvert1 = pg.read(10)
Rver1 = np.mean(Vvert1)/1e-3
print(f'Vert1: {Rver1}')

sb.switch(vert2_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
tvert2, Vvert2 = pg.read(10)
Rver2 = np.mean(Vvert2)/1e-3
print(f'Vert2: {Rver2}')

sb.switch(vert3_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
tvert3, Vvert3 = pg.read(10)
Rver3 = np.mean(Vvert3)/1e-3
print(f'Vert3: {Rver3}')

sb.switch(vert4_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
tvert4, Vvert4 = pg.read(10)
Rver4 = np.mean(Vvert4)/1e-3
print(f'Vert4: {Rver4}')

sb.switch(hor1_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
thor1, Vhor1 = pg.read(10)
Rhor1 = np.mean(Vhor1)/1e-3
print(f'Vhor1: {Rhor1}')


sb.switch(hor2_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
thor2, Vhor2 = pg.read(10)
Rhor2 = np.mean(Vhor2)/1e-3
print(f'Vhor2: {Rhor2}')

sb.switch(hor3_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
thor3, Vhor3 = pg.read(10)
Rhor3 = np.mean(Vhor3)/1e-3
print(f'Vhor3: {Rhor3}')

sb.switch(hor4_ass)
time.sleep(1)
pg.measure(1e-3, 10)
pg.trigger()
time.sleep(1)
thor4, Vhor4 = pg.read(10)
Rhor4 = np.mean(Vhor4)/1e-3
print(f'Vhor4: {Rhor4}')

Rvertical = (Rver1 + Rver2 + Rver3 + Rver4) / 4
Rhorizontal = (Rhor1 + Rhor2 + Rhor3 +Rhor4) / 4
print(f'Rvert: {Rvertical}, Rhor: {Rhorizontal}')


