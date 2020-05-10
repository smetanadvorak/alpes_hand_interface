import serial, time
from AlpesSerial import AlpesSerial
from AlpesProtocol import *



class AlpesHand:
    def __init__(self, port = None):
        self.serial = AlpesSerial(port)
        self.left_or_right()
        #self.current_limit = [self.read_register(VOIE2MEMOIRE(i)+LIMITE_COURANT, 1).data[0] for i in VOIES.ALL]
        self.current_limit = self.read_registers_across(LIMITE_COURANT)
        print(self.current_limit)
       
       
    def write_registers_consecutively(self, first_register_position, number_of_registers, data):
        assert isinstance(data, list), 'Provided data should be a list, even in single value'
        assert len(data) == number_of_registers, 'Number of registers requested for writing does not match the length of provided data'
        command = AlpesCommand(PREFIXES.ECRITURE_REGISTRE, first_register_position, number_of_registers, data)        
        self.serial.write(command.pack())
        return AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
    
    
    def read_registers_consecutively(self, first_register_position, number_of_registers):
        command = AlpesCommand(PREFIXES.LECTURE_REGISTRE, first_register_position, number_of_registers, [])               
        self.serial.write(command.pack())
        return AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        
   
    def write_registers_across(self, register_id, data):
        assert isinstance(data, list) and len(data)==6, 'AlpesHand: write_registers_across(): data should be a list of six elements.'
        [self.write_registers_consecutively(VOIE2MEMOIRE(v) + register_id, 1, [data[v]]) for v in VOIES.ALL]        
        
        
    def read_registers_across(self, register_id):
        data = [self.read_registers_consecutively(VOIE2MEMOIRE(v) + register_id, 1).data[0] for v in VOIES.ALL]
        return data
        
       
    def left_or_right(self):
        command = AlpesCommand(PREFIXES.LECTURE_REGISTRE, 1000 + ID_DROITE_GAUCHE, 1)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        self.id = 'gauche' if response.data[0] else 'droite'
        return self.id
    
    
    def check_initialised(self):
        command = AlpesCommand(PREFIXES.LECTURE_REGISTRE, INITIALISATION, 1)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        return response.data[0] == 1
        
        
    def initialise(self):
        if self.check_initialised():
            print('Great! Hand already initialised.')
            return 0
        else:
            self.write_registers_consecutively(INITIALISATION, 1, [1])
            start_time = time.perf_counter()
            while time.perf_counter() - start_time < 60: #Give the hand a minute to initialise. If it doesn't, abort and return an error.
                if self.check_initialised():
                    print('Hand initialised!')
                    return 0
                else:
                    print('\rInitialisation in progress ...', end='')
                    time.sleep(1)
                
            raise 'Hand initialisation timeout (60 seconds) exceeded without the hand confirming the initialisation.'
        
             
    
    def write_positions(self, angles, motors = None):
        # Sends to the hand a command to rotate motor until reaching a specified angle.
        # Send angles as a list. If fingers not specified, angles should be a 6-element list (for all motors).
        if motors is None:
            assert isinstance(angles, list) and len(angles)==6, 'AlpesHand: write_osition(): When motors are not specified, command is applied to all motors, so that "angles" should be a list with len of 6.'
            motors = VOIES.ALL
        else:
            assert len(angles) == len(motors), 'AlpesHand: write_position(): if list of motors is specified, its length should be equal to that of the angles list.'
        
        for (i,m) in enumerate(motors):
            self.write_registers_consecutively( VOIE2MEMOIRE(m) + MODE_CMD_MOTEUR,
                                        len([MODE_CMD_MOTEUR, CONSIGNE_TENSION_POSITION]),
                                        [CONTROL_MODES.POSITION, angles[i]] )            
        return 0
        
    def write_tensions(self, tensions, motors = None):
        # Sends to the hand a command to apply specified tensions (in Volts) to the motors.
        # Send tensions as a list. If motors not specified, tensions should be a 6-element list (for all motors).
        if motors is None:
            assert isinstance(angles, list) and len(angles)==6, 'AlpesHand: write_tension(): When motors are not specified, command is applied to all motors, so that "angles" should be a list with len of 6.'
            motors = VOIES.ALL
        else:
            assert len(angles) == len(motors), 'AlpesHand: write_tension(): if list of motors is specified, its length should be equal to that of the angles list.'
        
        for (i,m) in enumerate(motors):
            if abs(tensions[i]) > TENSION_MAXIMALE_MOTEUR:
                print("Warning: value of requested tension exceeds its' maximum set in the Alpes Hand documentation (-11.5V, 11.5V), command not sent to the hand.")
            else:
                self.write_registers_consecutively( VOIE2MEMOIRE(m) + MODE_CMD_MOTEUR,
                                            len([MODE_CMD_MOTEUR, CONSIGNE_TENSION_POSITION]),
                                            [CONTROL_MODES.TENSION, tensions[i]] * 100)    
        return 0 

        
        
    def read_positions(self):
        command = AlpesCommand(PREFIXES.LECTURE_POSITION_CODEUR, 0, 6, self.current_limit)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        return response.data
        
        
    def read_velocities(self):
        command = AlpesCommand(PREFIXES.LECTURE_VITESSE_MOTEUR, 0, 6, self.current_limit)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        return response.data
           
        
    