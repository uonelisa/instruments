import visa
import numpy as np

__all__ = ['K2401', 'K2000', 'PulseGenerator']


class K2401:

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
        self.k2401.write('INIT')        # self.k2400.write(f':READ?')
        self.k2401.write('*WAI')

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

        data = np.array(self.k2401.query_ascii_values('trac:data?'))
        return data[2::3], data[0::3], data[1::3]

    def close(self):
        self.k2401.write('outp off')
        self.k2401.close()


class K2000:
    def __init__(self):
        self.buffer_length = 500

    def connect(self, port, range):
        rm = visa.ResourceManager('@ni')
        self.k2000 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2000.close()

        self.k2000.open()
        self.k2000.baud_rate = 19200
        self.k2000.timeout = 5000
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
        self.k2000.write(f'sens:volt:rang {range}')# auto-raging


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
        self.k2400.write(
            f'SOUR:PULS:SWE:CURR:LIN 0, 0, {current}, 2, {width}, off, "defbuffer1", 0, 0, 1, 30, 30, off, off')
        self.k2400.write('INIT')  # self.k2400.write(f':READ?')
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
        # print(self.k2400.query('trac:act? "defBuffer1"'))
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
