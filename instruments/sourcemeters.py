import visa
import numpy as np
import time

__all__ = ['K2400', 'K2401', 'K2461', 'K2661']




class K2400:
    # Connects to K2401 using given port. Use 19200 baud rate (or 19.2K on screen)
    def connect(self, port):
        rm = visa.ResourceManager('@ni')
        self.k2400 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2400.close()
        self.k2400.open()
        self.k2400.baud_rate = 19200
        self.k2400.timeout = 10000
        self.k2400.write_termination = '\r\n'
        self.k2400.read_termination = '\r\n'
        self.k2400.write('*rst')
        self.k2400.write('*cls')
        print('connected to: ', self.k2400.query('*IDN?'))

    # Sends a square pulse of 5ms duration and amplitude "current" Amps
    def pulse_current(self, current):
        self.k2400.write('*rst')
        self.k2400.write(':SYSTEM:BEEP:STATE OFF')
        self.k2400.write('trac:cle')
        self.k2400.write('*cls')
        self.k2400.write(':syst:rsen on')
        self.k2400.write('trig:coun 1')
        self.k2400.write('sour:func curr')
        self.k2400.write('sens:func:conc off')
        self.k2400.write('sens:volt:rang:auto on')
        self.k2400.write('sens:volt:prot:lev 20')
        self.k2400.write(f'sour:curr:lev {current}')
        self.k2400.write('trig:del 0')
        self.k2400.write('sour:del 0')
        self.k2400.write('sour:cle:auto on')
        self.k2400.write('init')
        self.k2400.write('*wai')

    # Sets up the parameters to measure data and store it in buffer
    def measure_n(self, current, num, nplc=2):
        self.k2400.write('*rst')
        self.k2400.write('*cls')
        self.k2400.write(':SYSTEM:BEEP:STATE OFF')
        self.k2400.write('sour:func curr')
        self.k2400.write(f'sour:curr {current}')
        self.k2400.write('sour:curr:rang:auto on')
        self.k2400.write('sens:volt:prot:lev 20')
        self.k2400.write('sens:func "volt"')
        self.k2400.write(f'sens:volt:nplc {nplc}')
        self.k2400.write('sens:volt:rang:auto on')
        self.k2400.write('syst:rsen on')
        self.k2400.write('form:elem time, volt, curr')
        self.k2400.write('trac:cle')  # clear buffer
        self.k2400.write(f'trig:count {num}')  # number of p
        self.k2400.write(f'trac:poin {num}')  # size of buff
        self.k2400.write('trac:feed sens')  # what goes in b
        self.k2400.write('trac:feed:cont next')  # doesn't o
        self.k2400.write('trac:tst:form abs')
        self.k2400.write('outp on')

    # Initiates the measurement loop
    def trigger(self):
        self.k2400.write('init')
        self.k2400.write('*wai')

    # reads the results from the buffer
    def read_buffer(self):
        self.k2400.write('outp off')
        data = np.array(self.k2400.query_ascii_values('trac:data?'))
        t = data[2::3]
        v = data[1::3]
        c = data[0::3]
        return t, v, c

    def close(self):
        self.k2400.write('outp off')
        self.k2400.close()


class K2401:
    # Connects to K2401 using given port. Use 19200 baud rate (or 19.2K on screen)
    def connect(self, port):
        rm = visa.ResourceManager('@ni')
        self.k2401 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2401.close()
        self.k2401.open()
        self.k2401.baud_rate = 19200
        self.k2401.timeout = 10000
        self.k2401.write_termination = '\r\n'
        self.k2401.read_termination = '\r\n'
        self.k2401.write('*rst')
        self.k2401.write('*cls')
        print('connected to: ', self.k2401.query('*IDN?'))

    # Sends a square pulse of 5ms duration and amplitude "current" Amps
    def pulse_current(self, current):
        self.k2401.write('*rst')
        self.k2401.write('trac:cle')
        self.k2401.write('*cls')
        self.k2401.write(':syst:rsen on')
        self.k2401.write('trig:coun 1')
        self.k2401.write('sour:func curr')
        self.k2401.write('sens:func:conc off')
        self.k2401.write('sens:volt:rang:auto on')
        self.k2401.write('sens:volt:prot:lev 20')
        self.k2401.write(f'sour:curr:lev {current}')
        self.k2401.write('trig:del 0')
        self.k2401.write('sour:del 0')
        self.k2401.write('sour:cle:auto on')
        self.k2401.write('init')
        self.k2401.write('*wai')

    # Sets up the parameters to measure data and store it in buffer
    def measure_n(self, current, num, nplc=2):
        self.k2401.write('*rst')
        self.k2401.write('*cls')
        self.k2401.write('sour:func curr')
        self.k2401.write(f'sour:curr {current}')
        self.k2401.write('sour:curr:rang:auto on')
        self.k2401.write('sens:volt:prot:lev 20')
        self.k2401.write('sens:func "volt"')
        self.k2401.write(f'sens:volt:nplc {nplc}')
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

    # Initiates the measurement loop
    def trigger(self):
        self.k2401.write('init')
        self.k2401.write('*wai')

    # reads the results from the buffer
    def read_buffer(self):
        self.k2401.write('outp off')
        data = np.array(self.k2401.query_ascii_values('trac:data?'))
        t = data[2::3]
        v = data[1::3]
        c = data[0::3]
        return t, v, c

    def close(self):
        self.k2401.write('outp off')
        self.k2401.close()


class K2461:

    # connects to the k2461. If a different k2461 is bought, may have to add a loop to try all known resource names
    def connect(self):
        rm = visa.ResourceManager('@ni')
        self.k2461 = rm.open_resource('USB0::0x05E6::0x2461::04121022::INSTR')
        self.k2461.timeout = 50000
        print(self.k2461.query('*IDN?'))
        # self.k2400.write(':SYST:BEEP:STAT OFF')
        self.k2461.write(':*RST')
        self.k2461.write('sour:func curr')
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write(f'trac:make "defBuffer1", {10000}')

    # sets up and sends a single square wave pulse with duration "width" in seconds and amplitude "current" in Amps
    def pulse_current(self, current, width=1e-3, vlim=30):
        self.k2461.write('sens:volt:rsen off')  # measure 2 wire
        self.k2461.write(':form:asc:prec 16')  # data precision to 16
        # set up pulse waveform
        self.k2461.write(
            f'sour:puls:swe:curr:lin 0, 0, {current}, 2, {width}, off, "defbuffer1", 0, 0, 1, {vlim}, {vlim}, off, off')
        self.k2461.write('init')  # send pulse
        self.k2461.write('*wai')  # queue up following commands instead of activating them instantly

    # sets up and sends a single square wave pulse with duration "width" in second and amplitude "voltage" in Volts
    def pulse_voltage(self, voltage, width=1e-3, clim=75e-3):
        self.k2461.write('sens:curr:rsen off')  # measure 2 wire
        self.k2461.write(':form:asc:prec 16')  # data precision to 16esigner
        # set up pulse waveform
        # :SOURce[1]:PULSe:SWEep:<function>:LINear <biasLevel>, <start>, <stop>, <points>, <pulseWidth>, <measEnable>,
        # "<bufferName>", <delay>, <offTime>, <count>, <xBiasLimit>, <xPulseLimit>, <failAbort>, <dual>
        # page 6-110 in ref man
        self.k2461.write(
            f'sour:puls:swe:volt:lin 0, 0, {voltage}, 2, {width}, off, "defbuffer1", 0, 0, 1, {clim}, {clim}, off, off')
        time.sleep(0.05)
        self.k2461.write('init')  # send pulse
        self.k2461.write('*wai')  # queue up following commands instead of activating them instantly

    # sets up a measurement of "num" points with applied probe current of "current" Amps
    def measure_n(self, current, num, nplc=2):
        self.k2461.write('*rst')
        self.k2461.write(f'trac:make "mybuffer", {num}')
        self.k2461.write('sour:curr:rang 200e-6')
        self.k2461.write('sour:func curr')
        self.k2461.write(f'sour:curr {current}')
        self.k2461.write('sour:curr:read:back on')

        self.k2461.write('sens:func "volt"')

        # self.k2400.write('sour:curr:vlim 1')
        self.k2461.write('sens:volt:rsen on')
        self.k2461.write(f'sens:volt:nplc {nplc}')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write(f'count {num}')
        # self.k2461.write(f'trig:load "SimpleLoop", {num}, 0, "defBuffer1"')
        # self.k2461.write(f'sens:count {num}')
        self.k2461.write('outp on')

    # initiates the measurement set up using measure
    def trigger(self):
        # self.k2461.write('init')
        self.k2461.write(':trac:trig "mybuffer"')
        self.k2461.write('*wai')

    def trigger_fetch(self):
        self.k2461.write(':trac:trig "defbuffer1"')
        self.k2461.write('*wai')

    # reads num data points from the buffer
    def read_buffer(self, num):
        self.k2461.write('outp off')
        # print(self.k2400.query('trac:act? "defBuffer1"'))
        try:
            data = np.array(self.k2461.query_ascii_values(f'trac:data? 1, {num}, "mybuffer", sour, read, rel'))
            t = data[2::3]
            v = data[1::3]
            c = data[0::3]
            return t, v, c
        except:
            print('could not read data from K2461')
            return np.array([]), np.array([]), np.array([])

    # For use when reading one value from the source meter in 4 wire mode.
    # Applies current and measures voltage drop across device (Rxx)
    def enable_4_wire_probe(self, current, nplc=2):
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write('sens:volt:rsen on')
        self.k2461.write(f'sens:volt:nplc {nplc}')
        self.k2461.write('sour:func curr')
        self.k2461.write(f'sour:curr {current}')
        self.k2461.write('sour:curr:vlim 2')
        self.k2461.write('outp on')

    # For use when reading one value from Source meter at a time in 2 wire mode.
    # Applies current and measures voltage required to apply that current
    # nplc: 0.02, 0.2, 1, 10, 100, 200. 0.2 is "fast".
    def enable_2_wire_probe(self, current, nplc=2):
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write('sens:volt:rsen off')
        self.k2461.write(f'sens:volt:nplc {nplc}')
        self.k2461.write('sour:func curr')
        self.k2461.write(f'sour:curr {current}')
        self.k2461.write('sour:curr:vlim 2')
        self.k2461.write('outp on')

    # Use after measuring with probe current to disable output
    def disable_probe_current(self):
        self.k2461.write('outp off')

    # For use with "enable_2_wire_probe" or "enable_4_wire_probe" to read individual values
    def read_one(self):
        data = np.array([self.k2461.query_ascii_values(':READ? "defbuffer1", sour, read')])
        print(data)
        cur = data[0][0]
        vol = data[0][1]
        return cur, vol

    def fetch_one(self):
        data = self.k2461.query_ascii_values(':fetch? "defbuffer1", sour, read')
        return data[1], data[0]

    # closes connections and allows for a new process to connect
    def close(self):
        self.k2461.write('*rst')
        self.k2461.write('*sre 0')
        self.k2461.write('outp off')
        self.k2461.close()


class K2661:
    def connect(self, port):
        rm = visa.ResourceManager('@ni')
        self.k2661 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2661.close()
        self.k2661.open()
        self.k2661.baud_rate = 19200
        self.k2661.timeout = 10000
        self.k2661.write_termination = '\r\n'
        self.k2661.read_termination = '\r\n'
        self.k2661.write('*rst')
        self.k2661.write('*cls')
        print('connected to: ', self.k2661.query('*IDN?'))

    def sine_wave(self,  hz, ma, duty=50):
        self.k2661.write('*RST')
        self.k2661.write('SOUR:WAVE:FUNC SIN')
        self.k2661.write(f'SOUR:WAVE:FREQ {hz}')
        self.k2661.write(f'SOUR:WAVE:AMPL {ma*1e-3}')
        self.k2661.write('SOUR:WAVE:ARM')

    # Current in mA and Freq in Hz duty in %
    def square_wave(self, hz, ma, duty=50):
        self.k2661.write('*RST')
        self.k2661.write('SOUR:WAVE:FUNC SQU')
        self.k2661.write(f'SOUR:WAVE:FREQ {hz}')
        self.k2661.write(f'SOUR:WAVE:AMPL {ma*1e-3}')
        self.k2661.write(f'SOUR:WAVE:DCYC {duty}')
        self.k2661.write('SOUR:WAVE:ARM')

    def wave_output_on(self):
        self.k2661.write('SOUR:WAVE:INIT')

    def wave_output_off(self):
        self.k2661.write('SOUR:WAVE:ABOR')

    def close(self):
        self.k2661.close()
