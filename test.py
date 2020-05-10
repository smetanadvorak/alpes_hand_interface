from AlpesSerial import *
from AlpesHand import *
from AlpesProtocol import *
import time

h = AlpesHand()
h.initialise()

#h.get_memory_dump()
#print(h.memory_dump[5])

print('Writing motor position ...')
h.write_positions([0]+[0] * 5)
#h.write_positions([0, 0, 0, 0, 0, 0])
#res = h.write_tensions([-0]*6)


print('Reading motor position ...')
for i in range(10):
     print('Pos.:', h.read_positions())
     print('Vel.:', h.read_velocities())
#print('Pos.:', h.read_positions()) 

#('Reading motor modes ...')
#print(h.read_registers_across(REGISTRES.MODE_CMD_MOTEUR)) 
