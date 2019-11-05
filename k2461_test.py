import visa
import numpy as np
import time
import matplotlib.pyplot as plt


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


    def pulse(self, current, width, delay):
        # self.k2400.write('sour:func "curr"')
        # self.k2400.write('sens:func "volt"')
        # self.k2400.write('sens:volt:rang:auto on')
        # self.k2400.write('sour:curr:vlim ')
        self.k2400.write('sens:volt:rsen off')

        self.k2400.write(f'sour:puls:tr:curr 0, {current}, {width}, 1, off, "defbuffer1", {delay}, 0, 5, 5')
        self.k2400.write('INIT')        # self.k2400.write(f':READ?')


    def measure(self, current, num):
        # self.k2400.write('sour:func curr')
        self.k2400.write('sour:curr:rang 200e-6')
        self.k2400.write(f'sour:curr {current}')

        # self.k2400.write('sour:curr:vlim 1')
        self.k2400.write('sens:volt:rsen on')
        self.k2400.write(f'sens:volt:nplc 2')
        self.k2400.write(f'trac:make "defBuffer1", {2*num}')
        self.k2400.write(f'trig:load "SimpleLoop", {num}, 0, "defBuffer1"')
        self.k2400.write('outp on')

    def trigger(self):
        self.k2400.write('init')

    def read(self, num):
        self.k2400.write('outp off')
        print(self.k2400.query('trac:act? "defBuffer1"'))
        try:
            data = np.array(self.k2400.query_ascii_values(f'trac:data? 1, {num}, "defBuffer1", read, rel'))
            t = data[1::2]
            d = data[0::2]
            return t, d
        except:
            return np.array([]), np.array([])

    def close(self):
        self.k2400.write('*RST')
        self.k2400.write('*SRE 0')
        self.k2400.write(':STAT:MEAS:ENAB 0')
        self.k2400.close()

pg = PulseGenerator()

pg.connect()

pg.pulse(1e-3, 1e-3, 0)
time.sleep(5)

pg.measure(100e-6, 50)
pg.trigger()
time.sleep(10)
time, data = pg.read(50)
plt.plot(time, data)
plt.show()