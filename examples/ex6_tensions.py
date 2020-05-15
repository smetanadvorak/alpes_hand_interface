from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis
import time

h = AlpesProsthesis()
h.initialise()

# Apply increasing tension to the motors:
# N = 10
# for i in range(1,N+1):
#     h.write_tensions([i/N * MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION/2], [VOIES.AURICULAIRE])
#     time.sleep(2/N)
#     print(h.read_registers_across(REGISTRES.SORTIE_PWM))
# 
# # Apply decreasing negative tension to the motors:
# for i in range(N+1):
#     h.write_tensions([-i/N * MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION/2], [VOIES.AURICULAIRE])
#     time.sleep(1/N)
#     print(h.read_registers_across(REGISTRES.SORTIE_PWM))
#     
# h.write_positions([0]*6)

# print(h.read_register(VOIES.AURICULAIRE, REGISTRES.CONSIGNE_TENSION_POSITION)[0]/100)
# #h.write_tensions([-5.5], [VOIES.AURICULAIRE])
# time.sleep(0.5)
# print(h.read_register(VOIES.AURICULAIRE, REGISTRES.CONSIGNE_TENSION_POSITION)[0]/100)
# h.write_positions([0]*6)
# print(h.read_register(VOIES.AURICULAIRE, REGISTRES.CONSIGNE_TENSION_POSITION)[0]/100)

print(h.read_memory()[5])