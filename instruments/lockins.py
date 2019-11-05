import visa
import numpy as np

__all__ = ['Prologix', 'SR830']


class Prologix:

    def __init__(self, port, address):
        self.address = address
        rm = visa.ResourceManager('@ni')
        self.prolog = rm.open_resource(f'COM{port}', baud_rate=9600)
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
        self.prolog.write(f'++addr {self.address}')
        self.prolog.write(string)

    def query_ascii_values(self, string):
        self.prolog.write(f'++addr {self.address}')
        self.prolog.write(string)
        return self.prolog.query_ascii_values('++read eoi')

    def query(self, string):
        self.prolog.write(f'++addr {self.address}')
        self.prolog.write(string)
        return self.prolog.query('++read eoi')


class SR830:

    def __init__(self):
        self.time_constants = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 1e1, 3e1, 1e2, 3e2,
                               1e3, 3e3, 1e4, 3e4]
        self.sensitivities = [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4,
                              2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1]
        self.sample_rates = [6.25e-2, 1.25e-1, 2.5e-1, 5e-1, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 'trigger']

    def connect(self, port, address):
        self.lockin = Prologix(port, address)
        print(self.lockin.query('*IDN?'))
        self.lockin.write('OVRM 1')

    def get_x(self):
        return float(self.lockin.query_ascii_values("OUTP? 1"))

    def get_y(self):
        return float(self.lockin.query_ascii_values("OUTP? 2"))

    def get_radius(self):
        return float(self.lockin.query_ascii_values("OUTP? 3"))

    def get_angle(self):
        return float(self.lockin.query_ascii_values("OUTP? 4"))

    def get_freq(self):
        return float(self.lockin.query_ascii_values("FREQ?"))

    def get_phase(self):
        return float(self.lockin.query_ascii_values("PHAS?"))

    def set_phase(self, phi):
        # must be float in degrees. will be wrapped and rounded automatically
        self.lockin.write(f'PHAS {phi}')

    def get_sensitivity(self):
        return self.sensitivities[int(self.lockin.query_ascii_values("SENS?"))]

    def set_sensitivity(self, sens):
        try:
            self.lockin.write(f'OFLT {self.sensitivities.index(sens)}s')
        except ValueError:
            print('Not valid sensitivity')

    def get_time_constant(self):
        return self.time_constants[int(self.lockin.query_ascii_values("OFLT?"))]

    def set_time_constant(self, tc):
        try:
            self.lockin.write(f'OFLT {self.time_constants.index(tc)}s')
        except ValueError:
            print('Not valid time constant')

    def get_sample_rate(self):
        return self.sample_rates[int(self.lockin.query_ascii_values("SRAT?"))]

    def set_sample_rate(self, srate):
        try:
            self.lockin.write(f'SRAT {self.sample_rates.index(srate)}s')
        except ValueError:
            print('Not valid sample rate')


    #  This is more complicated because it does not have an internal clock or way to set the measurement number.
    def measure(self):
        self.lockin.write('SEND 0')  # one shot mode: does not overwrite end of buffer
        self.lockin.write('REST')    # resets buffer
        self.set_sample_rate(32)  # 32 Hz sample rate
        self.lockin.write('TSTR 1')  # makes the trigger signal the start of measurements
        #  This is more complicated because it does not have an internal clock or way to set the measurement number.

    def trigger(self):
        self.lockin.write('STRT')

    def read(self, num):
        self.lockin.write('PAUS')
        return np.array(self.lockin.query_ascii_values(f'TRCA? 1, 1, {num}'))*1e6  # in micro volts
