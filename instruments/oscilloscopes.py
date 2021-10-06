import numpy as np
import pyvisa
import time

__all__ = ['DS1104']


class DS1104:

    def connect(self):
        """
        Connects to the DS1104Z instrument using the known unique identifier. Sets timeout to 50 seconds and
        resets the scope.
        :return: null
        """
        rm = pyvisa.ResourceManager('@ivi')
        self.scope = rm.open_resource('USB0::0x1AB1::0x04CE::DS1ZB192600334::INSTR')
        self.scope.timeout = 50000
        print('connected to: ', self.scope.query('*idn?'))
        self.scope.write('*rst')

    def prepare_for_pulse(self, pulsev, res, two_wire, pulse_width, mdepth=120000):
        """
        Sets the limits/scale of channel 1 to be appropriate for measuring the pulse by predicting V drop across a
        shunt resistor. Max pulse width is ~2ms in these settings
        :param float pulsev: float, voltage of applied pulse in V
        :param float res: float, resistance of the shunt resistor in ohms
        :param float two_wire: float, rough resistance of the device in ohms
        :param float pulse_width: duration of pulse. adjusts scope t axis
        :return: null
        """
        lim = pulsev * 3 * (res / two_wire)
        self.scope.write(f'chan{1}:disp 1')
        self.scope.write(f'chan{1}:prob 1')
        self.scope.write(f'chan{1}:scale {lim / 4}')
        self.scope.write(f'chan{1}:rang {lim}')
        self.scope.write('acq:type hres')
        self.scope.write(f'acq:mdep {mdepth}')
        self.scope.write('wav:form ascii')
        self.scope.write('wav:mode raw')
        if pulse_width > 0.3e-6:
            scale = 0.0005
        else:
            scale = 0.0002
        self.scope.write(f'tim:scal {scale}')
        # self.scope.write('tim:range 0.003')



    def prepare_for_4channel_pulse(self, pulsev, res, two_wire, pulse_width, mdepth=300000 ):
        """
        Sets the limits/scale of channel 1 to be appropriate for measuring the pulse by predicting V drop across a
        shunt resistor. Max pulse width is ~2ms in these settings
        :param float pulsev: float, voltage of applied pulse in V
        :param float res: float, resistance of the shunt resistor in ohms
        :param float two_wire: float, rough resistance of the device in ohms
        :param float pulse_width: duration of pulse. adjusts scope t axis
        :return: null
        """
        lim = pulsev * 3 * (res / two_wire)
        self.scope.write(f'chan{1}:disp 1')
        self.scope.write(f'chan{1}:prob 10')
        self.scope.write(f'chan{1}:scale {lim / 4}')
        self.scope.write(f'chan{1}:rang {lim}')
        self.scope.write(f'chan{2}:disp 1')
        self.scope.write(f'chan{2}:prob 10')
        self.scope.write(f'chan{2}:scale {lim * 4}')
        self.scope.write(f'chan{2}:rang {lim}')
        self.scope.write(f'chan{3}:disp 1')
        self.scope.write(f'chan{3}:prob 10')
        self.scope.write(f'chan{3}:scale {lim * 4}')
        self.scope.write(f'chan{3}:rang {lim}')
        self.scope.write('acq:type hres')
        self.scope.write(f'acq:mdep {mdepth}')
        self.scope.write('wav:form ascii')
        self.scope.write('wav:mode raw')
        if pulse_width > 0.3e-6:
            scale = 0.0005
        else:
            scale = 0.0002
        self.scope.write(f'tim:scal {scale}')
        # self.scope.write('tim:range 0.003')


    # Should probably make this set a bunch of custom stuff
    def set_trig_chan(self, chan=2):
        """
        Sets up a trigger of 2.5V and sets channel and it's settings appropriately. Triggers on pos edge. Stops the
        scope. Use single_trig to ready the scope.
        :param chan: the channel the trigger out from the instrument is connected to
        :return: null
        """
        self.scope.write(f'trig:edg:sour chan{chan}')
        self.scope.write(f'chan{chan}:prob 1')
        self.scope.write(f'chan{chan}:scale 2')
        self.scope.write(f'chan{chan}:rang 16')
        self.scope.write('trig:mode edge')
        self.scope.write('trig:edg:slop pos')
        self.scope.write('trig:edg:lev 2.5')
        self.scope.write('trig:swe single')
        self.stop()

    def single_trig(self):
        """
        sets the scope to be ready for a trigger signal.
        :return:
        """
        self.scope.write('single')

    def get_data(self, start, stop, chan=1):
        """
        Retrieves the buffer of chan1 from the scope. Use get_time_inc to find the x-spacing of each point to
        construct time array
        :param start: first data point in the buffer
        :param stop: last data point in the buffer
        :return: np.ndarray, raw y data from the scope
        """
        self.scope.write(f'stop')
        time.sleep(0.2)
        self.scope.write(f'wav:sour chan{chan}')
        self.scope.write(f'wav:start {start}')
        self.scope.write(f'wav:stop {stop}')
        self.scope.write('wav:data?')
        return np.array(str(self.scope.read())[11:].split(','), dtype=np.float32)

    def get_time_inc(self):
        """
        Get the x-spacing from the settings in the scope to construct a time array from.
        :return: float, the time delta between any 2 points in the scope's buffer
        """
        return self.scope.query('wav:xinc?')

    def run(self):
        """
        Start the scope in continuous trigger mode.
        :return: null
        """
        self.scope.write('run')

    def stop(self):
        """
        Stops the scope
        :return: null
        """
        self.scope.write(f'stop')

    def close(self):
        """
        Closes the instrument, i.e. frees the port up for other applications/threads
        :return: null
        """
        self.scope.close()
