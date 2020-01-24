import numpy as np
import time
import instruments

switch_box = instruments.SwitchBox()
balance_box = instruments.BalanceBox()
pg = instruments.K2461()
# all 4 opposite pairing assignments for 2 wire measurements
assignments_0 = {"I+": "G", "I-": "C"}
assignments_45 = {"I+": "F", "I-": "B"}
assignments_90 = {"I+": "E", "I-": "A"}
assignments_135 = {"I+": "D", "I-": "H"}

resistance_assigned = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0, "H": 0}
resistance_measured = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0, "H": 0}

switch_box.connect(4)
balance_box.connect(5)
pg.connect()

pg.enable_2_wire_probe(100e-6, 2)
balance_box.reset_resistances()
switch_box.switch(assignments_0)
time.sleep(2)
c, v = pg.read_one()
print(int(v/c))
resistance_measured["G"] = int((v / c) / 2)
resistance_measured["C"] = int((v / c) / 2)

switch_box.switch(assignments_45)
time.sleep(2)
c, v = pg.read_one()
resistance_measured["F"] = int((v / c) / 2)
resistance_measured["B"] = int((v / c) / 2)

switch_box.switch(assignments_90)
time.sleep(2)
c, v = pg.read_one()
resistance_measured["E"] = int((v / c) / 2)
resistance_measured["A"] = int((v / c) / 2)

switch_box.switch(assignments_135)
time.sleep(2)
c, v = pg.read_one()
resistance_measured["D"] = int((v / c) / 2)
resistance_measured["H"] = int((v / c) / 2)
print(resistance_measured["D"])
max_res = int(max(resistance_measured.values()) + 50)

for pin, res in resistance_measured.items():
    resistance_assigned[pin] = max_res - int(res)

balance_box.set_resistances(resistance_assigned)

print(resistance_assigned, resistance_measured)
