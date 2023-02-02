
import os
import time
import typing
import struct

class I2CPacket:
    '''
    Contains functions that aim to abstract away all the functionality
    related to packets, mainly building it and verifying packet integrity
    Packet structure:
    Size of data                - Python type
    245 byte for data           - bytes
    1 byte for data length      - integer
    1 byte for status messages  - bytes
    4 bytes for checksum        - integer
    4 bytes for sequence number - integer
    1 byte for sender ID        - bytes
    '''

    struct_format: str = '=245sBcIIc'
    data_len: int = 245
    data_index: int = 0
    dlen_index: int = 1
    stat_index: int = 2
    par_index: int = 3
    seq_index: int = 4
    id_index: int = 5

    def create_pkt(data: bytes, size: int, status: str, 
                   sequence: int, ID: str):
        '''
        Builds a packet containing the specified data. Adds in checksum. 
        Returns bytes object for writing.
        '''
        # Check lengths of input. Return false if packing cannot be done
        if size > I2CPacket.data_len:
            return False

        # Create packet with zero checksum for calculation
        pkt_array = bytearray(struct.pack(I2CPacket.struct_format, 
                                data, size, status[:1].encode(),
                                          0, sequence, ID[:1].encode()))

        # Use the sum of the packet array to set the checksum
        pkt_array[247:251] = sum(pkt_array).to_bytes(4, 'little')

        # Convert to bytes object and return it
        pkt = bytes(pkt_array)
        
        return pkt

    def parse_pkt(pkt: bytes):
        '''
        Unpacks packet, returns resulting tuple
        '''
        return struct.unpack(I2CPacket.struct_format, pkt)

    def verify_pkt(pkt: bytes):
        '''
        Given a packet, calculates checksum, checks with provided checksum of 
        packet.
        Returns True if they match, False if they do not.
        '''
        # Convert to byte array
        pkt_array = bytearray(pkt)

        # Extract checksum from packet
        provided = int.from_bytes(pkt_array[247:251], 'little', signed=False)

        # Substitute checksum with all zeros
        pkt_array[247:251] = bytearray(4)

        # Calculate checksum
        calculated = sum(pkt_array)

        # Return True if matching, False otherwise
        if calculated == provided:
            return True
        else:
            return False

class Nano_I2C:
    '''
    Monitor program for the Nvidia Jetson.
    Acts as an interface for the I2C communication buffer.
    Programs that desire to communicate with the Pi controller
    need to request writes through here. The monitor
    program ensures there are no outstanding
    messages from the controller and writes said data
    to the buffer, or performs needed actions if
    commands from the Pi are in the buffer.
    '''

    buf: str = '/sys/bus/i2c/devices/0-0064/slave-eeprom'
    blocksize: int = 256
    timewait: float = 0.2 # Time delay to help with data transmission
    
    pkt_self_id: str = 'J'           # This system's packet ID
    pkt_targ_id: str = 'P'           # The target packet ID (RPi)

    def __init__(self):
        self.log = open('logfile', 'w')
        self.vision = False
        print('Monitor program running')

    def write_pkt(self, pkt):
        '''
        Handles all writes to the eeprom buffer. Turns incoming data to bytes
        datatype for writing.
        Data can be of the type str, bytes, or a number
        '''
        # If the data is already in bytes, do nothing
        if type(data) == bytes:
            pass

        # Otherwise if the data is a string, encode it with UTF-8
        elif type(data) == str:
            data = data.encode(encoding='UTF-8', errors='replace')

        # Otherwise try to convert it to a bytes object
        else:
            try:
                data = bytes(data)

            # If this fails, return false
            except:
                return False

        with open(self.buf, 'wb') as buf:
            buf.write(data)

        # Return true to let caller know write was successful
        return True
    
    def read_pkt(self):
        '''
        Reads from the eeprom buffer. 
        Returns the data as a bytes object. 
        '''
        # Open buffer and return first 256 bytes
        with open(self.buf, 'rb') as buf:
            return buf.read(self.blocksize)
   
def main():
    bus = 1 # bus number 
    address = 0x50 # device address

    i2c = Nano_I2C(bus, address) # bus number and device address might need to change

    # Test write and read byte
    value = 0x42
    i2c.write_byte(value)
    read_value = i2c.read_byte()
    print("Received value: 0x{:02X}".format(read_value))

    # Test writing a packet
    task = "Sen"
    success = 0x01
    data = bytearray(245)
    packet = I2CPacket.create_packet(task, success, data)
    register = 0x00
    i2c.write_packet(register, packet)
   
    # Test reading a packet
    task, success, data = i2c.read_packet(register)
    print("Read task: {}, success: {}, data: {}".format(task, success, data))
