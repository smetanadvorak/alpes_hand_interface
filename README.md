# Python interface for Alpes robotic hands

## Dependencies
You have to use Python 3 (tested on 3.8) with the following packages installed:
	-pyserial
	-numpy

## Contents
Classes and constant structures (from low to high level):
- AlpesSpecification.py 	- provides a bunch of constant structures that define alias for the hand registers, communication codes, etc.
- AlpesSerial				- a mere supplement for original pyserial module; can automatically detect serial ports that hands are connected to. 
- AlpesProtocol				- contains functions that transform requests to correct binary packages that are sent to the hand. Also parces the responses. 
- AlpesHand.	 			- low-level reading/writing instructions for the hand, initialisation, commands. 
- AlpesProsthesis			- high-level command instructions for the hand. Permits to perform discrete gestures, as well as proportional grasps.
	
Note: class diagram that illustrates the relationship between these classes is provided in *class\_diagram.xml* and *class\_diagram.png* files.

## Usage
### Bare bones
Very basic code that initialises the hand and the corresponding AlpesProsthesis object:
'''python
from AlpesProsthesis import AlpesProsthesis
h = AlpesProsthesis()
h.initialise()
'''
If everything goes correctly, the hand will start the initialisation procedure. This procedure lasts about 30 seconds and aims to check the extents of motor rotations and is necessary if the hand was switched off for some considerable amount of time. If initialisation is finished successfully, you will see the message: 
'Hand initialised!' 
in your terminal. If something goes wrong, another message will appear: 
'Hand initialisation timeout (60 seconds) exceeded without the hand confirming the end of initialisation.'.

If the hand was not switched off between the runs of this code, the  initialisation procedure will be automatically omitted to save time.

### Reading/writing hand's registers
memory dump
re-initialised automatically?

### Writing direct commands

### Gestures and proportional control

## Relation with official Alpes' documentation

## What's next?

## Acknowledgments