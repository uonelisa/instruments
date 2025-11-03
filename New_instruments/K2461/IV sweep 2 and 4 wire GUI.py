import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets



# Close function
def closefunc(event):
    plt.close('all') # Close all open figures


# Running Sweep function
def RunFunc(event):
    
    # 2 or 4 wire command
    wire_selected = Wires_button.value_selected
    
    print(wire_selected, "Selected")
    
    meas_4Wire = {"I+": "H", "I-": "G", "V1+": "E", "V1-": "F"}
    meas_2Wire = {"I+": "H", "I-": "F"}
    
    if wire_selected == '2 wire':
       
        wire_choice = meas_2Wire
        wire_title = "2 wire IV Curve"
    
    elif wire_selected == '4 wire':
       
        wire_choice = meas_4Wire
        wire_title = "4 wire IV Curve"
    
    else:
        
        wire_choice = 0
        print("Select 2 or 4 wire")
    
    # Popout figure
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_ylabel("Voltage (V)")
    ax.set_xlabel("Current (A)")
    ax.set_title(wire_title)
    ax.grid(True)
    
    
    # Current perams
    Current_limit = 1e-3
    
    # print("Max Current = ",Maxbox.text)
    # print("Min Current = ",Minbox.text)
    
    Maxval_inputed = float(Maxbox.text)
    Minval_inputed = float(Minbox.text)
    Stepval_inputed = float(Stepbox.text)
    
    if Maxval_inputed > Current_limit or Minval_inputed < -Current_limit:
        
        Imax = 0
        Imin = 0
        steps = 0
        print("current value too high")
        
    else:
        
        Imax = Maxval_inputed
        Imin = Minval_inputed
        steps = Stepval_inputed
    
    print("Max Current = ",Imax)
    print("Min Current = ",Imin)
    print("Current Steps = ",steps)
    
    # Connecting and setting up source meter and switch box
    sb = instruments.SwitchBox()
    sm = instruments.K2461()

    sb.connect(5)
    sm.connect()
    
    sb.switch(wire_choice)
    
    nplc = 2
    vlim = 1

    Zero_Imax = np.arange(0, Imax , steps)
    Imax_Zero = np.arange(Imax, 0, -steps)
    Zero_Imin = np.arange(0, Imin , -steps)
    Imin_Zero = np.arange(Imin, 0, steps)
    
    Isweep = np.append(Zero_Imax,[Imax_Zero, Zero_Imin, Imin_Zero])
    
    # array setup
    Current_arr = []
    Voltage_arr = []
    
    Failed = "No"
    

    # loop for sweep
    try:
        
        if wire_selected == '2 wire':
            
            for i, n in enumerate(Isweep):
                
                sm.enable_2_wire_probe(n, nplc, vlim)
                plt.pause(0.001)
                c, v = sm.read_one()
                plt.pause(0.001)
                
                Current_arr.append(c)
                Voltage_arr.append(v)

                ax.scatter(c,v, color="blue")
                plt.pause(0.01)
                
            
            sm.disable_probe_current()

          
        elif wire_selected == '4 wire':
            
            for i, n in enumerate(Isweep):
                
                sm.enable_4_wire_probe(n, nplc, vlim)
                plt.pause(0.001)
                c, v = sm.read_one()
                plt.pause(0.001)
                
                Current_arr.append(c)
                Voltage_arr.append(v)
    
                ax.scatter(c,v, color="blue")
                plt.pause(0.01)
                
            
            sm.disable_probe_current()

    except:
        
        sb.close()
        sm.close()
        
        print("Something went wrong")
        
        sm.BEEP(311, 0.25)
        plt.pause(0.15)
        sm.BEEP(294, 0.25)
        plt.pause(0.15)
        sm.BEEP(262, 0.5)
        plt.pause(0.15)
        
        Failed = "Yes"
        

    if Failed == "No":
        
        sm.BEEP(440, 0.6)
        plt.pause(0.1)
        sm.BEEP(466, 0.6)
        plt.pause(0.1)
        sm.BEEP(494, 0.6)
        plt.pause(0.1)
        sm.BEEP(523, 0.6)
        plt.pause(0.1)
        sm.BEEP(784, 1.2)
        plt.pause(0.1)
    
        sb.close()
        sm.close()

    # colecting and plotting data
    slope, intercept = np.polyfit(Current_arr, Voltage_arr, 1)
    dummy_arr = np.arange(Imin,Imax + steps,steps)
    ax.plot(dummy_arr, dummy_arr*slope + intercept)
    
    print("Resistance = ",slope,"Ohms")
    
    if save_button.value_selected == "Data saved":
        
        # saving data
        name = FileNamebox.text
        data = np.column_stack([Current_arr,Voltage_arr])
        date = FileDatabox.text
        np.savetxt(rf"C:\Users\ppyak4\OneDrive - The University of Nottingham\PhD\Exported Data sets from Python\Pulsing Devices Oct 2025\RC364 10um\{date}\{name}.txt", data)
    




fig_input_control = plt.figure(figsize=(6, 4)) # control pannel figure
# Title
fig_input_control.text(0.3, 0.9, "Alex's IV Sweep", size=20)

# Off button
Offax = plt.axes([0.85, 0.05, 0.1, 0.1]) # Add new axes to the figure
Offbutton = widgets.Button(Offax, 'Close')
Offbutton.on_clicked(closefunc)

# Run button
Runax = plt.axes([0.05, 0.05, 0.25, 0.25]) # Add new axes to the figure
Runbutton = widgets.Button(Runax, 'Run')
Runbutton.on_clicked(RunFunc)

# Radio buttons for selecting 2 or 4 wire
Wires_ax = plt.axes([0.7, 0.7, 0.15, 0.15])
Wires_button = widgets.RadioButtons(Wires_ax, ('2 wire', '4 wire'))
#Wires_button.on_clicked(Update)

# Radio buttons for selecting save data or not
Saved_ax = plt.axes([0.7, 0.5, 0.25, 0.15])
save_button = widgets.RadioButtons(Saved_ax, ('No data saved', 'Data saved'))
#Wires_button.on_clicked(Update)

# Max Current input
MaxBox_ax = plt.axes([0.3, 0.75, 0.1, 0.1])
Maxbox = widgets.TextBox(MaxBox_ax, "Max Current (A) =", initial='1e-4', color='.95', hovercolor='1', label_pad=0.01, textalignment='left')

# Min Current input
MinBox_ax = plt.axes([0.3, 0.6, 0.1, 0.1])
Minbox = widgets.TextBox(MinBox_ax, "Min Current (A) =", initial='-1e-4', color='.95', hovercolor='1', label_pad=0.01, textalignment='left')

# Current step input
StepBox_ax = plt.axes([0.3, 0.45, 0.1, 0.1])
Stepbox = widgets.TextBox(StepBox_ax, "Current Steps (A) =", initial='1e-6', color='.95', hovercolor='1', label_pad=0.01, textalignment='left')

# File name input
FileName_ax = plt.axes([0.5, 0.35, 0.45, 0.09])
FileNamebox = widgets.TextBox(FileName_ax, "File name :", initial='', color='.95', hovercolor='1', label_pad=0.01, textalignment='left')

# File directory input
FileDate_ax = plt.axes([0.5, 0.23, 0.45, 0.09])
FileDatabox = widgets.TextBox(FileDate_ax, "File date :", initial="date ie 03112025",  color='.95', hovercolor='1', label_pad=0.01, textalignment='left') 





























