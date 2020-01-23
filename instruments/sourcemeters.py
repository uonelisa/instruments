import visa
import numpy as np

__all__ = ['K2401', 'K2461']


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


class K2461:

    # connects to the k2461.
    def connect(self):
        rm = visa.ResourceManager('@ni')

        self.k2461 = rm.open_resource('USB0::0x05E6::0x2461::04121022::INSTR')
        self.k2461.timeout = 12000
        print(self.k2461.query('*IDN?'))
        # self.k2400.write(':SYST:BEEP:STAT OFF')
        self.k2461.write(':*RST')
        self.k2461.write('sour:func curr')
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write(f'trac:make "defBuffer1", {10000}')

    # sends a pulse with given current and time length
    def pulse(self, current, width):
        # self.k2400.write('sour:func "curr"')
        # self.k2400.write('sens:func "volt"')
        # self.k2400.write('sens:volt:rang:auto on')
        # self.k2400.write('sour:curr:vlim ')
        self.k2461.write('sens:volt:rsen off')
        self.k2461.write(':FORM:ASC:PREC 16')
        # self.k2400.write(f'sour:puls:tr:curr 0, {current}, {width}, 1, off, "defbuffer1", {delay}, 0, 5, 5')
        self.k2461.write(
            f'SOUR:PULS:SWE:CURR:LIN 0, 0, {current}, 2, {width}, off, "defbuffer1", 0, 0, 1, 30, 30, off, off')
        self.k2461.write('INIT')  # self.k2400.write(f':READ?')
        self.k2461.write('*WAI')

    # sets up a measurement of "num" points with applied probe current of "current" Amps
    def measure_n(self, current, num):
        # self.k2400.write('sour:func curr')
        self.k2461.write('sour:curr:rang 200e-6')
        self.k2461.write(f'sour:curr {current}')

        # self.k2400.write('sour:curr:vlim 1')
        self.k2461.write('sens:volt:rsen on')
        self.k2461.write(f'sens:volt:nplc 2')
        self.k2461.write('sens:volt:rang:auto on')

        self.k2461.write(f'trig:load "SimpleLoop", {num}, 0, "defBuffer1"')
        self.k2461.write('outp on')

    # For use when reading one value from the source meter in 4 wire mode.
    # Applies current and measures voltage drop across device (Rxx)
    def enable_4_wire_probe(self, current, nplc):
        self.k2461.write('sour:func curr')
        self.k2461.write(f'sour:curr {current}')
        self.k2461.write('sour:curr:vlim 2')
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write('sens:volt:rsen on')
        self.k2461.write(f'sens:volt:nplc {nplc}')
        self.k2461.write('outp on')

    # For use when reading one value from Source meter at a time in 2 wire mode.
    # Applies current and measures voltage required to apply that current
    # nplc: 0.02, 0.2, 1, 10, 100, 200. 0.2 is "fast".
    def enable_2_wire_probe(self, current, nplc):
        self.k2461.write('sour:func curr')
        self.k2461.write(f'sour:curr {current}')
        self.k2461.write('sour:curr:vlim 2')
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write('sens:volt:rsen off')
        self.k2461.write(f'sens:volt:nplc {nplc}')
        self.k2461.write('outp on')


    def disable_probe_current(self):
        self.k2461.write('outp off')

    # initiates the measurement set up using measure
    def trigger(self):
        self.k2461.write('init')
        self.k2461.write('*wai')

    # reads num data points from the buffer
    def read_buffer(self, num):
        self.k2461.write('outp off')
        # print(self.k2400.query('trac:act? "defBuffer1"'))
        try:
            data = np.array(self.k2461.query_ascii_values(f'trac:data? 1, {num}, "defBuffer1", read, rel'))
            t = data[1::2]
            d = data[0::2]
            return t, d
        except:
            print('could not read data from K2461')
            return np.array([]), np.array([])

    def read_one(self):
        data = np.array([self.k2461.query_ascii_values(':READ? "defbuffer1", sour, read')])
        print(data)
        cur = data[0][0]
        vol = data[0][1]
        return cur, vol

    # closes conections and allows for a new process to connect
    def close(self):
        self.k2461.write('*RST')
        self.k2461.write('*SRE 0')
        self.k2461.write('outp off')
        self.k2461.close()
