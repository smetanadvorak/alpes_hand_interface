from AlpesSerial import *
from AlpesHand import *
from AlpesProtocol import *
from AlpesGestures import *
import time

#h = AlpesHand()
h = AlpesProsthesis()
h.initialise()


# Go through all gestures
# gestures = [g for g in dir(GESTURES()) if not g.startswith('__') and not callable(getattr(GESTURES(), g))]
# for g in gestures:
#     print('Performing %s gesture' % g)
#     h.set_gesture(getattr(GESTURES(), g))
#     time.sleep(2.5)


# Go through 1-2-3-4-5 gestures
# gestures = ["ONE", "TWO", "THREE", "FOUR", "FIVE"]
# for g in gestures:
#     print('Performing %s gesture' % g)
#     h.set_gesture(getattr(GESTURES(), g))
#     time.sleep(2)
# 
# h.set_gesture(GESTURES.REST)


# #Proportional control (position)
# h.set_grasp(GRASPS.CYLINDRICAL)
# time.sleep(1)
# N = 10
# for t in range(N):
#     h.proportional_control_position(t/N)
#     time.sleep(0.25)
# 
# time.sleep(5)
# h.proportional_control_position(0)
# h.set_gesture(GESTURES.OPEN)


# Proportional control (current)
h.set_grasp(GRASPS.CYLINDRICAL)
time.sleep(5)
N = 10
for t in range(N+1):
    h.proportional_control_current(t/N)
    time.sleep(0.1)

for t in range(N,-1,-1):
    h.proportional_control_current(t/N)
    time.sleep(0.1)

time.sleep(5)
h.proportional_control_current(0)
h.set_gesture(GESTURES.OPEN)


h.get_memory_dump()
print(h.memory_dump[5])

#print('Writing motor position ...')
#h.write_positions([0]+[0] * 5)
#h.write_positions([0, 0, 0, 0, 0, 0])
#res = h.write_tensions([-0]*6)


print('Reading motor position ...')
for i in range(10):
     print('Pos.:', h.read_positions())
     print('Vel.:', h.read_velocities())
print('Pos.:', h.read_positions()) 

#('Reading motor modes ...')
#print(h.read_registers_across(REGISTRES.MODE_CMD_MOTEUR)) 

