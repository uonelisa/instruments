import time
import matplotlib.pyplot as plt
import instruments
# This scripts measures the 4 wire resistance using the k2461 as a source meter.

pg = instruments.K2461()
dmm = instruments.K2000()
dmm.connect(4)
pg.connect()

pg.enable_2_wire_probe(100e-6, 2)
time.sleep(0.1)
dmm.measure_one(0, 2)
current, voltage = pg.read_one()

volt2 = dmm.read_one()
print(voltage/current, volt2/current)
pg.disable_probe_current()

pg.enable_4_wire_probe(100e-6, 2)
time.sleep(0.1)
dmm.measure_one(0, 2)
current, voltage = pg.read_one()
volt2 = dmm.read_one()
print(voltage/current, volt2/current)
pg.disable_probe_current()