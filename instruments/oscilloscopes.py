import numpy as np
import visa
import time

__all__ = ['DS1104']


class DS1104:

    def connect(self):
        rm = visa.ResourceManager('@ni')
        self.scope = rm.open_resource('USB0::0x1AB1::0x04CE::DS1ZB192600334::INSTR')
        self.scope.timeout = 50000
        print('connected to: ', self.scope.query('*idn?'))
        self.scope.write('*rst')
        self.scope.write('acq:mdep 60000')

    def prepare_for_pulse(self, pulsev, res, two_wire):
        # lim is 1.2* the predicted voltage across the resistor
        lim = pulsev * 1.2 * (res/two_wire)
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
        self.scope.write('tim:scal 0.0005')
        self.scope.write('tim:range 0.006')
        self.scope.write('acq:mdep 60000')

    # Should probably make this set a bunch of custom stuff
    def set_trig_chan(self, n=3):
        self.scope.write(f'trig:edg:sour chan{n}')
        self.scope.write(f'chan{n}:prob 1')
        self.scope.write(f'chan{n}:scale 2')
        self.scope.write(f'chan{n}:rang 16')
        self.scope.write('trig:mode edge')
        self.scope.write('trig:edg:slop pos')
        self.scope.write('trig:edg:lev 2.5')
        self.scope.write('trig:swe single')
        self.stop()

    def single_trig(self):
        self.scope.write('single')


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

    def run(self):
        self.scope.write('run')

    def stop(self):
        self.scope.write(f'stop')

    def close(self):
        self.scope.close()