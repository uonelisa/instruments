# Instruments
Python Instruments Library for common instruments in Spintronics at Nottingham

This repo includes examples scripts, WIP scripts and actually used scripts for convenience. 

Please excuse the informal format of the repo. There are plans to create appropriate branches and neaten things up in the future (probably when procrastinating).

import Instruments
Keithley_2000 = Instruments.K2000() # create the instrument object/instance
K2000.connect(12) # connect to the instrument in port COM12

# lockins.py 
File containing classes for the Signal Recovery SR830 and a preliminary attempt for the Ametek/Synktek MCL model 5210.

# multimeters.py
Just contains the keithley 2000 for now.

# sourcemeters.py
Contains the Keithley models K2400, K2401, K2461 and K6221. 

# oscilloscopes.py 
Contains the Rigol DS1104 basic control scripts.

# redpitaya.py
A script that pulls data from the red pitaya. It interfaces with the script running on the red pitaya for ASOPS measurements and probably won't be too helpful for most people except in B314

# switchbox.py
Contains controls to change the connections in our inhouse switchboxes. Uses dictionaries to make it simple to see what is connecting to what.

# temperaturecontrollers.py 
Contains binary interface code for the TEC1089SV peltier controller for the Room Temperature System. There are plans to control the eurotherm temperature controllers for high temperature measurements and oxford instruments cryogenic controllers.

# sounds.py
Just includes methods to play the error/notification sounds
