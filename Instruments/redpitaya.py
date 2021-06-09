import tkinter.messagebox as mb

import os

import numpy as np
import paramiko
from .sounds import *

__all__ = ['RedPitaya']


class RedPitaya:
    """
    Class to control the red pitaya used in ASOPS in B314. Not useful for much else since it interacts with the embedded
    software
    """

    def connect(self, IP='192.168.0.11'):
        """
        Connects to Red Pitaya using IP address (192.168.0.11) by default

        :param str IP: IP address of the red pitaya

        :returns: None
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # The static IP on the UoN Network is "10.156.65.153". Direct connect is 192.168.0.11.
        try:
            self.ssh.connect(f'{IP}', port=22, username='root', password='root')
        except:
            error_sound()
            mb.showerror('SSH error', 'Could not connect to Red Pitaya')
            self.close()

        fpgacmd = 'cat /opt/redpitaya/fpga/fpga_0.94.bit > /dev/xdevcfg'
        stdin, stdout, stderr = self.ssh.exec_command(fpgacmd)
        stdout.readlines()  # makes sure that command completes before continuing
        avgcmd = 'monitor 0x40100028 1'
        stdin, stdout, stderr = self.ssh.exec_command(avgcmd)
        stdout.readlines()

        # Open SFTP client to download data from Red Pitaya to computer
        self.sftp = self.ssh.open_sftp()

    def get_data(self, tracelen, numavgs, dec, trig):
        """
        initiates a measurement and then reads the buffer
        :param int tracelen: number of points per trace
        :param int numavgs: number of traces to average together
        :param int dec: decimation level (1 or 8)
        :param float trig: trigger level threshold (1V is almost always used)

        :returns: meaned array of voltages of length "tracelen"
        :rtype: np.ndarray
        """

        datacmd = f'/root/ASOPS/trig_stu.o {tracelen} {numavgs} {dec} {trig}'
        stdin, stdout, stderr = self.ssh.exec_command(datacmd)
        t = str(stdout.readlines())
        if 'no trig' in t:
            error_sound()
            raise RuntimeError('No trigger detected')

        self.sftp.get('data', 'data')

        file = open("data", "rb")
        a = np.mean(np.fromfile(file, dtype=np.int16).reshape(int(numavgs), tracelen), 0)
        file.close()
        # print(a.shape)
        return a

    def close(self):
        """
        Closes connection to the instrument
        :returns: None
        """
        self.ssh.close()
