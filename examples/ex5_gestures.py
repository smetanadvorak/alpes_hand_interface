from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis, GESTURES
import time

h = AlpesProsthesis()
h.initialise()

# Go through all gestures
gestures = [g for g in dir(GESTURES()) if not g.startswith('__') and not callable(getattr(GESTURES(), g))]
for g in gestures:
     print('Performing %s gesture' % g)
     h.set_gesture(getattr(GESTURES(), g))
     time.sleep(2.5)

print('Back to initial position')
h.set_gesture(GESTURES.OPEN)
time.sleep(5)
