from AlpesSerial import *
from AlpesHand import *
from AlpesProtocol import *
import time

h = AlpesHand()
h.initialise()
time.sleep(1)


print('Writing motor position ...')
res = h.write_positions([15000]*6)


print('Reading motor position ...')
for i in range(50):
     print('Pos.:', h.read_positions())
     print('Vel.:', h.read_velocities())
     

print('Reading motor modes ...')
print(h.read_registers_across(MODE_CMD_MOTEUR)) 
