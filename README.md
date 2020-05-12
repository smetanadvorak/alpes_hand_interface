# Python interface for Alpes robotic hands

## Dependencies
You have to use Python 3 (tested on 3.8) with the following packages installed:
	-pyserial
	-numpy

## Contents
Classes and constant structures (from low to high level):
- __AlpesSpecification.py__:    provides a bunch of constant structures that define alias for the hand registers, communication codes, etc.
- __AlpesSerial__:              a mere supplement for original pyserial module; can automatically detect serial ports that hands are connected to. 
- __AlpesProtocol__:            contains functions that transform requests to correct binary packages that are sent to the hand. Also parces the responses. 
- __AlpesHand__:                low-level reading/writing instructions for the hand, initialisation, commands. 
- __AlpesProsthesis__:          high-level command instructions for the hand. Permits to perform discrete gestures, as well as proportional grasps.
	
_Note_: class diagram that illustrates the relationship between these classes is provided in *class\_diagram.xml* and *class\_diagram.png* files.

## Usage
Before using this code, please get familiar with the documentation files provided by hand's developer.

### Bare bones
Very basic code that initialises the hand and the corresponding __AlpesProsthesis__ object:
```python
from AlpesSpecification import *
from AlpesProsthesis import AlpesProsthesis
h = AlpesProsthesis()
h.initialise()
```
If everything goes correctly, the hand will start the initialisation procedure. This procedure lasts about 30 seconds and aims to check the extents of motor rotations and is necessary if the hand was switched off for some considerable amount of time. If initialisation is finished successfully, you will see the message: 

`Hand initialised!` 

in your terminal. If something goes wrong, another message will appear: 

`Hand initialisation timeout (60 seconds) exceeded without the hand confirming the end of initialisation.`

It is hard to tell in advance, what could go wrong during initialisation since the author never experienced it. First thing to do would be to check if nothing blocks the motion of the fingers. Other than that ... It'd better not happen.

__Note__: If the hand was not switched off between the runs of this code, the  initialisation procedure will be automatically omitted to save time.

### Reading/writing hand's registers
To read in a specific register, first, check it's name in __AlpesSpecification.py__ file. For example, if you want to know the parameters of index finger's internal PID controller, you want to read from __COEF\_P__, __COEF\_I__ and __COEF\_D__ registers of the corresponding channel:
```python
pid = [ h.read_register(VOIES.INDEX, REGISTRES.COEF_P),
		h.read_register(VOIES.INDEX, REGISTRES.COEF_I),
		h.read_register(VOIES.INDEX, REGISTRES.COEF_D) ]
```
This will read three registers starting from the position of __COEF\_P__ register in motor of the INDEX finger, and put the result in a 3-element list __pid__.


To read a specific register for all motors of the hand, use the following method:
```python
mode = h.read_registers_across(REGISTRES.MODE_CMD_MOTEUR)
```
This will return a 6-element list (for six motors) containing the control modes applied in the motors. 


Writing to the registers is very similar to reading, except that you need to add data to the function call:
```python
h.write_register(VOIES.INDEX, REGISTRES.MODE_CMD_MOTEUR, 1)
h.write_registers_across(REGISTRES.MODE_CMD_MOTEUR, [0,0,0,1,1,1])
```
Where the last argument is the integer that you want to right into the register (or a list, in case of writing to all the motors).

If you want to see the contents of all registers of a specific channel (middlefinger, in this example), you can use:
```python
h.get_memory_dump()
print(h.memory_dump[VOIES.MAJEUR])
```
This will list all the registers of this channel and their contents.


### Writing direct commands
The device has three accessible variables that affect the motion of the fingers:
- __REGISTRE.CONSIGNE/_TENSION/_POSITION__ when __REGISTRE.MODE\_CMD\_MOTEUR = 1__ allows to set an angular position of each motor that the internal PIDs will seek to reach.
- __REGISTRE.CONSIGNE/_TENSION/_POSITION__ when __REGISTRE.MODE\_CMD\_MOTEUR = 2__ allows to apply a specific voltage to each of the motors (between -11.5V and 11.5V).
- __REGISTRE.LIMITE\_COURANT__ allows to change the internal limit set on the motor current.

Access these variables is wrapped in the methods:
```python
h.write_positions([0, 0, 0, 0, 0, 0]) #Sets target angular position of all motors to 0 (unfold all fingers).
h.write_tensions([0, 0, 5, -5, 0, 0]) #Slowly folds the index and unfolds the middle finger.
h.set_current_limits([750, 750, 750, 750, 750, 750]) #Sets default value of current limit (see AlpesSpecification.py for more information).
```
The usage of *h.write\_positions()* is harmless. This software checks and forbids erroneous requests.
The usage of *h.write\_tensions()* or *h.set\_current\_limits()* may be harmful if done without proper attention. This software checks and forbids requests that exceed values specified in the documentation. However, when a finger is blocked by an object and a large torque is applied by the motor, its cable may break. This is not catastrophic, but replacing the cable may be tedious. 

### Gestures and proportional control
List of pre-programmed gestures can be found in __AlpesProsthesis.py__, class __GESTURES__. Each gesture is simply a list of final positions to be reached by the motors. Use the following method to perform gestures:
```python
import time
h.set_gesture(GESTURES.VICTORY)
time.sleep(2) #Give the hand time to reach the final position before proceeding.
```
Or iterate through multiple gestures:
```python
from AlpesProsthesis import AlpesProsthesis, GESTURES
import time
for g in ["ONE", "TWO", "THREE", "FOUR", "FIVE"]:
    print('Performing %s gesture' % g)
    h.set_gesture(getattr(GESTURES(), g))
    time.sleep(2)
```

(UNDER REVISION)

Proportional control is continuous version of setting a gesture. It makes the hand to perform a grasp up to a specific degree between 0 (no grasp) and 1 (maximal grasping force).
Available grasps are listed in __AlpesProsthesis.py__, class __GRASPS__ (see its comments for details). List can be extened.
To set up proportional control, run:
```python
from AlpesProsthesis import AlpesProsthesis, GRASPS
h.set_grasp(GRASPS.CYLINDRICAL)
```
and then, to perform the proportional control:
```python
N = 10
for t in range(N+1):
     h.proportional_control_current(t/N)
     time.sleep(0.2)
```

## Two-hands support

## Relation with official Alpes' documentation
In the official documentation all the internal constants and register names are in French. Therefore, all variable names in __AlpesSpecification.py__ that were drawn from the documentation are in French, too, for consistence. All other elements or derivatives of the official names are in English. 

## What's next?
One can extend the provided classes the way he or she needs. The only suggestion is to not change the methods that are close to hardware, like reading/writing methods of __AlpesHand__. Low-level classes like __AlpesSerial__ and __AlpesProtocol__ should be handles with care and full understanding of your intentions.
To implement new control approaches, inherit from __AlpesHand__ or __AlpesProsthesis__. 

## Acknowledgments
We would like to thank Alpes Industries for providing us with a detailed documentation on their product and for some after-purchase support.
Also, kind regards to Benjamin Gautier who was the first to write Matlab utilities for working with the hands.
Finally, we thank Guillaume Perrault for pythonification of the Benjamin's code, which became a basis for this repositorium.

