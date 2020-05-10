import serial
from serial.tools.list_ports import comports
from CRC16 import crc16
import struct

__test__ = False


class AlpesSerial:
    
    def __init__(self, port = None):
        self.connect_serial(port)
           
                    
    def write(self, command):
        command += struct.pack('<BB', *crc16(command)) # Add CRC16 code to the payload (last two bytes)
        if not __test__:
            self.serial.write(command) # Write to the serial
            
        if __debug__:
            print('\nAlpesSerial: write(): Command sent to the hand:', command)
    
    
    
    def read(self, n_bytes):
        if not __test__:
            response = self.serial.read(n_bytes+2) #Plus 2 for CRC code
        else:
            response = b'test__'
                        
        if __debug__:
            print('\nAlpesSerial:  read(): Response received from the hand: ', response)
        return response[:-2] #CRC check is omitted
        
        
        
    def connect_serial(self, port = None):
        if port is None:    
            ports = self.find_ports()
            if len(ports) > 1:
                print('In cases when two hands communiction is required, please specify the port names manually as: "hand1=AlpesHand(portname1);  hand2=AlpesHand(portname12)". Port names are listed above.')
                return False
            elif len(ports) == 0:
                return False
            else:
                port = ports[0]
        
        if not __test__:
            self.serial = serial.Serial(port, baudrate=460800, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=False,
                                 dsrdtr=False, timeout=1, writeTimeout=1)
            
        self.port = port
    
    @staticmethod   
    def find_ports():
        ports = [port[0] for port in comports() if port[1] == 'FT232R USB UART']

        if len(ports) == 0:
            print('Could not find a serial port connection associated to the hand. Try specifying it by passing its name when initialising an AlpesHand object!')
            raise
        elif len(ports) == 1:
            print('Found one serial port connection associated to the hand at %s' % ports[0])
        elif len(ports) == 2:
            print('Found two serial port connections associated to hands at %s and %s' % (ports[0], ports[1]))
        elif len(ports) >  2:
            print('Found more than two serial port connections associated to FT232UART at ', end='')
            print([port[2] for port in ports])
            print('This is an unusual situation, are you having three or more serial devices connected? In this case, you may need to pass hadns'' addresses to AlpesHand manually')
        return ports



