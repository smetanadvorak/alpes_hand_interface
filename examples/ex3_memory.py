from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis
import time

h = AlpesProsthesis()
h.initialise()

# Access any register you need. Register names are defined in Alpes.Specifications
pid = [ h.read_register(VOIES.INDEX, REGISTRES.COEF_P),
        h.read_register(VOIES.INDEX, REGISTRES.COEF_I),
        h.read_register(VOIES.INDEX, REGISTRES.COEF_D) ]
        
print('PID coefficients of index finger motor: ', pid)


# Access the same register in all motors:
mode = h.read_registers_across(REGISTRES.MODE_CMD_MOTEUR)
print('Motor command modes: ', mode)


# Read the entire hand's memory:
h.read_memory()
print('Contents of all registers of thumb motor:')
print(h.memory[VOIES.POUCE])