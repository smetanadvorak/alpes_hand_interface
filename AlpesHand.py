import serial, time
from AlpesSerial import AlpesSerial
from AlpesProtocol import *
from AlpesSpecification import *

class AlpesHand:
    def __init__(self, port = None):
        self.serial = AlpesSerial(port)
        self.left_or_right()
        self.set_current_limits()
        self.current_limit = self.read_registers_across(REGISTRES.LIMITE_COURANT)
       
        
    def initialise(self):
        if self.check_initialised():
            print('Great! Hand already initialised.')
            return 0
        else:
            self.__write_registers_consecutively(REGISTRE_INITIALISATION, 1, [1])
            start_time = time.perf_counter()
            while time.perf_counter() - start_time < 60: #Give the hand a minute to initialise. If it doesn't, abort and return an error.
                if self.check_initialised():
                    print('Hand initialised!')
                    return 0
                else:
                    print('\rInitialisation in progress ...', end='')
                    time.sleep(1)                
            raise 'Hand initialisation timeout (60 seconds) exceeded without the hand confirming the end of initialisation.'
    
    def check_initialised(self):
        command = AlpesCommand(PREFIXES.LECTURE_REGISTRE, REGISTRE_INITIALISATION, 1)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(command.expected_response_size))
        return response.data[0] == 1
        

    def left_or_right(self):
        command = AlpesCommand(PREFIXES.LECTURE_REGISTRE, 1000 + REGISTRES.ID_DROITE_GAUCHE, 1)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(command.expected_response_size))
        self.id = 'gauche' if response.data[0] else 'droite'
        return self.id   
        
         
             
    #################################################################################  
    ############################## COMMAND FUNCTIONS ################################        
    #################################################################################   
    def write_positions(self, vals, motors = None):
        # Sends to the hand a command to rotate motor until reaching a specified angle.
        # Send angles as a list. If fingers not specified, vals should be a 6-element list (for all motors).
        if motors is None:
            if not (isinstance(vals, list) and len(vals)==6) :
                print('AlpesHand.write_positions(): Error: When motors are not specified, command is applied to all motors, so that "vals" should be a list with len of 6.')
                return 1
            motors = VOIES.ALL
        else:
            if len(vals) != len(motors):
                print('AlpesHand.write_positions(): Error: if list of motors is specified, its length should be equal to that of the angles list.')
                return 1     

        if any([abs(val) > MAXIMAL_MOTOR_POSITIONS[i] for (i,val) in enumerate(vals)]):
            print("AlpesHand.write_positions(): Error: value of requested position exceeds its possible maximum (%s), command not sent to the hand." % MAXIMAL_MOTOR_POSITIONS)
            return 1   
        if any([    val  < 0                        for val in vals]):
            print("AlpesHand.write_positions(): Error: value of requested positoin cannot be negative, command not sent to the hand.")
            return 1 
                    
        for (i,m) in enumerate(motors):
            self.__write_registers_consecutively( VOIE2MEMOIRE(m) + REGISTRES.MODE_CMD_MOTEUR, 2,
                                                [MODE_CMD_MOTEUR.POSITION,   int(vals[i])] )            
        return 0
     
        
    def write_tensions(self, vals, motors = None):
        # Sends to the hand a command to apply specified tensions (in Volts) to the motors.
        # Send tensions as a list. If motors not specified, vals should be a 6-element list (for all motors).
        # First, check all kinds of stuff: 
        if motors is None:
            if not (isinstance(vals, list) and len(vals)==6) :
                print('AlpesHand.write_tension(): Error: When motors are not specified, command is applied to all motors, so that "tensions" should be a list with len of 6.')
                return 1
            motors = VOIES.ALL
        else:
            if len(vals) != len(motors):
                print('AlpesHand.write_tension(): Error: if list of motors is specified, its length should be equal to that of the tensions list.')
                return 1
        
        if any([abs(val) > MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION for val in vals]):
            print("AlpesHand.write_tensions(): Error: value of requested tension exceeds its maximum set in the Alpes Hand documentation (-11.5V, 11.5V), command not sent to the hand.")
            return 1
            
        # If everything is ok, send the command
        for (i,m) in enumerate(motors):
            self.__write_registers_consecutively( VOIE2MEMOIRE(m) + REGISTRES.MODE_CMD_MOTEUR, 2,
                                                [MODE_CMD_MOTEUR.TENSION, int(vals[i] * 100)])    
        return 0 
        
        
    def set_current_limits(self, vals = [750] * 6, motors = None):
        if motors is None:
            if not (isinstance(vals, list) and len(vals)==6) :
                print('AlpesHand.set_current_limits(): Error: When motors are not specified, command is applied to all motors, so that "tensions" should be a list with len of 6.')
                return 1
            motors = VOIES.ALL
        else:
            if len(vals) != len(motors):
                print('AlpesHand.set_current_limits(): Error: if list of motors is specified, its length should be equal to that of the tensions list.')
                return 1
        
        if any([abs(val) > CONTROLE_COURANT.LIMITE_COURANT_MAX for val in vals]):
            print("AlpesHand.set_current_limits(): Error: value of requested tension exceeds its maximum set in the Alpes Hand documentation (0.211 A, or 4000 in LIMITE_COURANT points), command not sent to the hand.")
            return 1
        if any([    val  < 0                        for val in vals]):
            print("AlpesHand.set_current_limits(): Error: value of requested positoin cannot be negative, command not sent to the hand.")
            return 1             
            
        # If everything is ok, send the command
        for (i,m) in enumerate(motors):
            self.__write_registers_consecutively( VOIE2MEMOIRE(m) + REGISTRES.LIMITE_COURANT, 1, [int(vals[i])])    
        
        self.current_limit = vals
        return 0         
     
         
        
    def get_memory_dump(self):
        # Full memory dump is a list of six objects of type REGISTRES with fields filled by the hand's memory
        self.memory_dump = [REGISTRES() for i in VOIES.ALL]
        # Get list of the attributes of type REGISTRES to project memory onto the REGISTRES objects.
        attributes  = [s for s in dir(REGISTRES()) if not s.startswith('__') and not callable(getattr(REGISTRES(), s))]
        # For each 'voie' (motor channel)
        for (i,voie) in enumerate(self.memory_dump):
            voie_dump = self.__read_registers_consecutively(VOIE2MEMOIRE(i), 42) #Total of 42 registers per motor channel (See 'Registres Main Robotisee.pdf')
            for attr in attributes:
                memory_position = getattr(REGISTRES(), attr)
                setattr(voie, attr, voie_dump[memory_position])
        
            
        
    #################################################################################  
    ########################### MEASUREMENTS FUNCTIONS ##############################        
    #################################################################################         
    def read_positions(self):
        command = AlpesCommand(PREFIXES.LECTURE_POSITION_CODEUR, 0, 6, self.current_limit)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(command.expected_response_size))
        return response.data
        
        
    def read_velocities(self): #, get_directions = 'False'):
        # Asks the hand and returns angular velocity of the motors in turns/min
        command = AlpesCommand(PREFIXES.LECTURE_VITESSE_MOTEUR, 0, 6, self.current_limit)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(command.expected_response_size)).data        
        return [d/100 for d in response] # Conversion to turns/min
        
        
    #################################################################################
    ##################### REGISTER READING/WRITING FUNCTIONS ########################
    #################################################################################   
    def __write_registers_consecutively(self, first_register_position, number_of_registers, data):
        assert isinstance(data, list), 'Provided data should be a list, even in single value'
        assert len(data) == number_of_registers, 'Number of registers requested for writing does not match the length of provided data'
        command = AlpesCommand(PREFIXES.ECRITURE_REGISTRE, first_register_position, number_of_registers, data)        
        self.serial.write(command.pack())
        return AlpesResponse(self.serial.read(command.expected_response_size))
    
    
    def __read_registers_consecutively(self, first_register_position, number_of_registers):
        command = AlpesCommand(PREFIXES.LECTURE_REGISTRE, first_register_position, number_of_registers, [])               
        self.serial.write(command.pack())
        return AlpesResponse(self.serial.read(command.expected_response_size)).data
        
   
    def write_registers_across(self, register_id, data):
        assert isinstance(data, list) and len(data)==6, 'AlpesHand: write_registers_across(): data should be a list of six elements.'
        [self.__write_registers_consecutively(VOIE2MEMOIRE(v) + register_id, 1, [data[v]]) for v in VOIES.ALL]        
        
        
    def read_registers_across(self, register_id):
        return [self.__read_registers_consecutively(VOIE2MEMOIRE(v) + register_id, 1)[0] for v in VOIES.ALL]
        
 
           
           
           
           
           
# Saved for later
#     def read_velocities(self): #, get_directions = 'False'):
#         # Asks the hand and returns angular velocity of the motors in turns/min
#         command = AlpesCommand(PREFIXES.LECTURE_VITESSE_MOTEUR, 0, 6, self.current_limit)
#         self.serial.write(command.pack())
#         response = AlpesResponse(self.serial.read(command.expected_response_size)).data
#         # Getting sign of velocity is optional since it requires additional reading procedure
#         # and may slow down the acquisition. In most of the cases, sign can be derived from the command.
#         if get_directions:
#             directions = self.read_registers_across(REGISTRES.DIR_MOTEUR_CODEUR)
#             signs = [(d & 2) > 0 for d in directions] # Read second bit of the response
#             print(directions, signs)
#             for i in range(len(response)):
#                 if not signs[i]:
#                     response[i] *= -1    
    
    
    
    def check_command(self, vals, motors, min_values, max_values):
        if motors is None:
            if not (isinstance(vals, list) and len(vals)==6) :
                message = 'Error: when it is not specified to which motors to apply, the command is applied to all motors, so that input should be a six-element list. Command was not sent to the hand.'
                return False, message
            motors = VOIES.ALL
        else:
            if len(vals) != len(motors):
                message = 'Error: when list of motors is specified, its length should be equal to that of the command list. Command was not sent to the hand.'
                return False, message
        
        if any([val > max_values[i] for (i,val) in enumerate(vals)]):
            message = "Error: at least one of the requested values exceeds its maximum set in the Alpes Hand documentation or by this software. Command was not sent to the hand."
            return False, message
        if any([val < min_values[i] for (i,val) in enumerate(vals)]):
            message = "Error: at least one of the requested value is below its maximum set in the Alpes Hand documentation or by this software. Command was not sent to the hand."
            return False, message
        return True, ''