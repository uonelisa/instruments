"""

Created on Mon 29th Apr 09:00 2019

@author: Stuart Poole - stuart.poole@nottingham.ac.uk or stuart.f.poole@gmail.com

Developed for Python 3.7

"""

import numpy as np
import time
import tkinter as tk
import tkinter.messagebox as mb
from tkinter import filedialog as dialog
import paramiko
import visa
import os
import winsound
import matplotlib
import serial
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


# from numba import jit


# import warnings
# stops false warning showing when plotting
# warnings.filterwarnings("ignore", ".*GUI is implemented.*")


def error_sound():
    winsound.Beep(880, 200)
    winsound.Beep(440, 200)


def alert_sound():
    winsound.Beep(440, 200)
    winsound.Beep(660, 200)
    winsound.Beep(880, 200)


class GUI:

    def __init__(self, rootin):
        self.rp = RedPitaya()
        self.sb = SwitchBox()
        self.pg = PulseGenerator()
        self.dmm = DMM()
        self.pulse_times = np.array([])


        self.window = rootin
        self.isRunning = False

        # default calibration values
        self.offset = -6.9e-3
        self.factor = 7.12e3

        # Change default values here
        num_avgs = 300000
        avgs_per_loop = 20000
        trace_length = 2000
        frequency_diff = 800
        trigger_level = 1
        bias_voltage = 0
        self.data = np.zeros((trace_length, 3))

        frame1 = tk.LabelFrame(self.window, text='Entries')
        frame1.grid(row=0, column=0, padx=2)

        tk.Label(frame1, text="Number of averages:").grid(row=0, column=0, sticky='E')
        tk.Label(frame1, text="Averages per loop:").grid(row=1, column=0, sticky='E')
        tk.Label(frame1, text="Trace length (samples):").grid(row=2, column=0, sticky='E')
        tk.Label(frame1, text="Difference Setpoint (Hz):").grid(row=3, column=0, sticky='E')
        tk.Label(frame1, text="Trigger level (V):").grid(row=4, column=0, sticky='E')
        tk.Label(frame1, text="Bias voltage (V):").grid(row=5, column=0, sticky='E')

        self.entry_avgs = tk.Entry(frame1)
        self.entry_avgs.insert(tk.END, str(num_avgs))
        self.entry_avgs.grid(row=0, column=1, padx=3, pady=3)

        self.entry_nploop = tk.Entry(frame1)
        self.entry_nploop.insert(tk.END, str(avgs_per_loop))
        self.entry_nploop.grid(row=1, column=1, pady=3)

        self.entry_len = tk.Entry(frame1)
        self.entry_len.insert(tk.END, str(trace_length))
        self.entry_len.grid(row=2, column=1, pady=3)

        self.entry_diff = tk.Entry(frame1)
        self.entry_diff.insert(tk.END, str(frequency_diff))
        self.entry_diff.grid(row=3, column=1, pady=3)
        self.diff = float(self.entry_diff.get())

        self.entry_trig = tk.Entry(frame1)
        self.entry_trig.insert(tk.END, str(trigger_level))
        self.entry_trig.grid(row=4, column=1, pady=3)

        self.entry_bias = tk.Entry(frame1)
        self.entry_bias.insert(tk.END, str(bias_voltage))
        self.entry_bias.grid(row=5, column=1, pady=3)

        frame2 = tk.LabelFrame(self.window, text='Options')
        frame2.grid(row=0, column=1, padx=2)

        self.decimation_var = tk.IntVar()
        self.decimation_var.set(8)
        tk.Label(frame2, text="Decimaton level:").grid(row=0, column=0, sticky='E')
        tk.Radiobutton(frame2, text="1", variable=self.decimation_var, value=1).grid(row=0, column=1, sticky='W')
        tk.Radiobutton(frame2, text="8", variable=self.decimation_var, value=8).grid(row=0, column=2, sticky='W')

        self.scaling_var = tk.IntVar()
        self.scaling_var.set(1)
        tk.Label(frame2, text="Frequency scaling:").grid(row=1, column=0, sticky='E')
        tk.Radiobutton(frame2, text="Off", variable=self.scaling_var, value=0).grid(row=1, column=1, sticky='W')
        tk.Radiobutton(frame2, text="On", variable=self.scaling_var, value=1).grid(row=1, column=2, sticky='W')

        self.bias_var = tk.IntVar()
        self.bias_var.set(0)
        tk.Label(frame2, text="Bias voltage mode:").grid(row=2, column=0, sticky='E')
        tk.Radiobutton(frame2, text="Off", variable=self.bias_var, value=0).grid(row=2, column=1, sticky='W')
        tk.Radiobutton(frame2, text="On", variable=self.bias_var, value=1).grid(row=2, column=2, sticky='W')

        frame3 = tk.LabelFrame(self.window, text='Other Functions')
        frame3.grid(row=1, column=1, padx=2)

        tk.Button(frame3, text='Calibrate Red Pitaya', command=self.calib, width=20).grid(row=0, column=0, padx=5,
                                                                                          pady=2)
        tk.Button(frame3, text='Open Manual', command=self.manual, width=20).grid(row=1, column=0, padx=5, pady=2)

        tk.Button(frame3, text='Plot Averaged Trace', command=self.trace_plot, width=20).grid(row=2, column=0, padx=5,
                                                                                              pady=2)
        tk.Button(frame3, text='Save Data', command=self.save, width=20).grid(row=3, column=0, padx=5, pady=2)

        # tk.Button(frame3, text='Plot Power Spectrum', command=self.fft_plot, width=20).grid(row=4, column=0, padx=5,
        #                                                                                     pady=2)

        # deprecated by constfreq.py
        # tk.Button(frame3, text='Plot Freq Difference', command=self.diffs_plot, width=20).grid(row=5, column=0,
        #                                                                                        padx=5, pady=2)

        # # Start/stop buttons
        frame4 = tk.LabelFrame(self.window, relief='flat')
        frame4.grid(row=1, column=0, padx=2)

        tk.Button(frame4, text='RUN', command=self.start, width=25, height=2).grid(row=0, column=0, pady=10)
        tk.Button(frame4, text='ABORT', command=self.stop, width=25, height=2).grid(row=1, column=0, pady=10)

    def start(self):
        print("start")
        try:
            self.rp.connect()
            print("connected to red pitaya")
        except:
            error_sound()
            self.rp.close()
            print('couldnt connect to red pitaya')
        try:
            self.pg.connect()
            print("connected to pulse generator")
        except:
            error_sound()
            print('could not connect to pulse generator')
        try:
            self.sb.connect(5)
            print("connected to switch box")
        except:
            error_sound()
            print('could not connect to switch box')
        try:
            self.dmm.connect(4)
            print('connected to kiethley 2000')
        except:
            error_sound()
            print("Could not connect to k2000")

        # Attempt to load all the values from the entry boxes
        try:
            num_avgs = int(self.entry_avgs.get())
            avgs_per_loop = int(self.entry_nploop.get())
            trigger_level = float(self.entry_trig.get())
            trace_length = int(self.entry_len.get())
            frequency_diff = int(self.entry_diff.get())
            bias_check = self.bias_var.get()
            bias_voltage = int(self.entry_bias.get()) * 2
            scale_check = self.scaling_var.get()
            decimation_level = self.decimation_var.get()
        except ValueError as error:
            error_sound()
            print("The Entries could not be read:")
            print(error)
            return
        try:
            pump = float(np.loadtxt("Laser_Frequency.txt"))
        except IOError:
            print("Could not find Laser_Frequency.txt. Using default pump value of 80MHz")
            pump = 80e6
        #
        # gencmdon = f'ASOPS/gen 1 0.0 1000 sine {self.bvolt}'
        # gencmdoff = f'ASOPS/gen 1 0.0 1000 sine 0'
        est_time = round(num_avgs / (2 * frequency_diff) / 60, 2)
        est_loop_time = round(avgs_per_loop / (2 * frequency_diff), 2)
        # TODO: This needs to be measured and edited to fit
        print(f'Estimated run time: {est_time} min Estimated loop time: {est_loop_time} s')
        # if not mb.askyesno("Time Estimate",
        #                    f'Estimated run time: {est_time} min\nEstimated loop time: {est_loop_time} s\n\nStart run?'):
        #     return

        # the end condition (number of loops * number of runs (usually 1)
        end = (self.bias_var.get() + 1) * int(num_avgs / avgs_per_loop)
        pulse1_assignments = {"I+": "B", "I-": "F"}
        pulse2_assignments = {"I+": "D", "I-": "H"}
        measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}
        # Make figure and plot starting line and axis labels
        trace_fig = plt.figure()
        trace_ax = plt.gca()
        if scale_check:
            # calculate the length of the trace in scaled time given the dac has a rate of 125MHz
            # total trace time = (period of sampling * number of samples * scaled time per sample)
            # time_axis_max = (decimation_level  * trace_length * 125e-6) * (frequency_diff / pump)
            time_axis_max = (decimation_level / 125e6) / (pump / frequency_diff) * trace_length
            time_array = np.linspace(0, time_axis_max, trace_length)
            print(time_axis_max)
            plt.xlabel('Time (ns)')
        else:
            time_array = np.arange(0, trace_length)
            plt.xlabel('Time (samples)')

        positive_array = np.zeros(trace_length)
        negative_array = np.zeros(trace_length)
        plt.ylabel('Signal (V)')
        pos_line, = trace_ax.plot(time_array * 1e9, positive_array, 'b.')
        neg_line, = trace_ax.plot(time_array * 1e9, negative_array, 'r.')
        plt.suptitle('Averaged Data', fontsize=20)
        freq_diff_text = trace_fig.text(0.2, 0.88, f'Freq Diff: {frequency_diff}Hz', ha='center', va='bottom', size='large')
        averages_text = trace_fig.text(0.9, 0.88, f'Avgs: {0}', ha='right', va='bottom', size='large')
        plt.grid()

        rxx_transport_fig = plt.figure()
        rxx_transport_ax = plt.gca()
        plt.xlabel('TIme (s)')
        plt.ylabel('Rxx (ohms)')
        rxy_transport_fig = plt.figure()
        rxy_transport_ax = plt.gca()
        plt.xlabel('TIme (s)')
        plt.ylabel('Rxy (ohms)')
        pos_rxy_array = np.array([])
        pos_rxx_array = np.array([])
        pos_time_array = np.array([])
        neg_rxy_array = np.array([])
        neg_rxx_array = np.array([])
        neg_time_array = np.array([])
        pos_rxy_line, = rxy_transport_ax.plot(pos_time_array, pos_rxy_array, 'b+')
        pos_rxx_line, = rxx_transport_ax.plot(pos_time_array, pos_rxx_array, 'b+')
        neg_rxy_line, = rxy_transport_ax.plot(neg_time_array, neg_rxy_array, 'r+')
        neg_rxx_line, = rxx_transport_ax.plot(neg_time_array, neg_rxx_array, 'r+')

        plt.show()

        n = 0
        start_time = time.time()

        self.isRunning = True
        num_r = 75  # number of resistance measurements
        pulse_current = 32e-3
        pulse_width = 1e-3
        probe_current = 500e-6

        while self.isRunning:
            loop_start = time.time()
            self.pulse_times = np.array([])

            try:
                # first pulse
                self.sb.switch(pulse1_assignments)
                # time.sleep(0.1)
                self.pg.pulse(pulse_current, pulse_width, 0)
                self.pulse_times = np.append(self.pulse_times, time.time()-start_time)
                time.sleep(0.1)
                self.sb.switch(measure_assignments)
                time.sleep(0.05)
                # time.sleep(2)
                self.pg.measure(probe_current, num_r)
                self.dmm.measure(num_r)
                self.pg.trigger()
                self.dmm.trigger()
                pos_loop_data = self.rp.get_data(trace_length, avgs_per_loop / decimation_level, decimation_level, trigger_level)
                pos_time, pos_rxx = self.pg.read(num_r)
                pos_rxy = self.dmm.read()

                # second pulse
                self.sb.switch(pulse2_assignments)
                # time.sleep(0.1)
                self.pg.pulse(pulse_current, pulse_width, 0)
                self.pulse_times = np.append(self.pulse_times, time.time()-start_time)
                time.sleep(0.1)
                self.sb.switch(measure_assignments)
                time.sleep(0.05)
                # time.sleep(2)
                self.pg.measure(probe_current, num_r)
                self.dmm.measure(num_r)
                self.pg.trigger()
                self.dmm.trigger()
                neg_loop_data = self.rp.get_data(trace_length, avgs_per_loop / decimation_level, decimation_level, trigger_level)
                neg_time, neg_rxx = self.pg.read(num_r)
                neg_rxy = self.dmm.read()

            except RuntimeError:
                self.rp.close()
                mb.showerror('Data Acquisition Error', 'No trigger or no response from multi-meters')
                return

            try:
                pos_loop_data = (pos_loop_data / self.factor) - self.offset
                neg_loop_data = (neg_loop_data / self.factor) - self.offset
                positive_array = (n * positive_array + pos_loop_data) / (n + 1)
                negative_array = (n * negative_array + neg_loop_data) / (n + 1)
                current_avgs = avgs_per_loop * (n + 1)
            except IndexError:
                print("Index error occurred, trying again until it works")
                continue
            except:
                error_sound()
                print("exception occurred outside of expected issues. Check command window for last saved file.")
                raise Exception

            pos_time_array = np.append(pos_time_array, pos_time + self.pulse_times[-2])
            neg_time_array = np.append(neg_time_array, neg_time + self.pulse_times[-1])
            #
            # pos_time_array = np.append(pos_time_array, pos_time)
            # neg_time_array = np.append(neg_time_array, neg_time )
            pos_rxx_array = np.append(pos_rxx_array, pos_rxx/probe_current)
            pos_rxy_array = np.append(pos_rxy_array, pos_rxy/probe_current)
            neg_rxx_array = np.append(neg_rxx_array, neg_rxx/probe_current)
            neg_rxy_array = np.append(neg_rxy_array, neg_rxy/probe_current)

            pos_rxx_line.set_xdata(pos_time_array)
            pos_rxx_line.set_ydata(pos_rxx_array)
            pos_rxy_line.set_xdata(pos_time_array)
            pos_rxy_line.set_ydata(pos_rxy_array)

            neg_rxx_line.set_xdata(neg_time_array)
            neg_rxx_line.set_ydata(neg_rxx_array)
            neg_rxy_line.set_xdata(neg_time_array)
            neg_rxy_line.set_ydata(neg_rxy_array)

            temp_name = f'temp/temp{n + 1}.txt'
            np.savetxt(temp_name, np.column_stack((time_array, positive_array, negative_array)), newline='\r\n', delimiter='\t')
            np.savetxt(temp_name.replace('.txt', '_magnetotransport.txt'),
                       np.column_stack((pos_time_array, pos_rxx_array, pos_rxy_array, neg_time_array,
                                       neg_rxx_array, neg_rxy_array)), newline='\r\n', delimiter='\t')
            print(f'Temporary data saved as {temp_name}')

            pos_line.set_ydata(positive_array)
            neg_line.set_ydata(negative_array)
            averages_text.set_text(f'Avgs: {current_avgs}')
            trace_ax.relim()
            trace_ax.autoscale_view()
            trace_fig.canvas.flush_events()
            rxx_transport_ax.relim()
            rxx_transport_ax.autoscale_view()
            rxy_transport_ax.relim()
            rxy_transport_ax.autoscale_view()
            rxy_transport_fig.canvas.flush_events()
            rxx_transport_fig.canvas.flush_events()
            self.window.update_idletasks()
            self.window.update()
            # self.window.lift()

            print(f'Loop {n + 1} time: {round(time.time() - loop_start, 3)}')
            n += 1
            if n >= end:
                self.isRunning = False
                self.data = np.column_stack((time_array, positive_array, negative_array))
                self.other_data = np.column_stack((pos_time_array, pos_rxx_array, pos_rxy_array, neg_time_array,
                                                  neg_rxx_array, neg_rxy_array))

        # Close the SSH connection and print the total time it took for that run to complete
        self.rp.close()
        self.sb.close()
        self.pg.close()
        self.dmm.close()
        runtime = time.time() - start_time
        print(f'Total runtime is {round(runtime, 3)}')
        alert_sound()

        # Save data to txt file if desired
        if mb.askyesno('Run Completed!', 'Save data?'):
            self.save()
        else:
            print('Data not saved. ')

    def save(self):
        name = dialog.asksaveasfilename(title='Save')
        if name:  # if a name was entered, don't save otherwise
            if name[-4:] != '.txt':  # add .txt if not already there
                name = f'{name}.txt'
            np.savetxt(name, self.data, newline='\r\n', delimiter='\t')  # save
            np.savetxt(name.replace('.txt', '_pulse_times.txt'), self.pulse_times, newline='\r\n', delimiter='\t')
            np.savetxt(name.replace('.txt', '_magnetoTransport.txt'), self.other_data, newline='\r\n', delimiter='\t')
            print(f'Data saved as {name}')
        else:
            print('Data not saved')

    def stop(self):
        # stops the code and allows safe exit
        # print("Code stopped. Look in the command line for the last temporary file if you want to save it.")
        self.isRunning = False
        try:
            self.rp.close()
        except:
            return

    def manual(self):
        os.startfile('C:/Users/physicsuser/Documents/python/Manual.txt')
        # TODO: point this to the actual manual file.... also read that.

    def trace_plot(self):
        plt.figure()
        plt.plot(self.data[0, :], self.data[1, :], 'r-', label="Positive")
        plt.plot(self.data[0, :], self.data[2, :], 'b-', label="Negative")
        plt.xlabel("Time")
        plt.ylabel('Signal')

    def calib(self):
        def run_calib():
            # Check to see if vpp entry is valid, as well as trigger level
            try:
                vpp = float(entryc.get())
            except:
                error_sound()
                mb.showerror('Entry Error', 'Invalid entry for vpp')
                return
            if vpp <= 0:
                error_sound()
                mb.showerror('Entry Error', 'Invalid value for vpp\nMust be greater than 0')
                return

            try:
                v = float(entryvc.get())
            except:
                mb.showerror('Entry Error', 'Invalid entry for trigger level')
                return
            if v <= 0 or v > 1:
                error_sound()
                mb.showerror('Entry Error', 'Invalid value for trigger level\nMust be between 0 and 1')
                return

            # Connect to red pitaya, and get 125 full-length traces at
            # decimation 8 (1000 averages)
            try:
                self.RpConnect('192.168.0.11', 22, 'root', 'root')
            except:
                error_sound()
                mb.showerror('Connection Error', 'Couldn\'t connect to Red Pitaya')
                return
            try:
                averaged_data = self.GetData(16383, 125, 8, v)
            except RuntimeError:
                self.Close()
                error_sound()
                mb.showerror('Trigger Error', 'No trigger detected after 2 seconds')
                return

                # Calculate the scale factor and offset
            self.factor = (max(averaged_data) - min(averaged_data)) / vpp
            dataavgf = averaged_data / self.factor
            self.offset = (max(dataavgf) + min(dataavgf)) / 2
            dataavgc = dataavgf - self.offset
            print('Calibration completed')
            print(f'Scale factor is {round(self.factor, 3)}, dc offset is {round(self.offset, 3)}')

            # Plot calibrated and non-calibrated data
            plt.figure()
            plt.plot(dataavgc)
            plt.suptitle('Calibrated data')
            plt.figure()
            plt.plot(averaged_data)
            plt.suptitle('Non-calibrated data')
            self.stop()
            window.destroy()

        # Create new window with entry box
        window = tk.Toplevel()
        window.title('Calibration')
        window.focus_set()
        tk.Label(window, text="Enter peak-to-peak amplitude of signal (V):").grid(row=0, column=0, padx=5, pady=2)
        entryc = tk.Entry(window)
        entryc.grid(row=1, column=0, padx=5, pady=2)
        tk.Label(window, text="Enter trigger level (V):").grid(row=2, column=0, padx=5, pady=2)
        entryvc = tk.Entry(window)
        entryvc.grid(row=3, column=0, padx=5, pady=2)
        tk.Button(window, text='RUN', command=run_calib, width=10).grid(row=4, column=0, padx=5, pady=2)


class RedPitaya:

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # The static IP on the UoN Network is "10.156.65.153". Direct connect is 192.168.0.11.
        try:
            self.ssh.connect('192.168.0.11', port=22, username='root', password='root')
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

    def close(self):
        # This function is almost useless tbh. The close call has a try and except inside it already so if it isn't
        # open it doesn't show any error anyway. It is easier to type self.rp.close() in the GUI calls though.
        self.ssh.close()


class PulseGenerator:

    def connect(self):
        rm = visa.ResourceManager('@ni')
        # self.k2400 = serial.Serial("COM%d" % port, 38400, 8, timeout=1)
        self.k2400 = rm.open_resource('USB0::0x05E6::0x2461::04121022::INSTR')
        self.k2400.timeout = 12000
        print(self.k2400.query('*IDN?'))
        # self.k2400.write(':SYST:BEEP:STAT OFF')
        self.k2400.write(':*RST')
        self.k2400.write('sour:func curr')
        self.k2400.write('sens:func "volt"')
        self.k2400.write('sens:volt:rang:auto on')
        self.k2400.write(f'trac:make "defBuffer1", {10000}')

    def pulse(self, current, width, delay):
        # self.k2400.write('sour:func "curr"')
        # self.k2400.write('sens:func "volt"')
        # self.k2400.write('sens:volt:rang:auto on')
        # self.k2400.write('sour:curr:vlim ')
        self.k2400.write('sens:volt:rsen off')
        self.k2400.write(':FORM:ASC:PREC 16')
        # self.k2400.write(f'sour:puls:tr:curr 0, {current}, {width}, 1, off, "defbuffer1", {delay}, 0, 5, 5')
        self.k2400.write(f'SOUR:PULS:SWE:CURR:LIN 0, 0, {current}, 2, {width}, off, "defbuffer1", 0, 0, 1, 30, 30, off, off')
        self.k2400.write('INIT')        # self.k2400.write(f':READ?')
        self.k2400.write('*WAI')


    def measure(self, current, num):
        # self.k2400.write('sour:func curr')
        self.k2400.write('sour:curr:rang 200e-6')
        self.k2400.write(f'sour:curr {current}')

        # self.k2400.write('sour:curr:vlim 1')
        self.k2400.write('sens:volt:rsen on')
        self.k2400.write(f'sens:volt:nplc 2')
        self.k2400.write('sens:volt:rang:auto on')

        self.k2400.write(f'trig:load "SimpleLoop", {num}, 0, "defBuffer1"')
        self.k2400.write('outp on')

    def trigger(self):
        self.k2400.write('init')
        self.k2400.write('*wai')

    def read(self, num):
        self.k2400.write('outp off')
        print(self.k2400.query('trac:act? "defBuffer1"'))
        try:
            data = np.array(self.k2400.query_ascii_values(f'trac:data? 1, {num}, "defBuffer1", read, rel'))
            t = data[1::2]
            d = data[0::2]
            return t, d
        except:
            print('could not read data from k2400')
            return np.array([]), np.array([])

    def close(self):
        self.k2400.write('*RST')
        self.k2400.write('*SRE 0')
        self.k2400.write('outp off')
        self.k2400.close()


class SwitchBox:
    def __init__(self):
        self.start_byte = 'FE'
        self.clear_byte = '10'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'
        self.binary_dictionary = {"A": '00', "B": '01', "C": '02', "D": '03', "E": '04', "F": '05', "G": '06', "H": '07',
                                  "V1+": '20', "V1-": '10', "V2+": '08', "V2-": '04', "I+": '02', "I-": '01', "0": '00',
                                  "": '00'}

    def connect(self, port):
        self.sb = serial.Serial(f'COM{port}', 57600, 8)
        self.sb.close()
        self.sb.open()
        self.clear()

    def switch(self, assignments):

        #     this will be called with a desired arrangement and will call make_command if it seems necessary
        self.clear()
        for x, y in assignments.items():
            for char in y:
                self.sb.write(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                               self.stop_byte))
                # print(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                #                self.stop_byte))
        self.refresh()

    def close(self):
        self.clear()
        self.refresh()
        self.sb.close()

    def refresh(self):
        # sends command to turn off all channels
        self.sb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def clear(self):
        self.sb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()

class DMM:
    def __init__(self):
        self.buffer_length = 500

    def connect(self, port):
        rm = visa.ResourceManager('@ni')
        self.k2000 = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.k2000.close()

        self.k2000.open()
        self.k2000.baud_rate = 19200
        self.k2000.timeout = 12000
        self.k2000.write_termination = '\r\n'
        self.k2000.read_termination = '\r\n'
        self.k2000.write('*rst')
        self.k2000.write('*cls')

        print(self.k2000.query('*IDN?'))
        # self.k2000.write('*rst')  # reset
        # k2000.write('disp:enab off')
         # clear system
        self.k2000.write('sens:func "volt"')  # measure volts
        self.k2000.write(
            'sens:volt:nplc 2')  # level of averaging min, 0.01 -> 10 ish Power line cycle: 50hz 2-> 25hz measurement
        self.k2000.write('sens:volt:rang 0')# auto-raging


    def close(self):
        self.k2000.close()

    def measure(self, num):
        self.k2000.write(f'trig:count {num}')  # number of points to measure
        self.k2000.write('trac:clear')  # clear buffer
        self.k2000.write(f'trac:poin {num}')  # size of buffer
        self.k2000.write('trac:feed sens')  # what goes in buffer
        self.k2000.write('trac:feed:cont next')  # doesn't overwrite previous data until full
        # self.k2000.write('init')

    def trigger(self):
        self.k2000.write('init')
        self.k2000.write('*wai')

    def read(self):
        # self.k2000.write('form:data ASCII')  #  read doesn't work without this line ?
        data = self.k2000.query_ascii_values('trac:data?')

        data = np.array(data)

        return data



root = tk.Tk()
asops_gui = GUI(root)
plt.ion()

while 1:
    root.update_idletasks()
    root.update()

