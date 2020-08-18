import numpy as np
import visa
import time

__all__ = ['DS1104']


class DS1104:

    def connect(self):
        rm = visa.ResourceManager('@ni')
        self.scope = rm.open_resource('USB0::0x1AB1::0x04CE::DS1ZB192600334::INSTR')
        self.scope.timeout = 50000
        self.scope.write('*rst')
        self.scope.write('acq:mdep 6000000')

    def prepare_for_pulse(self, pulsev):
        lim = pulsev * 1.2
        self.scope.write(f'chan{1}:disp 1')
        self.scope.write(f'chan{1}:prob 1')
        self.scope.write(f'chan{1}:scale {lim / 4}')
        self.scope.write(f'chan{1}:rang {lim}')
        self.scope.write(f'chan{2}:disp 1')
        self.scope.write(f'chan{2}:prob 1')
        self.scope.write(f'chan{2}:scale {lim / 4}')
        self.scope.write(f'chan{2}:rang {lim}')
        self.scope.write('wav:form ascii')
        self.scope.write('wav:mode raw')
        self.scope.write('tim:scal 0.02')
        self.scope.write('tim:range 0.24')

    # Should probably make this set a bunch of custom stuff
    def set_trig_chan(self, n=3):
        self.scope.write(f'trig:edg:sour chan{n}')

        self.scope.write(f'chan{n}:prob 1')
        self.scope.write(f'chan{n}:scale 2')
        self.scope.write(f'chan{n}:rang 16')
        self.scope.write('trig:mode edge')
        self.scope.write('trig:edg:slop neg')
        self.scope.write('trig:edg:lev 2.5')
        # self.scope.write('trig:swe single')

    def single_trig(self):
        self.scope.write('trig:swe single')

    def get_data(self, start, stop):
        self.scope.write(f'stop')
        self.scope.write(f'wav:sour chan{1}')
        self.scope.write(f'wav:start {start}')
        self.scope.write(f'wav:stop {stop}')
        self.scope.write('wav:data?')
        chan1 = np.array(str(self.scope.read())[11:].split(','), dtype=np.float32)
        self.scope.write(f'wav:sour chan{2}')
        self.scope.write(f'wav:start {start}')
        self.scope.write(f'wav:stop {stop}')
        self.scope.write('wav:data?')
        chan2 = np.array(str(self.scope.read())[11:].split(','), dtype=np.float32)
        # [13:-3].split(',')
        return chan1-chan2

    def get_time_inc(self):
        return self.scope.query('wav:xinc?')
