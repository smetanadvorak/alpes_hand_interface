import serial, time
from Alpes.Specification import *
from Alpes.Serial import AlpesSerial
from Alpes.Protocol import AlpesResponse, AlpesCommand


class AlpesHand:
    def __init__(self, port = None):
        try:
            self.serial = AlpesSerial(port) # Instantiate the serial connection
        except ConnectionError:
            self.serial = None
            raise
        self.left_or_right()       # Figure out if this is the right or the left hand
        self.set_current_limits()  # Set default current limit

    def __del__(self):
        if not isnone(self.serial):
            self.set_mode(MODE_CMD_MOTEUR.STOP)
            self.set_current_limits([0]*6) # If this software object gets destroyed in case of an error or an interrupt,
                                           # secure the hand first by setting all current limits to zero.
                                           # This way, motors won't be able to proceed with a possibly erroneous command.
                                           # If the hand is stuck in some bad position and you stopped the execution by ctrl-c,
                                           # switch off and on the hand, then start over.

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
        self.id = 'left' if response.data[0]==2 else 'right'
        return self.id


    @classmethod
    def two_hands(cls):
        # This is declared as a @classmethod because we need it to work for child classes too.
        ports = AlpesSerial.find_ports()
        if len(ports) != 2:
            raise ConnectionError('Could not find the two hands in the list of serial ports. Check if USB and power cables are inserted properly. Here is the port(s) that I found: %s' % ports)
        else:
            left_hand  = cls(ports[0])
            right_hand = cls(ports[1])
            if left_hand.left_or_right() == 'right':
                left_hand, right_hand = right_hand, left_hand
        return left_hand, right_hand

    #################################################################################
    ############################## COMMAND FUNCTIONS ################################
    #################################################################################
    def check_command(self, vals, motors, max_values, min_values=[0]*6):
        if motors is None:
            if not (isinstance(vals, list) and len(vals)==6) :
                message = 'Error: when it is not specified to which motors to apply, the command is applied to all motors, so that input should be a six-element list. Command was not sent to the hand.\n'
                return False, message
            motors = VOIES.ALL
        else:
            if len(vals) != len(motors):
                message = 'Error: when list of motors is specified, its length should be equal to that of the command list. Command was not sent to the hand.\n'
                return False, message

        if any([val > max_values[motors[i]] for (i,val) in enumerate(vals)]):
            message = "Error: at least one of the requested values exceeds its maximum set in the Alpes Hand documentation or by this software. Command was not sent to the hand.\n"
            return False, message
        if any([val < min_values[motors[i]] for (i,val) in enumerate(vals)]):
            message = "Error: at least one of the requested value is below its maximum set in the Alpes Hand documentation or by this software. Command was not sent to the hand.\n"
            return False, message
        return True, ''


    def write_positions(self, vals, motors = None):
        # Check the passed values for correctness
        correct, message = self.check_command(vals, motors, MAXIMAL_MOTOR_POSITIONS, [0] * 6)
        if not correct:
            details = "Note: Maximal rotation angles reachable by motors in POSITION control mode are %s. Passed list is %s" % (MAXIMAL_MOTOR_POSITIONS, vals)
            raise ValueError(message + details)
        if motors is None:
            motors = VOIES.ALL
        for (i,m) in enumerate(motors):
            self.__write_registers_consecutively( VOIE2MEMOIRE(m) + REGISTRES.MODE_CMD_MOTEUR, 2,
                                                 [MODE_CMD_MOTEUR.POSITION,  int(vals[i])] )
        return 0


    def write_tensions(self, vals, motors = None):
        # Check the passed values for correctness
        correct, message = self.check_command(vals, motors, [MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION] * 6, [-MOTORSPEC.MAXIMAL_ABSOLUTE_TENSION] * 6)
        if not correct:
            details = "Note: Maximal negative and positive tension specified in the Alpes Hand documentation are -11.5V, 11.5V."
            raise ValueError(message + details)
        if motors is None:
            motors = VOIES.ALL
        # If everything is ok, send the command
        for (i,m) in enumerate(motors):
            self.__write_registers_consecutively( VOIE2MEMOIRE(m) + REGISTRES.MODE_CMD_MOTEUR, 2,
                                                [MODE_CMD_MOTEUR.TENSION, int(vals[i] * 100)])
        return 0


    def set_current_limits(self, vals = [750] * 6, motors = None):
        # Check the passed values for correctness
        correct, message = self.check_command(vals, motors, [CONTROLE_COURANT.LIMITE_COURANT_MAX] * 6)
        if not correct:
            details = "Note: Maximal current limit, according to the motor specification, is CONTROLE_COURANT.LIMITE_COURANT_MAX = 750."
            raise ValueError(message + details)
        if motors is None:
            motors = VOIES.ALL
        # If everything is ok, send the command
        for (i,m) in enumerate(motors):
            self.__write_registers_consecutively( VOIE2MEMOIRE(m) + REGISTRES.LIMITE_COURANT, 1, [int(vals[i])])

        self.current_limit = vals
        return 0

    def set_mode(self, mode = MODE_CMD_MOTEUR.POSITION):
        if mode < 0 or mode > 2:
            raise ValueError('Incorrect motor mode specified. Motor mode can take the following values: 0 - no motion, 1 - position, 2 - tension.')
        self.write_registers_across(REGISTRES.MODE_CMD_MOTEUR, [mode]*6)

    #################################################################################
    ########################### MEASUREMENTS FUNCTIONS ##############################
    #################################################################################
    def read_positions(self):
        command = AlpesCommand(PREFIXES.LECTURE_POSITION_CODEUR, 0, 6, self.current_limit)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(command.expected_response_size))
        # Sometimes when rotating backwards, motors go slightly beyond the origin point of rotation,
        # which results in values like 65535 that are, in fact, impossible.
        # In my opinion, it only clutters the user's data and therefore I filter it out.
        result = list(map(lambda x: x if x < 65500 else 0, response.data))
        limits = [21000, 19000, 43000, 43000, 43000, 43000]
        result = list(map(lambda x,y: x if x < y else y, result, limits))
        return result


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
        if not isinstance(data, list):
            raise ValueError('Provided data should be a list, even in single value')
        if len(data) != number_of_registers:
            raise ValueError('Number of registers requested for writing does not match the length of provided data')
        command = AlpesCommand(PREFIXES.ECRITURE_REGISTRE, first_register_position, number_of_registers, data)
        self.serial.write(command.pack())
        return AlpesResponse(self.serial.read(command.expected_response_size))

    def __read_registers_consecutively(self, first_register_position, number_of_registers):
        command = AlpesCommand(PREFIXES.LECTURE_REGISTRE, first_register_position, number_of_registers, [])
        self.serial.write(command.pack())
        return AlpesResponse(self.serial.read(command.expected_response_size)).data


    def write_register(self, motor, register_id, data):
        return self.__write_registers_consecutively(VOIE2MEMOIRE(motor) + register_id, 1, [data])

    def read_register(self, motor, register_id):
        return self.__read_registers_consecutively(VOIE2MEMOIRE(motor) + register_id,  1)


    def write_registers_across(self, register_id, data):
        if not (isinstance(data, list) and len(data)==6):
            raise ValueError('AlpesHand: write_registers_across(): data should be a list of six elements.')
        [self.__write_registers_consecutively(VOIE2MEMOIRE(v) + register_id, 1, [data[v]]) for v in VOIES.ALL]

    def read_registers_across(self, register_id):
        return [self.__read_registers_consecutively(VOIE2MEMOIRE(v) + register_id, 1)[0] for v in VOIES.ALL]


    def read_memory(self):
        # Full memory dump is a list of six objects of type REGISTRES with fields filled by the hand's memory
        self.memory = [REGISTRES() for i in VOIES.ALL]
        # Get list of the attributes of type REGISTRES to project memory onto the REGISTRES objects.
        attributes  = [s for s in dir(REGISTRES()) if not s.startswith('__') and not callable(getattr(REGISTRES(), s))]
        # For each 'voie' (motor channel)
        for (i,voie) in enumerate(self.memory):
            voie_dump = self.__read_registers_consecutively(VOIE2MEMOIRE(i), 42) #Total of 42 registers per motor channel (See 'Registres Main Robotisee.pdf')
            for attr in attributes:
                memory_position = getattr(REGISTRES(), attr)
                setattr(voie, attr, voie_dump[memory_position])
        return self.memory


    def read_velocities_and_directions(self):
        # Asks the hand and returns angular velocity of the motors in turns/min
        # ATTENTION: this method is left here in case someone wants to re-test it.
        # Previous attempts to receive the direction of rotation from the hand were not successful: contents of DIR_MOTEUR_CODEUR do not change in function of direction.
        command = AlpesCommand(PREFIXES.LECTURE_VITESSE_MOTEUR, 0, 6, self.current_limit)
        self.serial.write(command.pack())
        response = AlpesResponse(self.serial.read(command.expected_response_size)).data
        # Getting sign of velocity is optional since it requires additional reading procedure
        # and may slow down the acquisition. In most of the cases, sign can be derived from the command.
        directions = self.read_registers_across(REGISTRES.DIR_MOTEUR_CODEUR)
        #print('AlpesHand.read_velocities_and_directions:', directions)
        signs = [(d & 2) > 0 for d in directions] # Read second bit of the response
        for i in range(len(response)):
            if not signs[i]:
                response[i] *= -1
        return response
