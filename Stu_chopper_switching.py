"""

Created on Mon 29th Apr 09:00 2019

@author: Stuart Poole - stuart.poole@nottingham.ac.uk or stuart.f.poole@gmail.com

Developed for Python 3.7

"""

import tkinter as tk
import tkinter.messagebox as mb
from tkinter import filedialog as dialog

import matplotlib
import numpy as np
import time

import instruments

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


# from numba import jit


# import warnings
# stops false warning showing when plotting
# warnings.filterwarnings("ignore", ".*GUI is implemented.*")



class GUI:

    def __init__(self, rootin):
        # self.rp = RedPitaya()
        self.sb = instruments.SwitchBox()
        self.pg = instruments.PulseGenerator()
        self.dmm = instruments.DMM()
        self.lockin = instruments.DMM()
        self.pulse_times = np.array([])


        self.window = rootin
        self.isRunning = False

        # default calibration values
        self.offset = -6.9e-3
        self.factor = 7.12e3

        # Change default values here
        num_avgs = 100
        avgs_per_loop = 2
        curr = 15


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

        pulse1_assignments = {"I+": "B", "I-": "F"}
        pulse2_assignments = {"I+": "D", "I-": "H"}
        measure_assignments = {"V1+": "C", "V1-": "G", "V2+": "B", "V2-": "D", "I+": "A", "I-": "E"}

        try:
            num_avgs = int(self.entry_avgs.get())
            num_loops = int(self.entry_nploop.get())
            current = float(self.entry_curr.get())/1000
            # trace_length = int(self.entry_len.get())

        except ValueError as error:
            instruments.error_sound()
            print("The Entries could not be read:")
            print(error)
            return

        try:
            self.pg.connect()
            print("connected to pulse generator")
        except:
            instruments.error_sound()
            print('could not connect to pulse generator')
        try:
            self.sb.connect(8)
            print("connected to switch box")
        except:
            instruments.error_sound()
            print('could not connect to switch box')
        try:
            self.dmm.connect(6, 0)
            print('connected to kiethley 2000')
        except:
            instruments.error_sound()
            print("Could not connect to k2000")
        try:
            self.lockin.connect(7, 10)
            print('connected to kiethley 2000')
        except:
            instruments.error_sound()
            print("Could not connect to k2000")

        # Attempt to load all the values from the entry boxes




        # Make figure and plot starting line and axis labels
        trace_fig = plt.figure()
        trace_ax = plt.gca()


        positive_array = np.array([])
        negative_array = np.array([])
        pos_rxy_array = np.array([])
        pos_rxx_array = np.array([])
        pos_time_array = np.array([])
        neg_rxy_array = np.array([])
        neg_rxx_array = np.array([])
        neg_time_array = np.array([])

        plt.ylabel('Signal (V)')
        pos_line, = trace_ax.plot(pos_time_array, positive_array, 'b.')
        neg_line, = trace_ax.plot(neg_time_array, negative_array, 'r.')
        plt.suptitle('Averaged Data', fontsize=20)
        # freq_diff_text = trace_fig.text(0.2, 0.88, f'Freq Diff: {frequency_diff}Hz', ha='center', va='bottom', size='large')
        # averages_text = trace_fig.text(0.9, 0.88, f'Avgs: {0}', ha='right', va='bottom', size='large')
        plt.grid()

        rxx_transport_fig = plt.figure()
        rxx_transport_ax = plt.gca()
        plt.xlabel('TIme (s)')
        plt.ylabel('Rxx (ohms)')
        rxy_transport_fig = plt.figure()
        rxy_transport_ax = plt.gca()
        plt.xlabel('TIme (s)')
        plt.ylabel('Rxy (ohms)')

        pos_rxy_line, = rxy_transport_ax.plot(pos_time_array, pos_rxy_array, 'b+')
        pos_rxx_line, = rxx_transport_ax.plot(pos_time_array, pos_rxx_array, 'b+')
        neg_rxy_line, = rxy_transport_ax.plot(neg_time_array, neg_rxy_array, 'r+')
        neg_rxx_line, = rxx_transport_ax.plot(neg_time_array, neg_rxx_array, 'r+')

        plt.show()

        n = 0
        start_time = time.time()

        self.isRunning = True
        num_r = num_avgs  # number of resistance measurements
        delay = num_avgs * 0.18
        pulse_current = current
        pulse_width = 1e-3
        probe_current = 500e-6

        while self.isRunning:
            loop_start = time.time()
            self.pulse_times = np.array([])

            try:
                # first pulse
                self.sb.switch(pulse1_assignments)
                self.pg.pulse(pulse_current, pulse_width, 0)
                self.pulse_times = np.append(self.pulse_times, time.time()-start_time)
                time.sleep(0.1)
                self.sb.switch(measure_assignments)
                time.sleep(0.05)
                self.pg.measure(probe_current, num_r)
                self.dmm.measure(num_r)
                self.lockin.measure(num_r)
                self.pg.trigger()
                self.dmm.trigger()
                self.lockin.trigger()
                time.sleep(delay)
                pos_loop_data = self.lockin.read()
                pos_time, pos_rxx = self.pg.read(num_r)
                pos_rxy = self.dmm.read()

                # second pulse
                self.sb.switch(pulse2_assignments)
                self.pg.pulse(pulse_current, pulse_width, 0)
                self.pulse_times = np.append(self.pulse_times, time.time()-start_time)
                time.sleep(0.1)
                self.sb.switch(measure_assignments)
                time.sleep(0.05)
                self.pg.measure(probe_current, num_r)
                self.dmm.measure(num_r)
                self.lockin.measure(num_r)
                self.pg.trigger()
                self.dmm.trigger()
                self.lockin.trigger()
                time.sleep(delay)
                neg_loop_data = self.lockin.read()
                neg_time, neg_rxx = self.pg.read(num_r)
                neg_rxy = self.dmm.read()

            except RuntimeError:
                self.rp.close()
                mb.showerror('Data Acquisition Error', 'No trigger or no response from multi-meters')
                return

            positive_array = (n * positive_array + pos_loop_data) / (n + 1)
            negative_array = (n * negative_array + neg_loop_data) / (n + 1)
            pos_rxx_array = (n * pos_rxx_array + pos_rxx/probe_current) / (n + 1)
            neg_rxx_array = (n * neg_rxx_array + neg_rxx/probe_current) / (n + 1)
            neg_rxy_array = (n * neg_rxy_array + neg_rxy/probe_current) / (n + 1)
            pos_rxy_array = (n * pos_rxy_array + pos_rxy/probe_current) / (n + 1)
            pos_time_array = (n * pos_time_array + pos_time) / (n + 1)
            neg_time_array = (n * neg_time_array + neg_time + np.maximum(pos_time) + 1) / (n + 1)

            # positive_array = np.append(positive_array, pos_loop_data)
            # negative_array = np.append(negative_array, neg_loop_data)
            # pos_time_array = np.append(pos_time_array, pos_time + self.pulse_times[-2])
            # neg_time_array = np.append(neg_time_array, neg_time + self.pulse_times[-1])
            # pos_rxx_array = np.append(pos_rxx_array, pos_rxx/probe_current)
            # pos_rxy_array = np.append(pos_rxy_array, pos_rxy/probe_current)
            # neg_rxx_array = np.append(neg_rxx_array, neg_rxx/probe_current)
            # neg_rxy_array = np.append(neg_rxy_array, neg_rxy/probe_current)

            temp_name = f'temp/temp{n + 1}.txt'
            np.savetxt(temp_name, np.column_stack((pos_time_array, positive_array, neg_time_array, negative_array)), newline='\r\n', delimiter='\t')
            np.savetxt(temp_name.replace('.txt', '_magnetotransport.txt'),
                       np.column_stack((pos_time_array, pos_rxx_array, pos_rxy_array, neg_time_array,
                                       neg_rxx_array, neg_rxy_array)), newline='\r\n', delimiter='\t')
            print(f'Temporary data saved as {temp_name}')
            pos_rxx_line.set_xdata(pos_time_array)
            pos_rxx_line.set_ydata(pos_rxx_array)
            pos_rxy_line.set_xdata(pos_time_array)
            pos_rxy_line.set_ydata(pos_rxy_array)

            neg_rxx_line.set_xdata(neg_time_array)
            neg_rxx_line.set_ydata(neg_rxx_array)
            neg_rxy_line.set_xdata(neg_time_array)
            neg_rxy_line.set_ydata(neg_rxy_array)

            pos_line.set_xdata(pos_time_array)
            neg_line.set_xdata(neg_time_array)
            pos_line.set_ydata(positive_array)
            neg_line.set_ydata(negative_array)

            trace_ax.relim()
            rxx_transport_ax.relim()
            rxy_transport_ax.relim()
            trace_ax.autoscale_view()
            rxx_transport_ax.autoscale_view()
            rxy_transport_ax.autoscale_view()
            trace_fig.canvas.draw()
            rxy_transport_fig.canvas.draw()
            rxx_transport_fig.canvas.draw()
            trace_fig.canvas.flush_events()
            rxy_transport_fig.canvas.flush_events()
            rxx_transport_fig.canvas.flush_events()
            self.window.update_idletasks()
            self.window.update()
            self.window.lift()

            print(f'Loop {n + 1} time: {round(time.time() - loop_start, 3)}')
            n += 1
            if n >= num_loops:
                self.isRunning = False
                self.data = np.column_stack((pos_time_array, positive_array, neg_time_array, negative_array))
                self.other_data = np.column_stack((pos_time_array, pos_rxx_array, pos_rxy_array, neg_time_array,
                                                  neg_rxx_array, neg_rxy_array))

        # Close the SSH connection and print the total time it took for that run to complete
        # self.rp.close()
        self.sb.close()
        self.pg.close()
        self.dmm.close()
        runtime = time.time() - start_time
        print(f'Total runtime is {round(runtime, 3)}')
        instruments.alert_sound()

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

    def trace_plot(self):
        plt.figure()
        plt.plot(self.data[0, :], self.data[1, :], 'r-', label="Positive")
        plt.plot(self.data[0, :], self.data[2, :], 'b-', label="Negative")
        plt.xlabel("Time")
        plt.ylabel('Signal')





root = tk.Tk()
asops_gui = GUI(root)
plt.ion()

while 1:
    root.update_idletasks()
    root.update()

