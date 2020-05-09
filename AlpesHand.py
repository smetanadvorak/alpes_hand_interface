import serial, time
from AlpesSerial import AlpesSerial
from AlpesProtocol import *



class AlpesHand:
    def __init__(self, port = None):
        self.serial = AlpesSerial(port)
       
    def left_or_right(self):
        pass
    
    def initialise(self):
        command_init = AlpesCommand(PREFIXES.ECRITURE_REGISTRE, 100, 1, 1)
        self.serial.write(command_init.pack())
        dummy = AlpesResponse(self.serial.read(AlpesResponse(command_init).expected_size)) #Flush serial data
        
        command_check = AlpesCommand(PREFIXES.LECTURE_REGISTRE, 100, 1)
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < 60: #Give the hand a minute to initialise. If it doesn't, abort and return an error.
            self.serial.write(command_check.pack())
            response = AlpesResponse(self.serial.read(AlpesResponse(command_check).expected_size))
            if response.data[0] == 1:
                print('Hand initialised!')
                return 0
            else:
                print('\rInitialisation in progress ...', end='')
                time.sleep(1)
                
        raise 'Hand initialisation timeout (60 seconds) exceeded without the hand confirming the initialisation.'
        
        
    def set_control_mode(self, mode):
        # Sets all motors to selected control mode. Available modes: CONTROL_MODE.STOP, CONTROL_MODE.TENSION, CONTROL_MODE.POSITION
        # ToDo: maybe it would make sense to set it separately for each finger.
        command = AlpesCommand(PREFIXES.ECRITURE_MODE_CMD_MOTEUR, 0, 6, [mode]*6)
        self.serial.write(command.pack())
        self.control_mode = mode
        return AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        
    
    def write_motor_position(self, angles, motor = None):
        # Sends to the hand a command to rotate motor until reaching a specified angle.
        # Send angles as a list. If fingers not specified, angles should be a 6-element list (for all motors).
        assert self.control_mode == CONTROL_MODE.POSITION, 'AlpesHand: write_motor_position(): control mode should be set to "POSITION" by method "set_position_control_mode()".'      
        if motor is not None: 
            command = AlpesCommand(PREFIXES.ECRITURE_CONSIGNE_TENSION_POSITION, motor, 1, angles)
        else:
            assert len(angles) == 6, 'AlpesHand: write_motor_position(): if "finger" is not specified, "angles" is assumed to be a 6-elements list (one for each finger)'
            command = AlpesCommand(PREFIXES.ECRITURE_CONSIGNE_TENSION_POSITION, 0, 6, angles)
        self.serial.write(command.pack())
        return AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        
        
    def read_motor_position(self, motor = None):
        if motor is not None: 
            command = AlpesCommand(PREFIXES.ECRITURE_MODE_CMD_MOTEUR, motor, 1, [self.control_mode])
        else:
            command = AlpesCommand(PREFIXES.ECRITURE_MODE_CMD_MOTEUR, 0, 6, [self.control_mode]*6)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(AlpesResponse(command).expected_size))
        return response.data
        
        
    def set_mixed_control_mode(self, modes):
        # To be implemented if ever needed. Advice: define a 'motor' class and keep an array of 6 instances of this class interfacing each of the 6 motors.
        raise 'Not implemented.'   
        
    