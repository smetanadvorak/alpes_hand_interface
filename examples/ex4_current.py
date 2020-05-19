from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis
import time

h = AlpesProsthesis()
h.initialise()

# Set current limit to zero: this will forbid the motor from drawing any current:
h.set_current_limits( [0], [VOIES.AURICULAIRE] )

# Now try to move this finger with the current limited to 0:
h.write_positions( [MAXIMAL_MOTOR_POSITIONS[VOIES.AURICULAIRE]], [VOIES.AURICULAIRE] )
print('Position command is sent but current is limited to zero. No rotation ...')
time.sleep(5)

# Setup default current limit:
h.set_current_limits( [CONTROLE_COURANT.LIMITE_COURANT_DEFAUT], [VOIES.AURICULAIRE] )
print('Setting up default current limit. Rotation is possible.')
time.sleep(5)

# Go back to initial position:
print('Getting back ...')
h.write_positions( [0], [VOIES.AURICULAIRE] )
time.sleep(5)
