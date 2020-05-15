from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis
import time

h = AlpesProsthesis()
h.initialise()

# Can write to motors separately:
for motor in [2,3,4,5]:
    h.write_positions([40000], [motor])
    time.sleep(3)
    
# Can write to all of them at once.
h.write_positions([0, 0, 0, 0, 0, 0])
time.sleep(3)