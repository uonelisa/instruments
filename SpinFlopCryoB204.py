import Instruments
import matplotlib
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import threading
import queue
import time
import numpy as np
from tkinter import filedialog as dialog

matplotlib.use('Qt5Agg')


def save(data, header):
    name = dialog.asksaveasfilename(title='Save data')
    if name:  # if a name was entered, don't save otherwise
        if name[-4:] != '.txt':  # add .txt if not already there
            name = f'{name}.txt'
        np.savetxt(name, data, header=header, newline='\r\n', delimiter='\t')  # save
        print(f'Data saved as {name}')
    else:
        print('Data not saved')


class Plotter:
    """
    no way to save data after completion.
    """

    def __init__(self, source_meter_port, dmm_port, meas_curr, source_volt_range, dmm_volt_range, max_time):
        self.source_volt_range = source_volt_range
        self.dmm_volt_range = dmm_volt_range
        self.max_time = max_time
        self.source_meter = Instruments.K2400()
        self.dmm = Instruments.K2000()
        self.dmm.connect(dmm_port)
        self.source_meter.connect(source_meter_port)
        self.current = meas_curr
        self.plot_queue = queue.Queue()
        self._is_running = True
        threading.Thread(target=self._get_data, daemon=True).start()
        self._do_plotting()

    def _get_data(self):
        self.source_meter.prepare_measure_one(self.current, self.source_volt_range)
        self.dmm.prepare_measure_one(self.dmm_volt_range)
        self.source_meter.use_rear_io(True)
        self.source_meter.enable_output_current()
        while self._is_running:
            self.source_meter.trigger()
            self.dmm.trigger()
            t, v_xx, c = self.source_meter.fetch_one()
            v_xy = self.dmm.fetch_one()
            self.plot_queue.put((t, c, v_xx, v_xy))
            time.sleep(0.25)

    def _do_plotting(self):
        times = []
        currents = []
        v_xx_values = []
        v_xy_values = []
        r_xx_values = []
        r_xy_values = []
        fig = plt.figure()
        fig.canvas.set_window_title('Resistance Plots')
        ax_xx = fig.add_subplot(211)
        ax_xx.grid()
        ax_xx.ticklabel_format(useOffset=False)
        # plt.xlabel('Time(s)')
        plt.ylabel('R_xx (Ohms)')
        ax_xy = fig.add_subplot(212)
        ax_xy.grid()
        ax_xx.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.1f}'))
        ax_xy.ticklabel_format(useOffset=False)
        ax_xy.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.4f}'))
        plt.xlabel('Time(s)')
        plt.ylabel('R_xy (Ohms)')
        r_xx_line, = ax_xx.plot(times, r_xx_values, 'r-')
        r_xy_line, = ax_xy.plot(times, r_xy_values, 'r-')
        stop_button_axes = plt.axes([0.81, 0.05, 0.1, 0.075])
        stop_button = Button(stop_button_axes, 'Stop')
        stop_button.on_clicked(self._stop_button_callback)

        plt.show(block=False)
        while self._is_running:
            while not self.plot_queue.empty():
                t, c, v_xx, v_xy = self.plot_queue.get()
                times.append(t)
                currents.append(c)
                v_xx_values.append(v_xx)
                r_xx_values.append(v_xx / c)
                v_xy_values.append(v_xy)
                r_xy_values.append(v_xy / c)

                indices = [ind for ind, val in enumerate(times) if val > times[-1] - self.max_time]
                plot_times = [times[i] - times[0] for i in indices]
                plot_r_xx = [r_xx_values[i] for i in indices]
                plot_r_xy = [r_xy_values[i] for i in indices]

                r_xx_line.set_xdata(plot_times)
                r_xx_line.set_ydata(plot_r_xx)
                r_xy_line.set_xdata(plot_times)
                r_xy_line.set_ydata(plot_r_xy)
                ax_xx.relim()
                ax_xx.autoscale_view()
                ax_xy.relim()
                ax_xy.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
        header = "Time (s), Current (A), V_xx (V), V_xy (V)"
        data = np.column_stack((np.array(times), np.array(currents), np.array(v_xx_values), np.array(v_xy_values)))
        save(data, header)

    def _stop_button_callback(self, event):
        self._is_running = False
        self.source_meter.disable_output_current()
        self.source_meter.close()


if __name__ == '__main__':
    current = 100e-6
    source_port = 7
    dmm_port = 6
    source_volt_range = 2
    dmm_volt_range = 0.01
    max_time = 180
    plotter = Plotter(source_port, dmm_port, current, source_volt_range, dmm_volt_range, max_time)
