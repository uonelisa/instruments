import instruments
import time
import numpy as np
from tkinter import filedialog as dialog
import matplotlib.pyplot as plt

sb = instruments.SwitchBox()
sm = instruments.K2461()

def Van_der_Pauw_Hall_Voltage(probe_current):
    """
    This code is for measueing a Van der Pauw inverted average Hall voltage
    
    returns the Hall voltages
    """
    
    try:
    
        sb.connect(5)
        sm.connect()
        
        #probe_current = 100e-6
        nplc = 2
        vlim = 1
        
        # Voltages
        meas_V_13 = {"I+": "H", "I-": "F", "V1+": "F", "V1-": "E"}
        meas_V_24 = {"I+": "F", "I-": "E", "V1+": "H", "V1-": "G"}
        meas_V_31 = {"I+": "G", "I-": "H", "V1+": "E", "V1-": "F"}
        meas_V_42 = {"I+": "E", "I-": "F", "V1+": "G", "V1-": "H"}
        
        
        MEAS = np.array([meas_V_13, meas_V_24, meas_V_31, meas_V_42])
        name = np.array(["_13", "_24", "_31", "_42"])
        V_array =[]
        
        for i,n in enumerate(MEAS):
            
            V_num = name[i]
            
            sb.switch(n)
            
            sm.enable_4_wire_probe(probe_current, nplc, vlim)
            time.sleep(2)
        
            c, v = sm.read_one()
            R = v / probe_current
            sm.disable_probe_current()
            
            V_array.append(v)
        
            print("Current =",probe_current*10**(3),"mA")
            print(f"Recorded: V{V_num} =",v,"V","  Resistance =",R,"Ohms")
        
        
        sm.BEEP(300,0.5)
        plt.pause(0.5)
        sm.BEEP(400,0.5)
        plt.pause(0.5)
        sm.BEEP(500,0.5)
    
        sb.close()
        sm.close()
    
    
    except:
    
        sb.close()
        sm.close()


    return V_array




def Van_der_Pauw_Sheet_Resistance(probe_current):
    
    """
    This code is for measueing a Van der Pauw inverted average sheet resistance
    
    returns the vertical and horisontal resistance array
    """
    try:
        
    
        sb.connect(5)
        sm.connect()
        
        #probe_current = 100e-6
        nplc = 2
        vlim = 1
        
        
        # Verticle and Horrisontal resistance measurments
        R_12_34 = {"I+": "H", "I-": "G", "V1+": "F", "V1-": "E"}
        R_34_12 = {"I+": "F", "I-": "E", "V1+": "H", "V1-": "G"}
        R_21_43 = {"I+": "G", "I-": "H", "V1+": "E", "V1-": "F"}
        R_43_21 = {"I+": "E", "I-": "F", "V1+": "G", "V1-": "H"}
        
        MEAS_vert = np.array([R_12_34, R_34_12, R_21_43, R_43_21])
        
        R_23_41 = {"I+": "G", "I-": "F", "V1+": "E", "V1-": "H"}
        R_41_23 = {"I+": "E", "I-": "H", "V1+": "G", "V1-": "F"}
        R_32_14 = {"I+": "F", "I-": "G", "V1+": "H", "V1-": "E"}
        R_14_32 = {"I+": "H", "I-": "E", "V1+": "F", "V1-": "G"}
    
        MEAS_hori = np.array([R_23_41, R_41_23, R_32_14, R_14_32])
        
        name_vert = np.array(["_12_34", "_34_12", "_21_43", "_43_21"])
        name_hori = np.array(["_23_41", "_41_23", "_32_14", "_14_32"])
        
        R_vert_arr =[]
        R_hori_arr =[]
        
        for i,n in enumerate(MEAS_vert):
        
            R_num = name_vert[i]
            
            sb.switch(n)
            
            sm.enable_4_wire_probe(probe_current, nplc, vlim)
            time.sleep(2)
            
            c, v = sm.read_one()
            R = v / probe_current
            sm.disable_probe_current()
            
            R_vert_arr.append(R)
            
            
            print("Current =",probe_current*10**(3),"mA")
            print(f"Recorded: R{R_num} =",v,"V","  Resistance =",R,"Ohms")
            
            
            
        for i,n in enumerate(MEAS_hori):
        
            R_num = name_hori[i]
            
            sb.switch(n)
            
            sm.enable_4_wire_probe(probe_current, nplc, vlim)
            time.sleep(2)
            
            c, v = sm.read_one()
            R = v / probe_current
            sm.disable_probe_current()
            
            R_hori_arr.append(R)
            
            
            print("Current =",probe_current*10**(3),"mA")
            print(f"Recorded: R{R_num} =",v,"V","  Resistance =",R,"Ohms")
        
        
        # calculations
        
        R_vert = np.sum(R_vert_arr)/4
        
        R_hori = np.sum(R_hori_arr)/4
        
        R_av = (R_vert + R_hori)/2
        
        R_s = (np.pi*R_av)/np.log(2)
        
        s = np.exp(-np.pi/R_s)
        
        
        sm.BEEP(300,0.5)
        plt.pause(0.5)
        sm.BEEP(400,0.5)
        plt.pause(0.5)
        sm.BEEP(500,0.5)
        
        sb.close()
        sm.close()
        
    
    except:
    
        sb.close()
        sm.close()
        
    
    return R_vert, R_hori



R_vert, R_hori = Van_der_Pauw_Sheet_Resistance(0.1e-3)






























