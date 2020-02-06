import instruments
import matplotlib.pyplot as plt
import time
import numpy as np
pg = instruments.K2461()

pg.connect()

current = 100e-6
measure_n = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 700, 800, 900,
             1000])
t_measured = np.empty(24)
t_recorded = np.empty(24)

for i in range(len(measure_n)):
    start = time.time()
    pg.measure_n(current, measure_n[i])
    pg.trigger()
    plt.pause(measure_n[i] * 0.2)
    t, vxx, curr = pg.read_buffer(measure_n[i])
    end = time.time()
    t_measured[i] = max(t)
    t_recorded[i] = end - start


data = np.column_stack((measure_n, t_measured, t_recorded))
np.savetxt('loop_time_scaling.txt', data, newline='\n', delimiter='\t')
print('data saved as loop_time_scaling.txt')

plt.figure(1)
plt.plot(measure_n, t_measured, 'k-')
plt.plot(measure_n, t_recorded, 'r-')




