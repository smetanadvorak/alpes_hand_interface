from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis
import time

h = AlpesProsthesis()
h.initialise()

# Start flexing fingers
h.write_positions([5000, 20000, 40000, 40000, 40000, 40000])
# Reading while fingers are moving
print('Flexsion: reading motor positions and velocities ...')
for i in range(25):
     print('Pos.: %s, Vel.: %s', (h.read_positions(), h.read_velocities()))
     time.sleep(0.1)
     
     
# Start extending fingers
h.write_positions([0, 0, 0, 0, 0, 0])
# Reading while fingers are moving
print('Extension: reading motor positions and velocities ...')
for i in range(25):
     print('Pos.: %s, Vel.: %s' % (h.read_positions(), h.read_velocities()))
     time.sleep(0.1)
     
# Positions are measured in encoder ticks.
# Velocities are measured in rpm of the motor shaft after reduction.
