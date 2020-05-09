from AlpesSerial import *
from AlpesHand import *
from AlpesProtocol import *
import time

h = AlpesHand()
#h.initialise()

print('Setting control mode ...')
res = h.set_control_mode(CONTROL_MODE.POSITION)
print(res)

time.sleep(2)
print('Writing motor position ...')
res = h.write_motor_position([10000]*6)
#res = h.write_motor_position(1000, 1)
print(res)

time.sleep(2)

print('Reading motor position ...')
res = h.read_motor_position()
print(res)

#print('Writing motor position directly ...')
#res = h.serial.write_register(2000 + 1, 1, [2666])
#print(res)

#print('Reading motor position directly ...')
#res = h.serial.read_register(2000 + 1, 1)
#print(res)

#res = h.serial.read_register(2000 + 2, 2)
#print(res)
#test_command = b'W1\x01\x03\x02\x01\x00'
#h.serial.write(test_command)
#print(h.serial.read(10))