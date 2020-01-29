import numpy as np
import time
import instruments

## This script measures the resistance of each pulsing channel in an 8 arm device. The resulting resistances are left
# assigned to the bb and therefore can be used for pulsing after or the resulting assignments can be copied from the
# output into your own script.



# define all 4 opposite pairing assignments for 2 wire measurements
assignments_0 = {"I+": "G", "I-": "C"}
assignments_45 = {"I+": "F", "I-": "B"}
assignments_90 = {"I+": "E", "I-": "A"}
assignments_135 = {"I+": "D", "I-": "H"}

# a dictionary to store the values in
resistance_assigned = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0, "H": 0}
resistance_measured = {}

# create instrument objects
switchbox = instruments.SwitchBox()
balancebox = instruments.BalanceBox()
pg = instruments.K2461()

# connect to devices
switchbox.connect(5)
balancebox.connect(11)
pg.connect()

# set k2461 ready for 100uA probe current 2 wire with nplc 2
pg.enable_2_wire_probe(100e-6, 2)

# set first assignment
switchbox.switch(assignments_0)
time.sleep(0.1)  # delay to allow the sb to switch
c, v = pg.read_one()  # read one value
resistance_measured["G"] = int((v / c) / 2)  # store half resistance rounded down in each channel part of the pair
resistance_measured["C"] = int((v / c) / 2)

switchbox.switch(assignments_45)
time.sleep(0.1)
c, v = pg.read_one()
resistance_measured["F"] = int((v / c) / 2)
resistance_measured["B"] = int((v / c) / 2)

switchbox.switch(assignments_90)
time.sleep(0.1)
c, v = pg.read_one()
resistance_measured["E"] = int((v / c) / 2)
resistance_measured["A"] = int((v / c) / 2)

switchbox.switch(assignments_135)
time.sleep(0.1)
c, v = pg.read_one()
resistance_measured["D"] = int((v / c) / 2)
resistance_measured["H"] = int((v / c) / 2)

max_res = int(max(resistance_measured.values()) + 10)

for pin, res in resistance_measured.items():
    resistance_assigned[pin] = max_res - int(res)

balancebox.set_resistances(resistance_assigned)

print(resistance_assigned, resistance_measured)

# TODO: Test the resistance after setting resbox


