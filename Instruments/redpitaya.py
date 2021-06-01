import tkinter.messagebox as mb
import winsound
import os

import numpy as np
import paramiko

__all__ = ['error_sound', 'alert_sound', 'RedPitaya']


def error_sound():
    winsound.PlaySound(os.path.abspath('Windows Background.wav'), winsound.SND_FILENAME)


def alert_sound():
    winsound.PlaySound(os.path.abspath('Windows Notify System Generic.wav'), winsound.SND_FILENAME)


class RedPitaya:

    # Connects to RP using IP address (192.168.0.11)
    def connect(self, IP):
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

    # initiates a measurement and then reads the buffer
    def get_data(self, tracelen, numavgs, dec, trig):

        datacmd = f'/root/ASOPS/trig_stu.o {tracelen} {numavgs} {dec} {trig}'
        stdin, stdout, stderr = self.ssh.exec_command(datacmd)
        t = str(stdout.readlines())
        if 'no trig' in t:
            error_sound()
            raise RuntimeError('No trigger detected')
            return

        self.sftp.get('data', 'data')

        file = open("data", "rb")
        a = np.mean(np.fromfile(file, dtype=np.int16).reshape(int(numavgs), tracelen), 0)
        file.close()
        # print(a.shape)
        return a

    # closes connection
    def close(self):
        # This function is almost useless tbh. The close call has a try and except inside it already so if it isn't
        # open it doesn't show any error anyway. It is easier to type self.rp.close() in the GUI calls though.
        self.ssh.close()
