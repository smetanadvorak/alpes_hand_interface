from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis
import time

h = AlpesProsthesis()
h.initialise()

# Apply increasing tension to the motors:
print('Positive tension to the motor ...')
N = 10
for i in range(1,N+1):
    h.write_tensions([i/N * MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION/2], [VOIES.AURICULAIRE])
    time.sleep(4/N)
    print('Tension: %2.2f V' %  (i/N * MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION/2))

# Apply decreasing negative tension to the motors:
print('Negative tension to the motor ...')
for i in range(N+1):
    h.write_tensions([-i/N * MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION/2], [VOIES.AURICULAIRE])
    time.sleep(2/N)
    print('Tension: %2.2f V' % (-i/N * MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION/2))

print('Stopeed applying tension.')
time.sleep(2.5)

print('Getting back to initial position ...')
h.write_positions([0]*6)
time.sleep(5)
