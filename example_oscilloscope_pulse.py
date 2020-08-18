import instruments
import time
import matplotlib.pyplot as plt
import numpy as np


# math mode version

pg = instruments.K2461()
pg.connect()
v_pulse = 15
scope = instruments.DS1104()
scope.connect()
scope.prepare_for_pulse(v_pulse)
scope.set_trig_chan(3)
scope.single_trig()
time.sleep(12)

print("pulse now")

pg.pulse_voltage(v_pulse, 500e-6)
time.sleep(2)
n = 125000/2
s = 43
data = scope.get_data((n * s), n * (s + 1))
time_step = float(scope.get_time_inc())
time = np.array(range(0, len(data))) * time_step
res = 2973.5
plt.figure()
plt.plot(time, data/res)

plt.show()
