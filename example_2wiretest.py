import instruments
import time
import numpy as np
from tkinter import filedialog as dialog

assignments_0 = {"I+": "A", "I-": "E"}
assignments_45 = {"I+": "B", "I-": "F"}
assignments_90 = {"I+": "C", "I-": "G"}
assignments_135 = {"I+": "D", "I-": "H"}

R = np.zeros(4)
switch_box = instruments.SwitchBox()

pg = instruments.K2461()

switch_box.connect(4)

pg.connect()

pg.enable_2_wire_probe(1e-3, 2)
switch_box.switch(assignments_0)
time.sleep(1)
c, v = pg.read_one()
R[0] = (v / c)


time.sleep(0.1)

switch_box.switch(assignments_45)
time.sleep(1)
c, v = pg.read_one()
R[1] = (v / c)


time.sleep(0.1)

switch_box.switch(assignments_90)
time.sleep(1)
c, v = pg.read_one()
R[2] = (v / c)


time.sleep(0.1)

switch_box.switch(assignments_135)
time.sleep(1)
c, v = pg.read_one()
R[3] = (v / c)


print('Resistances: \n', R)
pg.disable_probe_current()
name = dialog.asksaveasfilename(title='Save')
if name:  # if a name was entered, don't save otherwise
    if name[-4:] != '.txt':  # add .txt if not already there
        name = f'{name}.txt'
    np.savetxt(name, R, newline='\r\n', delimiter='\t')  # save
    print(f'Data saved as {name}')
else:
    print('Data not saved')