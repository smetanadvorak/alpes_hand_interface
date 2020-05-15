from Alpes.Specification import *
from Alpes.Prosthesis import AlpesProsthesis

# Create an instance of AlpesProsthesis() object. It will try to connect to the hand by itself.
h = AlpesProsthesis()
# Start initialisation procedure.
h.initialise()