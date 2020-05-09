import struct
from enum import Enum
 
# Field names are in French to match the Alpes Instruments' official documentation
class PREFIXES:
    ECRITURE_REGISTRE            = bytearray([ord('W'), ord('R')])
    ECRITURE_MODE_CMD_MOTEUR     = bytearray([ord('W'), ord('1')])
    ECRITURE_CONSIGNE_TENSION_POSITION = bytearray([ord('W'), ord('2')])
    ECRITURE_LIMITE_COURANT      = bytearray([ord('W'), ord('3')])
    
    LECTURE_REGISTRE             = bytearray([ord('R'), ord('D')])
    LECTURE_POSITION_CODEUR      = bytearray([ord('W'), ord('1')])
    LECTURE_VITESSE_MOTEUR       = bytearray([ord('W'), ord('4')])


class FINGERS:
    POUCE_ROTATION  = 0
    POUCE           = 1
    INDEX           = 2
    MAJEUR          = 3
    ANNULAIRE       = 4
    AURICULAIRE     = 5  
    
class CONTROL_MODE:
    STOP = 0
    POSITION = 1
    TENSION = 2

  
  
class AlpesMessage():
    def __str__(self):
        s  = 'Alpes Message:\n'
        s += 'Type: %s\n' % str(self.prefix, 'utf-8')
        s += 'Start register: %d\n' % self.start_register
        s += 'Number of registers: %d\n' % self.number_registers
        s += 'Data (payload): ' + ' '.join('%d'* len(self.data)) % tuple(self.data) + '\n'
        return s
        
        
      
class AlpesCommand(AlpesMessage):
    def __init__(self, prefix, start_register, number_registers, data = []):
        self.prefix = prefix #Type of command: WR, RD, W1 ... W6
        self.start_register = start_register
        self.number_registers = number_registers
        self.data = self.check_data(number_registers, data) 
    
    def check_data(self, number_registers, data):
        if self.prefix != PREFIXES.LECTURE_REGISTRE:
            if not isinstance(data, list):
                data = [data]
            assert len(data) == number_registers, 'Number of registers requested for writing does not match the length of provided data'
        else:
            data = []
        return data
        
    def pack(self):
        # Messages sent to the hand have different format depending on their type.
        # For details, see "Protocole Com Main Robotisee". 
        if self.prefix == PREFIXES.ECRITURE_REGISTRE:
            self.packed = self.prefix + struct.pack('<HH', self.start_register, self.number_registers)
            self.packed += struct.pack('<%sI' % len(self.data), *self.data)
            
        elif self.prefix == PREFIXES.LECTURE_REGISTRE:
            self.packed = self.prefix + struct.pack('<HH', self.start_register, self.number_registers)
            
        elif   self.prefix == PREFIXES.ECRITURE_MODE_CMD_MOTEUR \
            or self.prefix == PREFIXES.LECTURE_POSITION_CODEUR  \
            or self.prefix == PREFIXES.LECTURE_VITESSE_MOTEUR:
            self.packed = self.prefix + struct.pack('<BB', self.start_register, self.number_registers)
            self.packed += struct.pack('<%sB' % len(self.data), *self.data)
            
        else: #All other types of command (W2, W3, W5, W6 have)
            self.packed = self.prefix + struct.pack('<BB', self.start_register, self.number_registers)
            self.packed += struct.pack('<%sH' % len(self.data), *self.data)
        
        return self.packed   
        
        
            
            
class AlpesResponse(AlpesMessage):
    def __init__(self, command_or_bytes):
        if isinstance(command_or_bytes, bytes):
            self.parce(command_or_bytes)
        elif isinstance(command_or_bytes, AlpesCommand):
            self.init_from_command(command_or_bytes)
            
            
    def init_from_command(self, command): 
        self.prefix = command.prefix
        self.start_register = command.start_register
        self.number_registers = command.number_registers
        self.data = command.data
        self.expected_size = len(self.pack())
            
            
    def pack(self):
        # Implemented only to calculate the expected size of the response message. 
        # Messages received from the hand have different format depending on their type.
        # For details, see "Protocole Com Main Robotisee". 
        if  self.prefix == PREFIXES.ECRITURE_REGISTRE:
            self.packed = self.prefix + struct.pack('<HH', self.start_register, self.number_registers)

        elif self.prefix == PREFIXES.LECTURE_REGISTRE:
            self.packed = self.prefix + struct.pack('<HH', self.start_register, self.number_registers)
            self.packed += struct.pack('<%sI' % self.number_registers, *[0 for d in range(self.number_registers)])
            
        else:
            self.packed = self.prefix + struct.pack('<BB', self.start_register, self.number_registers)
            self.packed += struct.pack('<%sH' % self.number_registers, *[0 for d in range(self.number_registers)])
   
        return self.packed   
        
        
    def parce(self, response):
        self.prefix = response[0:2]
        print(self.prefix)
        if  self.prefix == PREFIXES.LECTURE_REGISTRE:
            self.start_register   = struct.unpack('<H', response[2:4])
            self.number_registers = struct.unpack('<H', response[4:6])
            self.data             = struct.unpack('<%sI' % self.number_registers, response[6:])
            
        elif self.prefix == PREFIXES.ECRITURE_REGISTRE:
            self.start_register   = struct.unpack('<H', response[2:4])
            self.number_registers = struct.unpack('<H', response[4:6])
            self.data             = []

        else:
            self.start_register   = struct.unpack('<B', response[2:3])
            self.number_registers = struct.unpack('<B', response[3:4])
            self.data             = struct.unpack('<%sH' % self.number_registers, response[4:])
                        
        






# 0 UVAR_32 R/W Tous modes Non MODE_CMD_MOTEUR Mode de commande du moteur : (Arrêt, mode position, mode tension)
# 1 VAR_32 R/W Tous modes Non CONSIGNE_TENSION_POSITION Consigne moteur : Position (en mode position) / tension (en mode tension)
# 2 UVAR_32 R/W Tous modes Non LIMITE_COURANT Consigne de courant
# 3 UVAR_32 R/W Tous modes Oui LIMITE_COURANT_DEFAUT Consigne de courant par défaut à la mise sous tension
# 4 UVAR_32 R/W Non utilisé Oui LIMITE_COURANT_START_MOT Non utilisé
# 5 UVAR_32 R/W Non utilisé Oui TEMPS_DEMARRAGE_MOT Non utilisé
# 6 UVAR_32 R/W Position Oui DELAI_MODE_PI Consigne de temps pour passage en mode PI
# 7 VAR_32 R/W Position Oui DELTA_MODE_PI Consigne d'erreur pour passage en mode PI
# 8 UVAR_32 R/W Position Oui COEF_P
# Coefficient utilisé pour le calcul de la part de commande proportionnelle à
# l'écart
# 9 UVAR_32 R/W Position Oui COEF_I
# Coefficient utilisé pour le calcul de la part de commande proportionnelle au
# cumul des écarts
# 10 UVAR_32 R/W Position Oui COEF_D
# Coefficient utilisé pour le calcul de la part de commande proportionnelle à la
# différence entre l'écart actuel et l'écart précèdent
# 11 VAR_32 R Position Oui CONSIGNE_POSITION_MIN Valeur minimum de la consigne de position
# 12 VAR_32 R Position Oui CONSIGNE_POSITION_MAX Valeur maximum de la consigne de position
# 13 VAR_32 R/W Position Oui MIN_SORTIE_PWM Butée négative de la commande moteur
# 14 VAR_32 R/W Position Oui MAX_SORTIE_PWM Butée positive de la commande moteur
# 15 VAR_33 R/W Position Oui MIN_SOMME_ECARTS Butée négative du cumul des erreurs
# 16 VAR_34 R/W Position Oui MAX_SOMME_ECARTS Butée positive du cumul des erreurs
# 17 UVAR_32 R/W Non utilisé Oui TEMPS_DETECT_ROTATION Non utilisé
# 18 UVAR_32 R/W Non utilisé Oui POINTS_DETECT_ROTATION Non utilisé
# 19 UVAR_32 R Tous modes Oui DIR_MOTEUR_CODEUR Sens de commande du moteur et sens de comptage des tops codeur
# 20 UVAR_32 R/W Tous modes Oui TEMPS_CALCUL_VITESSE Période de calcul de la moyenne de vitesse
# 21 UVAR_32 R Non utilisé Oui RESERVE_RW2 Non utilisé
# 22 UVAR_32 R Non utilisé Oui RESERVE_RW3 Non utilisé
# 23 UVAR_32 R Non utilisé Oui RESERVE_RW4 Non utilisé
# 24 UVAR_32 R Tous modes Oui ID_DROITE_GAUCHE Identification main doit ou gauche
# 25 UVAR_32 R Tous modes Oui EMPLACEMENT_DIR_MOT_COD N° du registre contenant DIR_MOTEUR_CODEUR
# Electronique pour main robotisée 5/15 Document provisoire
# Registres internes Programme version 0.2