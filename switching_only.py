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
        # self.rp = RedPitaya()
        self.sb = SwitchBox()
        self.pg = PulseGenerator()
        self.dmm = DMM()
        self.pulse_times = np.array([])
        self.window = rootin
        self.isRunning = False

        # Change default values here
        num_avgs = 100
        avgs_per_loop = 10
        curr = 25
        # trace_length = 2000


        frame1 = tk.LabelFrame(self.window, text='Entries')
        frame1.grid(row=0, column=0, padx=2)

        tk.Label(frame1, text="Number of Points:").grid(row=0, column=0, sticky='E')
        tk.Label(frame1, text="Number of Loops:").grid(row=1, column=0, sticky='E')
        tk.Label(frame1, text="Pulse Current (mA):").grid(row=2, column=0, sticky='E')


        self.entry_avgs = tk.Entry(frame1)
        self.entry_avgs.insert(tk.END, str(num_avgs))
        self.entry_avgs.grid(row=0, column=1, padx=3, pady=3)

        self.entry_nploop = tk.Entry(frame1)
        self.entry_nploop.insert(tk.END, str(avgs_per_loop))
        self.entry_nploop.grid(row=1, column=1, pady=3)

        self.entry_curr = tk.Entry(frame1)
        self.entry_curr.insert(tk.END, str(curr))
        self.entry_curr.grid(row=2, column=1, pady=3)
        #
        # self.entry_diff = tk.Entry(frame1)
        # self.entry_diff.insert(tk.END, str(frequency_diff))
        # self.entry_diff.grid(row=3, column=1, pady=3)
        # self.diff = float(self.entry_diff.get())

        frame3 = tk.LabelFrame(self.window, text='Other Functions')
        frame3.grid(row=1, column=1, padx=2)

        tk.Button(frame3, text='Plot Averaged Trace', command=self.trace_plot, width=20).grid(row=2, column=0, padx=5,
                                                                                              pady=2)
        tk.Button(frame3, text='Save Data', command=self.save, width=20).grid(row=3, column=0, padx=5, pady=2)

        # # Start/stop buttons
        frame4 = tk.LabelFrame(self.window, relief='flat')
        frame4.grid(row=1, column=0, padx=2)

        tk.Button(frame4, text='RUN', command=self.start, width=25, height=2).grid(row=0, column=0, pady=10)
        tk.Button(frame4, text='ABORT', command=self.stop, width=25, height=2).grid(row=1, column=0, pady=10)

    def start(self):
        print("start")
        try:
            num_avgs = int(self.entry_avgs.get())
            num_loops = int(self.entry_nploop.get())
            pulse_current = float(self.entry_curr.get())/1000
            print(f'Current: {pulse_current}')
            # trigger_level = float(self.entry_trig.get())
        except ValueError as error:
            error_sound()
            print("The Entries could not be read:")
            print(error)
            return
        try:
            self.pg.connect()
            print("connected to pulse generator")
        except:
            error_sound()
            print('could not connect to pulse generator')
        try:
            self.sb.connect(8)
            print("connected to switch box")
        except:
            error_sound()
            print('could not connect to switch box')
        try:
            self.dmm.connect(15, 0)
            print('connected to kiethley 2000')
        except:
            error_sound()
            print("Could not connect to k2000")

        pulse1_assignments = {"I+": "B", "I-": "F"}
        pulse2_assignments = {"I+": "D", "I-": "H"}
        measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}
        # Make figure and plot starting line and axis labels

        pos_rxy_array = np.array([])
        pos_rxx_array = np.array([])
        pos_time_array = np.array([])
        neg_rxy_array = np.array([])
        neg_rxx_array = np.array([])
        neg_time_array = np.array([])

        rxx_transport_fig = plt.figure()
        rxx_transport_ax = plt.gca()
        plt.xlabel('TIme (s)')
        plt.ylabel('Rxx (ohms)')
        plt.grid()
        rxy_transport_fig = plt.figure()
        rxy_transport_ax = plt.gca()
        plt.xlabel('TIme (s)')
        plt.ylabel('Rxy (ohms)')
        plt.grid()

        pos_rxy_line, = rxy_transport_ax.plot(pos_time_array, pos_rxy_array, 'b+')
        pos_rxx_line, = rxx_transport_ax.plot(pos_time_array, pos_rxx_array, 'b+')
        neg_rxy_line, = rxy_transport_ax.plot(neg_time_array, neg_rxy_array, 'r+')
        neg_rxx_line, = rxx_transport_ax.plot(neg_time_array, neg_rxx_array, 'r+')

        plt.show()

        n = 0
        start_time = time.time()

        self.isRunning = True
        num_r = num_avgs  # number of resistance measurements
        delay = num_avgs * 0.20
        # pulse_current = 25e-3
        pulse_width = 1e-3
        probe_current = 1000e-6

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
                time.sleep(delay)
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
                time.sleep(delay)
                neg_time, neg_rxx = self.pg.read(num_r)
                neg_rxy = self.dmm.read()

            except RuntimeError:
                self.sb.close()
                self.pg.close()
                self.dmm.close()
                mb.showerror('Data Acquisition Error', 'No trigger or no response from multi-meters')
                return

            # try:
            #     # pos_loop_data = (pos_loop_data / self.factor) - self.offset
            #     # neg_loop_data = (neg_loop_data / self.factor) - self.offset
            #     positive_array = (n * positive_array + pos_loop_data) / (n + 1)
            #     negative_array = (n * negative_array + neg_loop_data) / (n + 1)
            #     current_avgs = avgs_per_loop * (n + 1)
            # except IndexError:
            #     print("Index error occurred, trying again until it works")
            #     continue
            # except:
            #     error_sound()
            #     print("exception occurred outside of expected issues. Check command window for last saved file.")
            #     raise Exception
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
            np.savetxt(temp_name.replace('.txt', '_magnetotransport.txt'),
                       np.column_stack((pos_time_array, pos_rxx_array, pos_rxy_array, neg_time_array,
                                       neg_rxx_array, neg_rxy_array)), newline='\r\n', delimiter='\t')
            print(f'Temporary data saved as {temp_name}')

            # averages_text.set_text(f'Avgs: {current_avgs}')
            rxx_transport_ax.relim()
            rxx_transport_ax.autoscale_view()
            rxy_transport_ax.relim()
            rxy_transport_ax.autoscale_view()
            rxy_transport_fig.canvas.flush_events()
            rxy_transport_fig.canvas.draw()
            rxx_transport_fig.canvas.flush_events()
            rxx_transport_fig.canvas.draw()
            self.window.update_idletasks()
            self.window.update()
            self.window.lift()

            print(f'Loop {n + 1} time: {round(time.time() - loop_start, 3)}')
            n += 1
            if n >= num_loops:
                self.isRunning = False
                self.other_data = np.column_stack((pos_time_array, pos_rxx_array, pos_rxy_array, neg_time_array,
                                                  neg_rxx_array, neg_rxy_array))

        # Close the SSH connection and print the total time it took for that run to complete
        # self.rp.close()
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
            # np.savetxt(name.replace('.txt', '_pulse_times.txt'), self.pulse_times, newline='\r\n', delimiter='\t')
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
        plt.plot(self.other_data[0, :], self.other_data[2, :], 'r-', label="Positive")
        plt.plot(self.other_data[3, :], self.otherdata[5, :], 'b-', label="Negative")
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
        # print(self.k2400.query('trac:act? "defBuffer1"'))
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

    def connect(self, port, range):
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
        self.k2000.write(f'sens:volt:rang {range}')# auto-raging


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

