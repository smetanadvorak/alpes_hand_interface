import struct
from Alpes.Specification import *

  
class AlpesMessage():
    def __str__(self):
        s  = 'Alpes Message:\n'
        s += 'Type: %s\n' % str(self.prefix, 'utf-8')
        s += 'Start register: %d\n' % self.start_register
        s += 'Number of registers: %d\n' % self.number_registers
        s += 'Data (payload): ' + ' '.join('%s'* len(self.data)) % tuple(self.data)
        return s
        
        
      
class AlpesCommand(AlpesMessage):
    def __init__(self, prefix, start_register, number_registers, data = []):
        self.prefix = prefix #Type of command: WR, RD, W1 ... W6
        self.start_register = start_register
        self.number_registers = number_registers
        self.data = self.__check_data(number_registers, data) 
        self.expected_response_size = AlpesResponse(self).size
    
    
    
    def __check_data(self, number_registers, data):
        if self.prefix != PREFIXES.LECTURE_REGISTRE:
            if not isinstance(data, list):
                data = [data]
            if len(data) != number_registers:
                raise ValueError('Number of registers requested for writing does not match the length of provided data.')
        else:
            data = []
        return data
        
        
        
    def pack(self):
        # Messages sent to the hand have different format depending on their type.
        # For details, see "Protocole Com Main Robotisee". 
        if self.prefix == PREFIXES.ECRITURE_REGISTRE:
            self.packed = self.prefix + struct.pack('<HH', self.start_register, self.number_registers)
            self.packed += struct.pack('<%si' % len(self.data), *self.data)
            
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
            self.__unpack(command_or_bytes)
        elif isinstance(command_or_bytes, AlpesCommand):
            self.__init_from_command(command_or_bytes)
            
            
    def __init_from_command(self, command): 
        self.prefix = command.prefix
        self.start_register = command.start_register
        self.number_registers = command.number_registers
        self.data = command.data
        self.size = len(self.__pack())
            
            
    def __pack(self):
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
        
        
    def __unpack(self, response):
        self.prefix = response[0:2]
        if  self.prefix == PREFIXES.TEST:
            print('Test response received.')
        elif self.prefix == PREFIXES.LECTURE_REGISTRE:
            self.start_register   = struct.unpack('<H', response[2:4])
            self.number_registers = struct.unpack('<H', response[4:6])
            self.data             = list(struct.unpack('<%si' % self.number_registers, response[6:]))
            
        elif self.prefix == PREFIXES.ECRITURE_REGISTRE:
            self.start_register   = struct.unpack('<H', response[2:4])
            self.number_registers = struct.unpack('<H', response[4:6])
            self.data             = []

        else:
            self.start_register   = struct.unpack('<B', response[2:3])
            self.number_registers = struct.unpack('<B', response[3:4])
            self.data             = list(struct.unpack('<%sH' % self.number_registers, response[4:]))
                        
    
               