import numpy as np
from tkinter import filedialog as dialog

__all__ = ['save']


def save(data, header=None):
    name = dialog.asksaveasfilename(title='Save data')
    if name:  # if a name was entered, don't save otherwise
        if name[-4:] != '.txt':  # add .txt if not already there
            name = f'{name}.txt'
        if header:
            np.savetxt(name, data, header=header, newline='\n', delimiter='\t')  # save
        else:
            np.savetxt(name, data, newline='\n', delimiter='\t')  # save
        print(f'Data saved as {name}')
    else:
        print('Data not saved')
