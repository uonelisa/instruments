import Instruments
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import threading
import queue
import time

matplotlib.use('Qt5Agg')

class Plotter:
    """
    no way to save data after completion.
    """

    def __init__(self, current, max_time):
        self.max_time = max_time
        self.source_meter = Instruments.K2400()
        self.source_meter.connect(7)

        self.plot_queue = queue.Queue()
        self._is_running = True
        threading.Thread(target=self.get_data, daemon=True).start()
        self.do_plotting()

    def get_data(self):
        self.source_meter.prepare_measure_one(current)
        self.source_meter.use_rear_io(True)
        self.source_meter.enable_output_current()
        while self._is_running:
            t, v, c = self.source_meter.read_one()
            self.plot_queue.put((t, v/c))
            time.sleep(0.25)


    def do_plotting(self):
        times = []
        resistances = []
        figure = plt.figure(1)
        plt.title("K2400 resistance plots")
        ax = figure.add_subplot(111)
        plt.xlabel('Time(s)')
        plt.ylabel('Resistance (Ohms)')
        resistance_line, = ax.plot(times, resistances, 'r-')
        stop_button_axes = plt.axes([0.81, 0.05, 0.1, 0.075])
        stop_button = Button(stop_button_axes, 'Stop')
        stop_button.on_clicked(self.stop_button_callback)
        ax.grid()
        ax.ticklabel_format(useOffset=False)
        plt.draw()
        plt.show(block=False)
        while self._is_running:
            if not self.plot_queue.empty():
                t, r = self.plot_queue.get()
                times.append(t)
                resistances.append(r)

                indices = [ind for ind, val in enumerate(times) if val > times[-1] - self.max_time]
                plot_times = [times[i]-times[0] for i in indices]
                plot_resistances = [resistances[i] for i in indices]

                resistance_line.set_xdata(plot_times)
                resistance_line.set_ydata(plot_resistances)
                ax.relim()
                ax.autoscale_view()


            figure.canvas.draw()
            figure.canvas.flush_events()

    def stop_button_callback(self, event):
        self._is_running = False
        self.source_meter.disable_output_current()
        self.source_meter.close()


if __name__ == '__main__':
    current = 100e-6
    plotter = Plotter(current, 60)
