import visa
import numpy as np
import time

__all__ = ['K2400', 'K2401', 'K2461', 'K2661']


class K2400:
    """
    Keithley 2400 control interface designed for use when switching
    """

    def connect(self, port):
        """
        connects to the instrument with baud rate 19200 and timeout 10s. prints IDN.
        :param int port: the COM port number i.e. 3 for COM3
        :return:
        """
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
        """
        Sends a square pulse of 5ms duration and specified amplitude Amps
        :param float current: current in AMPS
        :return:
        """
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
        """
        Measure many points in 4 wire mode. Use with "trigger" and "read buffer"
        :param float current: the source current for 4wire measurements
        :param float num: number of points to measure
        :param float nplc: number of powerline cycles per measurement
        :return:
        """
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

    def trigger(self):
        """
        Send the command to start measurements and wait to finish before processing further commands.
        :return:
        """
        self.k2400.write('init')
        self.k2400.write('*wai')

    def read_buffer(self):
        """
        Disables output current and then reads all data from the buffer in the format: current, voltage, time, current voltage time...
        :return: time, voltage, current. Use v/c to get resistance.
        :rtype: (np.ndarray, np.ndarray, np.ndarray)
        """
        self.k2400.write('outp off')
        data = np.array(self.k2400.query_ascii_values('trac:data?'))
        t = data[2::3]
        v = data[1::3]
        c = data[0::3]
        return t, v, c

    def close(self):
        """
        Closes the instrument, i.e. frees the port up for other applications/threads. Also disables output.
        :return:
        """
        self.k2400.write('outp off')
        self.k2400.close()


class K2401:
    def connect(self, port):
        """
        connects to the instrument with baud rate 19200 and timeout 10s. prints IDN.
        :param port: int, the COM port number i.e. 3 for COM3
        :return:
        """
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

    def pulse_current(self, current):
        """
        Sends a square pulse of 5ms duration and specified amplitude Amps
        :param current: float, current in AMPS
        :return:
        """
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
        """
        Measure many points in 4 wire mode. Use with "trigger" and "read buffer"
        :param current: float, the source current for 4wire measurements
        :param num: float/int, number of points to measure
        :param nplc: float/int, number of powerline cycles per measurement
        :return:
        """
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

    def trigger(self):
        """
        Send the command to start measurements and wait to finish before processing further commands.
        :return:
        """
        self.k2401.write('init')
        self.k2401.write('*wai')

    # reads the results from the buffer
    def read_buffer(self):
        """
        Disables output current and then reads all data from the buffer in the format: current, voltage, time, current voltage time...
        :return: time, voltage, current. Use v/c to get resistance.
        :rtype: (np.ndarray, np.ndarray, np.ndarray)
        """
        self.k2401.write('outp off')
        data = np.array(self.k2401.query_ascii_values('trac:data?'))
        t = data[2::3]
        v = data[1::3]
        c = data[0::3]
        return t, v, c

    def close(self):
        """
        Closes the instrument, i.e. frees the port up for other applications/threads. Also disables output.
        :return:
        """
        self.k2401.write('outp off')
        self.k2401.close()


class K2461:

    def connect(self):
        """
        Connects to our Keithley 2461 sourcemeter instrument using the known unique identifier. Sets timeout to 50 seconds and
        resets the instrument.
        :return:
        """
        rm = visa.ResourceManager('@ni')
        self.k2461 = rm.open_resource('USB0::0x05E6::0x2461::04121022::INSTR', write_termination='\n', send_end=True)
        self.k2461.timeout = 50000
        print('connected to: ', self.k2461.query('*idn?'))
        self.k2461.write('*rst')

    def prepare_pulsing_voltage(self, voltage, width, clim=100e-3):
        """
        Forms a voltage pulse trigger group for the instrument.See also: send_pulse and set_ext_trig()
        :param float voltage: The desired peak voltage of the sample in volts
        :param float width: The duration of the rise time and plateau in seconds
        :param float clim: The current limit for the pulse def:100mA
        :return:
        """
        self.k2461.write('*rst')
        self.k2461.write(
            f'sour:puls:swe:volt:lin 0, 0, {voltage}, 2, {width}, off, "defbuffer1", 0, 0, 1, {clim}, {clim}, off, off')
        self.set_ext_trig()

    def prepare_pulsing_current(self, current, width, vlim=40):
        """
        Forms a current pulse trigger group for the instrument. See also: send_pulse and set_ext_trig()
        :param float current: Desired peak current in AMPS (please use 1e-3 for milliamps for eg.
        :param float width: Duration of pulse rise and plateau time in seconds
        :param float vlim: The voltage limit for the pulse def: 40V
        :return:
        """
        self.k2461.write('*rst')
        self.k2461.write(
            f'sour:puls:swe:curr:lin 0, 0, {current}, 2, {width}, off, "defbuffer1", 0, 0, 1, {vlim}, {vlim}, off, off')

    def set_ext_trig(self, pin=3):
        """
        Configures the DIO pins on the instrument to send an external positive edges pulse to occur just before the
        voltage pulse is sent to the DUT
        :param pin: int/float the DIO pin on the instrument that is connected to the stinger on the BNC cable for the
                    scope (default 3). The script will work without a scope connected, of course.
        :return:
        """
        # todo(stu) figure out how to avoid the k2461 warning about pulse width.
        self.k2461.write(f'dig:line{pin}:mode trig, out')
        self.k2461.write(f'trig:dig{pin}:out:log pos')
        self.k2461.write(f'trig:dig{pin}:out:stim NOT1')
        self.k2461.write('trig:bloc:not 5, 1')
        self.k2461.write(f'TRIG:DIG{pin}:OUT:PULS 100e-6')

    def send_pulse(self):
        """
        Activates the preloaded trigger group from prepare_pulsing_voltage or prepare_pulsing_current to emit a pulse
        and (if configured) an external trigger
        :return:
        """
        self.k2461.write('init')  # send pulse

    def measure_n(self, current, num, nplc=2):
        """
        Prepares the instruments to measure specified number of points in a 4wire resistance configuration. Use trigger
        start the measurement and read_buffer to collect the data. This does not enable probe current.
        :param float current: probing current amplitude in amps
        :param float num: number of points to measure
        :param float nplc: number of powerline cycles per point def: 2
        :return:
        """
        self.k2461.write('*rst')
        self.k2461.write(f'trac:make "mybuffer", {num}')
        self.k2461.write('sour:curr:rang 200e-6')
        self.k2461.write('sour:func curr')
        self.k2461.write(f'sour:curr {current}')
        self.k2461.write('sour:curr:read:back on')
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rsen on')
        self.k2461.write(f'sens:volt:nplc {nplc}')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write(f'count {num}')

    def enable_4_wire_probe(self, current, nplc=2):
        """
        Prepares the instrument to measure a 4wire resistance one at a time. For use with either trigger_fetch and
        fetch_one or with read_one. This enables probe current.
        :param float current:
        :param float nplc:
        :return:
        """
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
        """
        Prepares the instrument to measure a 2wire resistance one at a time. For use with either trigger_fetch and
        fetch_one or with read_one. This enables probe current.
        :param float current: probing current in amps
        :param float nplc: number of powerline cycles to measure for
        :return:
        """
        self.k2461.write('sens:func "volt"')
        self.k2461.write('sens:volt:rang:auto on')
        self.k2461.write('sens:volt:rsen off')
        self.k2461.write(f'sens:volt:nplc {nplc}')
        self.k2461.write('sour:func curr')
        self.k2461.write(f'sour:curr {current}')
        self.k2461.write('sour:curr:vlim 2')
        self.k2461.write('outp on')

    def trigger(self):
        """
        Starts applying current and initiates the measurement set up using measure_n. Also use read_buffer then
        disable_probe_current.
        :return:
        """
        # self.k2461.write('init')
        self.k2461.write('outp on')
        self.k2461.write('trac:trig "mybuffer"')
        self.k2461.write('*wai')

    def trigger_fetch(self):
        """
        Triggers a single measurement for reading back off later. Use for higher synchronicity between instruments.
        Use fetch_one to get the data. See also: read_one
        :return:
        """
        self.k2461.write('trac:trig "defbuffer1"')
        self.k2461.write('*wai')

    def read_buffer(self, num):
        """
        Reads a specified number of points from the buffer and returns the data as numpy arrays
        :param float num: number of points to be read
        :return: time relative to trigger, voltage, current. Use v/c to resistance.
        :rtype: (np.ndarray, np.ndarray, np.ndarray)
        """
        self.k2461.write('outp off')
        try:
            data = np.array(self.k2461.query_ascii_values(f'trac:data? 1, {num}, "mybuffer", sour, read, rel'))
            t = data[2::3]
            v = data[1::3]
            c = data[0::3]
            return t, v, c
        except:
            print('could not read data from K2461')
            return np.array([]), np.array([]), np.array([])

    def read_one(self):
        """
        Measures, reads and returns a single value from the instrument. For use with enable_2_wire_probe and
        enable_4_wire_probe. To measure and read separately, see trigger_fetch and fetch_one
        :return: current, voltage. Do v/c for resistance
        :rtype: (float, float)
        """
        data = np.array([self.k2461.query_ascii_values('read? "defbuffer1", sour, read')])
        # print(data)
        cur = data[0][0]
        vol = data[0][1]
        return cur, vol

    def fetch_one(self):
        """
        Reads and returns a single value from the instrument. For use with trigger_fetch and either enable_2_wire_probe
        or enable_4_wire_probe.
        :return: current, voltage. Do v/c for resistance
        :rtype: (float, float)
        """
        data = self.k2461.query_ascii_values('fetch? "defbuffer1", sour, read')
        return data[1], data[0]

    def disable_probe_current(self):
        """
        Stops the instrument from outputting current. Same as hitting "output on/off" on the front IO.
        :return:
        """
        self.k2461.write('outp off')

    def close(self):
        """
        Closes the instrument connection, i.e. frees the port up for other applications/threads. Also disables output.
        :return:
        """
        self.k2461.write('*rst')
        self.k2461.write('*sre 0')
        self.k2461.write('outp off')
        self.k2461.close()


class K2661:

    def connect(self, port):
        """
        Connects to device and resets it
        :param int port:
        :return:
        """
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

    def sine_wave(self, hz, ma, duty=50):
        """
        Prepare the instrument to produce a sine wave output. Use with wave_output_on and wave_output_off
        :param hz: Frequency in Hz
        :param float ma: peak to peak amplitude in Milliamps
        :param duty: Duty cycle def: 50%
        :return:
        """
        self.k2661.write('*RST')
        self.k2661.write('SOUR:WAVE:FUNC SIN')
        self.k2661.write(f'SOUR:WAVE:FREQ {hz}')
        self.k2661.write(f'SOUR:WAVE:AMPL {ma * 1e-3}')
        self.k2661.write('SOUR:WAVE:ARM')

    # Current in mA and Freq in Hz duty in %
    def square_wave(self, hz, ma, duty=50):
        """
        Prepare a square wave output. Use with wave_output_on and wave_output_off
        :param float hz: desired frequency in Hz
        :param float ma: desired amplitude in milliAmps
        :param float duty: Duty cycle def: 50%
        :return:
        """
        self.k2661.write('*RST')
        self.k2661.write('SOUR:WAVE:FUNC SQU')
        self.k2661.write(f'SOUR:WAVE:FREQ {hz}')
        self.k2661.write(f'SOUR:WAVE:AMPL {ma * 1e-3}')
        self.k2661.write(f'SOUR:WAVE:DCYC {duty}')
        self.k2661.write('SOUR:WAVE:ARM')

    def wave_output_on(self):
        """
        Enables the output for the wave prepared using sine_wave or square_wave
        :return:
        """
        self.k2661.write('SOUR:WAVE:INIT')

    def wave_output_off(self):
        """
        Disables current output
        :return:
        """
        self.k2661.write('SOUR:WAVE:ABOR')

    def close(self):
        """
        Closes the instrument connection, i.e. frees the port up for other applications/threads. Also disables output.
        :return:
        """
        self.k2661.write('SOUR:WAVE:ABOR')
        self.k2661.close()
