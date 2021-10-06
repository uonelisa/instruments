import pyvisa
import numpy as np
import time

__all__ = ['Prologix', 'SR830', 'SR830_RS232']


class Prologix:
    """
    Defines constant values on object instantiation and also connects because thsi will be made during the
    lock-in's connect call
    """

    def __init__(self, port, address):
        """
        Connects to the prologix on creation.
        :param int port: The COM port number on the prologix virtual GPIB adapter
        :param int address: The GPIB address of the desired instrument.

        :returns: None
        """
        self.address = 0
        self.baud_rate = 19200
        self.address = address
        rm = pyvisa.ResourceManager('@ivi')
        self.prolog = rm.open_resource(f'COM{port}', baud_rate=self.baud_rate)
        self.prolog.close()
        self.prolog.open()
        self.prolog.baud_rate = 19200
        self.prolog.timeout = 5000
        self.prolog.write_termination = '\r\n'
        self.prolog.read_termination = '\r\n'
        print(self.prolog.query('++ver'))
        self.prolog.write('++mode 1')
        self.prolog.write('++auto 0')
        self.prolog.write('++eoi 1')

    def write(self, string):
        """
        Writes a command to the desired object using prologix

        :param str string: The message to be sent

        :returns: None
        """
        self.prolog.write(f'++addr {self.address}')
        self.prolog.write(string)

    def query_ascii_values(self, string):
        """
        sends a command to the lockin and reads some data to the desired object using prologix

        :param str string:

        :returns: None
        """
        self.prolog.write(f'++addr {self.address}')
        self.prolog.write(string)
        return self.prolog.query_ascii_values('++read eoi')

    def query(self, string):
        """
        Is supposed to read data after sending a command but seems broken

        :param str string:

        :returns: None
        """
        self.prolog.write(f'++addr {self.address}')
        self.prolog.write(string)
        return self.prolog.query('++read eoi')


class SR830:
    """
    SR830 communication using the prologix adapter
    """

    def __init__(self):
        """
        arrays defined for use later
        """
        self.time_constants = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 1e1, 3e1, 1e2, 3e2,
                               1e3, 3e3, 1e4, 3e4]
        self.sensitivities = [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4,
                              2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1]
        self.sample_rates = [6.25e-2, 1.25e-1, 2.5e-1, 5e-1, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 'trigger']

    def connect(self, port, address):
        """
        connects to the prologix and saves this object as a class member such that it can be used with address "address"
        another lockin can use the same port with a different address.

        :param port: Connected COM Port of the prologix adapter
        :param address: address of this instrument

        :returns: None
        """
        self.lockin = Prologix(port, address)
        print('connected to: ', self.lockin.query('*IDN?'))
        self.lockin.write('OVRM 1')

    def measure_n(self, sr):
        """
        Prepare to measure multiple values.
        This is more complicated than usual because it does not have an internal clock or way to set the measurement
        number so just leave this running with a pause or a sleep.

        :param float sr: sample rate

        :returns: None
        """
        self.lockin.write('SEND 0')  # one shot mode: does not overwrite end of buffer
        self.lockin.write('REST')  # resets buffer
        self.set_sample_rate(sr)  # 32 Hz sample rate
        self.lockin.write('TSTR 1')  # waits for the trigger to start measurements

    def trigger(self):
        """
        Initiates measurements (use with measure_n and read_buffer)

        :returns: None
        """
        self.lockin.write('STRT')

    def read_buffer(self, num):
        """
        reads the full buffer (use with measure_n and trigger)

        :param int num: number of values to try and read from the buffer

        :returns: voltage readings in uV
        :rtype: np.ndarray
        """
        self.lockin.write('PAUS')
        return np.array(self.lockin.query_ascii_values(f'TRCA? 1, 1, {num}')) * 1e6  # in micro volts

    def get_x(self):
        """
        Read one x value from lockin

        :returns: x value in V
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 1"))

    def get_y(self):
        """
        Read one y value from lockin

        :returns: y value in V
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 2"))

    def get_radius(self):
        """
        Read one radius value from lockin

        :returns: radius value in V
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 3"))

    def get_angle(self):
        """
        Read one angle value from lockin

        :returns: angle value in degrees
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 4"))

    def get_freq(self):
        """
        get frequency of reference wave from lockin

        :returns: frequency in Hz
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("FREQ?"))

    def get_phase(self):
        """
        get phase of reference wave from lockin

        :returns: phase in degrees
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("PHAS?"))

    def get_sensitivity(self):
        """
        get sensitivty value from lockin

        :returns: sensitivty range in V
        :rtype: float
        """
        return self.sensitivities[int(self.lockin.query_ascii_values("SENS?"))]

    def get_time_constant(self):
        """
        get time constant value from lockin

        :returns: time constant in seconds
        :rtype: float
        """
        return self.time_constants[int(self.lockin.query_ascii_values("OFLT?"))]

    def get_sample_rate(self):
        """
        get sample rate value from lockin

        :returns: sample rate in Hz
        :rtype: float
        """
        return self.sample_rates[int(self.lockin.query_ascii_values("SRAT?"))]

    def set_phase(self, phi):
        """
        Set the phase of the lockin. Value will be wrapped and rounded automatically
        :param float phi: desired phase

        :returns: None
        """
        self.lockin.write(f'PHAS {phi}')

    def set_sensitivity(self, sensitivity):
        """
        Set the measurement voltage range

        :param float sensitivity: Sensitivity in Volts, possible values: [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4,
                              2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1]

        :returns: None
        """
        try:
            self.lockin.write(f'OFLT {self.sensitivities.index(sensitivity)}s')
        except ValueError:
            print('Not vlid sensitivity')

    #
    def set_time_constant(self, tc):
        """
        Set time constant in seconds

        :param float tc: Time Constant in seconds, possible values: [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 1e1, 3e1, 1e2, 3e2,
                               1e3, 3e3, 1e4, 3e4]

        :returns: None
        """
        try:
            self.lockin.write(f'OFLT {self.time_constants.index(tc)}s')
        except ValueError:
            print('Not valid time constant')

    def set_sample_rate(self, sample_rate):
        """
        Set sample rate in Hz

        :param float/str sample_rate: Sample rate in Hz, possible values: [6.25e-2, 1.25e-1, 2.5e-1, 5e-1, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 'trigger']

        :returns: None
        """
        try:
            self.lockin.write(f'SRAT {self.sample_rates.index(sample_rate)}s')
        except ValueError:
            print('Not valid sample rate')


class SR830_RS232:
    """
    SR830 communication using RS232
    """

    def __init__(self):
        """
        arrays defined for use later
        """
        self.time_constants = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 1e1, 3e1, 1e2, 3e2,
                               1e3, 3e3, 1e4, 3e4]
        self.sensitivities = [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4,
                              2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1]
        self.sample_rates = [6.25e-2, 1.25e-1, 2.5e-1, 5e-1, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 'trigger']
        self.filters = [6, 12, 18, 24]

    def connect(self, port):
        """
        connects to lockin directly

        :param port: Connected COM Port of the instrument adapter

        :returns: None
        """
        rm = pyvisa.ResourceManager('@ivi')
        self.lockin = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.lockin.close()
        self.lockin.open()
        self.lockin.baud_rate = 19200
        self.lockin.timeout = 10000
        self.lockin.write_termination = '\r'
        self.lockin.read_termination = '\r'
        print('connected to: ', self.lockin.query('*IDN?'))

    def measure_n(self, sr):
        """
        Prepare to measure multiple values.
        This is more complicated than usual because it does not have an internal clock or way to set the measurement
        number so just leave this running with a pause or a sleep.

        :param float sr: sample rate

        :returns: None
        """
        self.lockin.write('SEND 0')  # one shot mode: does not overwrite end of buffer
        self.lockin.write('REST')  # resets buffer
        self.set_sample_rate(sr)  # 32 Hz sample rate
        self.lockin.write('TSTR 1')  # waits for the trigger to start measurements

    def trigger(self):
        """
        Initiates measurements (use with measure_n and read_buffer)

        :returns: None
        """
        self.lockin.write('STRT')

    def read_buffer(self, num):
        """
        reads the full buffer (use with measure_n and trigger)

        :param int num: number of values to try and read from the buffer

        :returns: voltage readings in uV
        :rtype: np.ndarray
        """
        self.lockin.write('PAUS')
        return np.array(self.lockin.query_ascii_values(f'TRCA? 1, 1, {num}')) * 1e6  # in micro volts

    def get_x(self):
        """
        Read one x value from lockin

        :returns: x value in V
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 1")[0])

    def get_y(self):
        """
        Read one y value from lockin

        :returns: y value in V
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 2")[0])

    def get_radius(self):
        """
        Read one radius value from lockin

        :returns: radius value in V
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 3")[0])

    def get_angle(self):
        """
        Read one angle value from lockin

        :returns: angle value in degrees
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("OUTP? 4")[0])

    def get_freq(self):
        """
        get frequency of reference wave from lockin

        :returns: frequency in Hz
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("FREQ?")[0])

    def get_phase(self):
        """
        get phase of reference wave from lockin

        :returns: phase in degrees
        :rtype: float
        """
        return float(self.lockin.query_ascii_values("PHAS?")[0])

    def get_sensitivity(self):
        """
        get sensitivty value from lockin

        :returns: sensitivty range in V
        :rtype: float
        """
        return self.sensitivities[int(self.lockin.query_ascii_values("SENS?")[0])]

    def get_time_constant(self):
        """
        get time constant value from lockin

        :returns: time constant in seconds
        :rtype: float
        """
        return self.time_constants[int(self.lockin.query_ascii_values("OFLT?")[0])]

    def get_sample_rate(self):
        """
        get sample rate value from lockin

        :returns: sample rate in Hz
        :rtype: float
        """
        return self.sample_rates[int(self.lockin.query_ascii_values("SRAT?")[0])]

    def set_phase(self, phi):
        """
        Set the phase of the lockin. Value will be wrapped and rounded automatically
        :param float phi: desired phase

        :returns: None
        """
        self.lockin.write(f'PHAS {phi}')

    def set_sensitivity(self, sens):
        """
        Set the measurement voltage range

        :param float sensitivity: Sensitivity in Volts, possible values: [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4,
                              2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1]

        :returns: None
        """
        try:
            self.lockin.write(f'OFLT {self.sensitivities.index(sens)}s')
        except ValueError:
            print('Not vlid sensitivity')

    def set_time_constant(self, tc):
        """
        Set time constant in seconds

        :param float tc: Time Constant in seconds, possible values: [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 1e1, 3e1, 1e2, 3e2,
                               1e3, 3e3, 1e4, 3e4]

        :returns: None
        """
        try:
            self.lockin.write(f'OFLT {self.time_constants.index(tc)}s')
        except ValueError:
            print('Not valid time constant')

    def set_sample_rate(self, srate):
        """
        Set sample rate in Hz

        :param float/str sample_rate: Sample rate in Hz, possible values: [6.25e-2, 1.25e-1, 2.5e-1, 5e-1, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 'trigger']

        :returns: None
        """
        try:
            self.lockin.write(f'SRAT {self.sample_rates.index(srate)}s')
        except ValueError:
            print('Not valid sample rate')

    def set_filter(self, attenuation):
        """
        Set filter attenuation in dB

        :param float attenuation: Sample rate in Hz, possible values: [6, 12, 18, 24]

        :returns: None
        """
        self.lockin.write(f'OFSL {self.filters.index(attenuation)}')

    def auto_range(self):
        """
        Activates the built in autoranging feature (same as pressing the auto range button)
        :returns: None
        """
        self.lockin.write(f'AGAN')

    def auto_phase(self):
        """
        Activates the built in autophasing feature (same as pressing the auto phase button)
        :returns: None
        """
        self.lockin.write(f'APHS')

    def set_harmonic(self, harm):
        """
        Set the harmonic number to measure at.

        :param int harm: desired harmonic number (if in doubt, it's 1)

        :return: None
        """
        self.lockin.write(f'HARM {harm}')
