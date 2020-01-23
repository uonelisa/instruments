import numpy as np
import time
import instruments

switchbox = instruments.SwitchBox()
balancebox = instruments.BalanceBox()
pg = instruments.K2461()
# all 4 opposite pairing assignments for 2 wire measurements
assignments_0 = {"I+": "G", "I-": "C"}
assignments_45 = {"I+": "F", "I-": "B"}
assignments_90 = {"I+": "E", "I-": "A"}
assignments_135 = {"I+": "D", "I-": "H"}

resistance_assigned = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0, "H": 0}
resistance_measured = {}

switchbox.connect(5)
balancebox.connect(11)
pg.connect()

pg.enable_2_wire_probe(100e-6, 2)

switchbox.switch(assignments_0)
time.sleep(0.1)
c, v = pg.read_one()
resistance_measured["G"] = (v / c) / 2
resistance_measured["C"] = (v / c) / 2

switchbox.switch(assignments_45)
time.sleep(0.1)
c, v = pg.read_one()
resistance_measured["F"] = (v / c) / 2
resistance_measured["B"] = (v / c) / 2

switchbox.switch(assignments_90)
time.sleep(0.1)
c, v = pg.read_one()
resistance_measured["E"] = (v / c) / 2
resistance_measured["A"] = (v / c) / 2

switchbox.switch(assignments_135)
time.sleep(0.1)
c, v = pg.read_one()
resistance_measured["D"] = (v / c) / 2
resistance_measured["H"] = (v / c) / 2

max_res = max(resistance_measured.values()) + 50
# map the assigned value to be max_res - value. Should be easy once you know how. Probably requires "zip"


