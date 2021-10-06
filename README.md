
# instruments
Python Instruments Library for common instruments in Spintronics at Nottingham

This repo includes examples scripts, WIP scripts and actually used scripts for convenience. 

Please excuse the informal format of the repo. There are plans to create appropriate branches and neaten things up in the future.
## Documentation 
    https://stupoole.github.io/instruments/

## Installation from github
    pip install git+https://github.com/stupoole/instruments
       
    
## Updating if already installed
    pip install --upgrade git+https://github.com/stupoole/instruments
    
## To add as a dependency to another pip repository
Add the following argument to setup.py setuptools.setup()

    dependency_links=['https://github.com/stupoole/instruments/tarball/repo/master#egg=package-1.0'],


## Importing the package and first use
    import instruments
    multimeter = instruments.K2000()
    multimeter.connect(12) # connected on COM12
    multimeter.

## Examples
    https://github.com/stupoole/instrumentsexamples

# Modules
## lockins
File containing classes for the Signal Recovery SR830. The Synktek MCL code is a private repository still.  

## multimeters
Just contains the keithley 2000 for now.

## sourcemeters
Contains the Keithley models K2400, K2401, K2461 and K6221. 

## oscilloscopes
Contains the Rigol DS1104 basic control scripts.

## redpitaya
A script that pulls data from the red pitaya. It interfaces with the script running on the red pitaya for ASOPS measurements and probably won't be too helpful for most people except in B314

## switchbox
Contains controls to change the connections in our inhouse switchboxes. Uses dictionaries to make it simple to see what is connecting to what.

## temperaturecontrollers
Contains binary interface code for the TEC1089SV peltier controller for the Room Temperature System. There are plans to control the eurotherm temperature controllers for high temperature measurements and oxford instruments cryogenic controllers.

## sounds
Just includes methods to play the error/notification sounds
