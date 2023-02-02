


import os
import time
import typing
import struct
import pylibi2c

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
        return calculated == provided

class Nano_I2CBus:
    '''
    I2C bus object for the Jetson to communicate with the Raspberry Pi.
    '''
    
    blocksize: int = 256    # Max bytes capable of sending
    timewait: float = 0.2

    pkt_self_id: str = 'J'           # This system's packet ID
    pkt_targ_id: str = 'P'           # The target packet ID (RPi)

    def __init__(self, target = 0x64, dev = '/dev/i2c-1'):
        '''
        Initializes the bus using the imported library.
        
        Default device address for Jetson is 
        Default device for I2C on Pi is 
        '''
        self.target = target # I2C adress of the target(Pi) being used on Pi
        self.dev = dev       # I2C bus being used on the Jetson 
        self.bus = pylibi2c.I2CDevice(self.dev, self.target)

    def write_pkt(self, pkt):
        '''
        Takes a string, converts it to bytes to send across I2C to the 
        specified target.

        msg limited to 256 bytes.

        Returns number bytes sent
        '''
        # If pkt is already in bytes, do nothing
        if type(pkt) == bytes:
            pass

        # Otherwise if the data is a string, encode it with UTF-8
        elif type(pkt) == str:
            pkt = pkt.encode(encoding='UTF-8', errors='replace')

        # Otherwise try to convert it to a bytes object
        else:
            try:
                pkt = bytes(pkt)

            # If this fails, return false
            except:
                return False

        return self.bus.write(0x0, pkt)

    def read_pkt(self, size: int = blocksize):
        '''
        Reads the message sent from Pi's I2C.

        size limited to 256 bytes.
        '''
        # If size is too big, throw an exception
        if size > self.blocksize:
            raise ValueError
        
        # Read requested size, return bytes object
        return self.bus.read(0x0, size)


def main():
    # Initialize the I2C bus
    i2c = Nano_I2CBus()

    # creating packet content
    data = b'Hello World!'
    size = len(data)
    status = 'S'
    sequence = 12345
    ID = 'J'
    
    # Test writing a packet
    pkt = I2CPacket.create_pkt(data, size, status, sequence, ID)
    bytes_sent = i2c.write_pkt(pkt)
    
    if bytes_sent == False:
        print('Packet creation failed!')
    else:
        print(f'{bytes_sent} bytes sent!')
    
    # Test reading a packet
    data_received = i2c.read_pkt()
    if len(data_received) == 0:
        print('No data received!')
    else:
        # Verify the received packet
        if I2CPacket.verify_pkt(data_received) == False:
            print('Packet corrupted!')
        else:
            # Unpack the received packet
            unpacked = I2CPacket.parse_pkt(data_received)
            print(f'Data received: {unpacked[0].decode()}')

if __name__ == '__main__':
    main()
