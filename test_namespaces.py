from AlpesSpecification import *

voie1 = REGISTRES()
voie2 = REGISTRES()

print(voie1.MODE_CMD_MOTEUR, voie2.MODE_CMD_MOTEUR)
voie1.MODE_CMD_MOTEUR = 1000
voie2.MODE_CMD_MOTEUR = 2000
print(voie1.MODE_CMD_MOTEUR, voie2.MODE_CMD_MOTEUR)

print([s for s in dir(voie1) if not s.startswith('__') and not callable(getattr(voie1, s))])
print(getattr(voie1, 'MODE_CMD_MOTEUR'))
setattr(voie1, 'MODE_CMD_MOTEUR', 3000)
print(getattr(voie1, 'MODE_CMD_MOTEUR'))