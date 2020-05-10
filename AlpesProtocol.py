import struct
 
# Field names are in French to match the Alpes Instruments' official documentation
class PREFIXES:
    ECRITURE_REGISTRE                   = bytearray([ord('W'), ord('R')])
    ECRITURE_MODE_CMD_MOTEUR            = bytearray([ord('W'), ord('1')])
    ECRITURE_CONSIGNE_TENSION_POSITION  = bytearray([ord('W'), ord('2')])
    ECRITURE_LIMITE_COURANT             = bytearray([ord('W'), ord('3')])
    
    LECTURE_REGISTRE                    = bytearray([ord('R'), ord('D')])
    LECTURE_POSITION_CODEUR             = bytearray([ord('W'), ord('3')])
    LECTURE_VITESSE_MOTEUR              = bytearray([ord('W'), ord('6')])



class VOIES:
    ALL             = [0,1,2,3,4,5]
    POUCE_ROTATION  = 0
    POUCE           = 1
    INDEX           = 2
    MAJEUR          = 3
    ANNULAIRE       = 4
    AURICULAIRE     = 5  
   
   
    
def VOIE2MEMOIRE(voie):
    return 1000 * (voie + 1) 
    
    
    
class CONTROL_MODES:
    STOP = 0
    POSITION = 1
    TENSION = 2



# Registers (see table "LISTE DES REGISTRES DE CONSIGNES ET DE PARAMETRAGE" of "Registre Main Robotisee.pdf")
MODE_CMD_MOTEUR             = 0
CONSIGNE_TENSION_POSITION   = 1
LIMITE_COURANT              = 2
LIMITE_COURANT_DEFAUT       = 3

ID_DROITE_GAUCHE            = 24
POSITION_CODEUR             = 26
VITESSE_MOTEUR              = 27

INITIALISATION              = 100

# Other constants
TENSION_MAXIMALE_MOTEUR     = 11.5
  
  
  
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
            
        elif self.prefix == PREFIXES.ECRITURE_MODE_CMD_MOTEUR: 
            self.packed = self.prefix + struct.pack('<BB', self.start_register, self.number_registers)
            self.packed += struct.pack('<%sB' % len(self.data), *self.data)
            
        else: #All other types of command (W2, W3, W5, W6)
            self.packed = self.prefix + struct.pack('<BB', self.start_register, self.number_registers)
            self.packed += struct.pack('<%sH' % len(self.data), *self.data)
        
        return self.packed   
        
        
            
            
class AlpesResponse(AlpesMessage):
    def __init__(self, command_or_bytes):
        if isinstance(command_or_bytes, bytes):
            self.unpack(command_or_bytes)
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
        
        
    def unpack(self, response):
        self.prefix = response[0:2]
        if  self.prefix == PREFIXES.LECTURE_REGISTRE:
            self.start_register   = struct.unpack('<H', response[2:4])
            self.number_registers = struct.unpack('<H', response[4:6])
            self.data             = list(struct.unpack('<%sI' % self.number_registers, response[6:]))
            
        elif self.prefix == PREFIXES.ECRITURE_REGISTRE:
            self.start_register   = struct.unpack('<H', response[2:4])
            self.number_registers = struct.unpack('<H', response[4:6])
            self.data             = []

        else:
            self.start_register   = struct.unpack('<B', response[2:3])
            self.number_registers = struct.unpack('<B', response[3:4])
            self.data             = list(struct.unpack('<%sH' % self.number_registers, response[4:]))
                        
