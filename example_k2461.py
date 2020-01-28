import visa
import numpy as np
import time
import matplotlib.pyplot as plt
import instruments

pg = instruments.K2461()
pg.connect()

pg.pulse_current(1e-3, 1e-3)
time.sleep(5)

pg.measure_n(100e-6, 50, 2)
pg.trigger()
time.sleep(10)
time, data = pg.read_buffer(50)
plt.plot(time, data)
plt.show()

pg.enable_2_wire_probe(100e-6, 2)
c, v = pg.read_one()
print(v/c)
pg.disable_probe_current()
pg.enable_4_wire_probe(100e-6, 2)
c, v = pg.read_one()
print(v/c)
pg.disable_probe_current()
