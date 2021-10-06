import pyvisa
import numpy as np

__all__ = ['K2000']


class K2000:
    """
    Class to control Keithley model 2000 multimeter using RS232 serial port
    """

    def connect(self, port):
        """
        Connect to the instrument using 19.2k baud rate with given port.

        :param int port: desired COM port e.g. 19 for COM19

        :returns: None
        """
        rm = pyvisa.ResourceManager('@ivi')
        self.k2000 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2000.close()
        self.k2000.open()
        self.k2000.baud_rate = 19200
        self.k2000.timeout = 10000
        self.k2000.write_termination = '\r\n'
        self.k2000.read_termination = '\r\n'
        self.k2000.write('*rst')
        self.k2000.write('*cls')
        print('connected to: ', self.k2000.query('*IDN?'))

    def prepare_measure_n(self, num, volt_range=0, nplc=2):
        """
         Sets up the instrument ready to measure multiple values into the buffer. Use with trigger and read_buffer

        :param int num: number of points to measure (and buffer size)
        :param float volt_range: specifies the measurement range in V. Defaults to autorange (0).
        :param float nplc: "number of powerline cycles" per measurement

        :returns: None
        """

        self.k2000.write('sens:func "volt"')  # measure volts
        self.k2000.write(f'sens:volt:nplc {nplc}')  # level of averaging min, 0.01 -> 10 ish Power line cycle:
        # 50hz 2-> 25hz measurement
        self.k2000.write(f'sens:volt:rang {volt_range}')  # auto-ranging
        self.k2000.write(f'trig:count {num}')  # number of points to measure
        self.k2000.write('trac:clear')  # clear buffer
        self.k2000.write(f'trac:poin {num}')  # size of buffer
        self.k2000.write('trac:feed sens')  # what goes in buffer
        self.k2000.write('trac:feed:cont next')  # doesn't overwrite previous data until full

    # sets up measurement for one single values. For use with a source meter to provide current and use
    # read_one to take readings. see trigger
    def prepare_measure_one(self, volt_range=0, nplc=2):
        """
        sets up measurement for one single values. For use with a source meter to provide current. Use trigger and then
        fetch_one to take readings separately or use measure_one/read_one to trigger and read in one call
        (less synchronous between devices)

        :param float volt_range: specifies the measurement range in V. Defaults to autorange (0).
        :param float nplc: "number of powerline cycles" per measurement

        :returns: None
        """
        self.k2000.write('sens:func "volt"')  # measure volts
        self.k2000.write(f'sens:volt:nplc {nplc}')  # level of averaging min, 0.01 -> 10 ish Power line cycle:
        # 50hz 2-> 25hz measurement
        self.k2000.write(f'sens:volt:rang {volt_range}')  # 0-> auto-ranging

    def trigger(self):
        """
        Initiates the measurement. Use after prepare_measure_one or prepare_measure_n and before read_one or read_buffer

        :returns: None
        """
        self.k2000.write('init')
        self.k2000.write('*wai')

    def read_buffer(self):
        """
        Reads the data from buffer. For use with prepare_measure_n and trigger.

        :returns: voltage values
        :rtype: np.ndarray
        """
        # self.k2000.write('form:data ASCII')  #  read doesn't work without this line ?
        data = self.k2000.query_ascii_values('trac:data?')

        data = np.array(data)

        return data

    def read_one(self):
        """
        Fetch_one is preferable...
        Reads as single value from the k2000's buffer. Use after prepare_measure_one initially
        read_one for each value. This does not need a trigger command

        :returns: voltage value
        :rtype: float
        """
        data = np.array([self.k2000.query_ascii_values('read?')])
        return data[0][0]

    def measure_one(self):
        """
        Use this after prepare_measure_one. Triggers and reads the value in one call (slower)

        :returns: voltage value
        :rtype: float
        """
        data = np.array([self.k2000.query_ascii_values('meas?')])
        return data[0][0]

    def fetch_one(self):
        """
        Fetches the latest measurement. Use after prepare_measure_one initially then trigger and
        fetch_one for each value. This is faster than read_one

        :returns: voltage measurement
        :rtype: float
        """
        return self.k2000.query_ascii_values('fetch?')[0]

    def close(self):
        """
        Closes the instrument connection, i.e. frees the port up for other applications/threads. Also disables output.

        :returns: None
        """
        self.k2000.close()
