import os
import time
import typing
import struct
import lidar

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

class Monitor:
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

    def write_log(self, msg: str):
        date = time.asctime()

        self.log.write(date + ': ' + msg + '\n')

    def check_buf(self):
        '''
        Checks inside the buffer to see if has anything written inside.
        Specifically we are checking for any keywords that do system-type tasks
        such as turning the vision system on or off.
        '''
        pkt = self.wait_response()

        if not pkt:
            return

        # If the packet isn't the target ID (pi) and it isn't a command
        if (pkt[I2CPacket.id_index].decode() != self.pkt_targ_id) or (pkt[I2CPacket.stat_index] != b'c'):
            return

        print('Command received:')

        msg = pkt[I2CPacket.data_index].decode().strip('\0')

        print(msg)
        
        if msg == 'vision start':
            if not self.vision:
                # Start vision system
                lidar.start_vision_pipe(640,480,640,480)
                self.vision = True

            tempresp = 'Jetson Response'.encode()
            self.write_pkt(tempresp, 't', pkt[I2CPacket.seq_index] + 1)


        elif msg  == 'vision stop':
            if self.vision:
                # Stop vision system
                lidar.end_vision_pipe()
                self.vision = False

            tempresp = 'Jetson Response'.encode()
            self.write_pkt(tempresp, 't', pkt[I2CPacket.seq_index] + 1)


        elif msg == 'get object':
            # Get list of object information (list of objects)
            objects = lidar.object_detection()

            # if there are objects detected
            if objects:
                flag = True
                dist = objects[0][0]
                str = bytes(objects[0][1].encode())

                # Pack data into struct
                data = struct.pack('?f6s', flag, dist, str)
                
                # Send object data packet
                self.write_pkt(data, 'd', pkt[I2CPacket.seq_index])


            # if no objects were detected
            else:
                flag = False
                dist = 0.0
                str = bytes(''.encode())

                # Pack data into struct
                data = struct.pack('?f6s', flag, dist, str)

                # Send object data packet
                self.write_pkt(data, 'd', pkt[I2CPacket.seq_index])

        elif msg == 'take picture':
            lidar.save_rgb_frame()

        elif msg == 'take depth image':
            lidar.save_depth_frame()

        elif msg[:12] == 'file receive':
            self.write_log('receiving file: ' + msg[13:])

            print('receiving file: ' + msg[13:])
                
            # Receive a file from the Pi, specified by the 3rd token
            self.file_receive(msg[13:])

        elif msg[:9] == 'file send':
            self.write_log('sending file: ' + msg[10:])

            print('Sending file: ' + msg[10:])

            # Send a file to the Pi, specified by the 3rd token
            self.file_send(msg[10:])

        elif msg == 'power low':
            print('Entering low power mode')
            os.system('echo "low" > powerstatus')
            tempresp = 'Jetson Response'.encode()
            self.write_pkt(tempresp, 't', pkt[I2CPacket.seq_index] + 1)


        elif msg == 'power high':
            print('Entering high power mode')
            os.system('echo "high" > powerstatus')
            tempresp = 'Jetson Response'.encode()
            self.write_pkt(tempresp, 't', pkt[I2CPacket.seq_index] + 1)




    def write_to_buf(self, data):
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

    def read_from_buf(self):
        '''
        Reads from the eeprom buffer. 

        Returns the data as a bytes object. 
        '''
        # Open buffer and return first 256 bytes
        with open(self.buf, 'rb') as buf:
            return buf.read(self.blocksize)

    def write_pkt(self, data: bytes, status: str, sequence: int):
        '''
        Used in file transfer or in response to a command. Given some 
        information about the packet, packs it into a struct and writes it to 
        the buffer for sending.
        '''
        pkt = I2CPacket.create_pkt(data, len(data), status,
                                   sequence, self.pkt_self_id)

        # Return status of write
        return self.write_to_buf(pkt)
  
    def read_pkt(self):
        '''
        If the packet is valid, the contents of if are returned in the form of
        a tuple. Otherwise False is returned.
        '''
        # Get the packet from the Pi
        data = self.read_from_buf()
        
        # Check its integrity (checksum)
        if not I2CPacket.verify_pkt(data):
            return False

        # Parse packet if it is valid and return
        return I2CPacket.parse_pkt(data)
    
    def wait_response(self):
        '''
        Blocks for one second or until the target responds

        Returns resulting packet, if valid packet is received
        Returns false otherwise
        '''
        # Timeout in 1 second
        timeout = time.time() + 3

        # Continuously check the Pi for its response
        while timeout > time.time():
            # Get the packet from the Pi
            data = self.read_from_buf()

            # Parse packet
            pkt = I2CPacket.parse_pkt(data)

            # Grab sender ID to know if transmission was complete
            sender = pkt[I2CPacket.id_index].decode(errors='ignore')

            # If the sender ID is not ourselves, we received a transmission

            if sender != self.pkt_self_id:             

                # Check its integrity (checksum)
                if I2CPacket.verify_pkt(data):
                    return pkt
                else:
                    # If invalid, send an error message so pi resends it
                    print('Requesting new packet (invalid)')
                    self.write_pkt(b'', 'e', 0)

        self.write_log('Timeout occured. Returning false.')
        # If timeout occurs, return false
        return False

    def send_and_wait(self, data: bytes, status: str, sequence: int):
        '''
        Send a packet, make continuous reads, resend packets if receiver
        sends an error message.

        Return false if an error occured (timeout or error writing)
        Return packet if non-error packet received
        '''
        # Create packet
        pkt = I2CPacket.create_pkt(data, len(data), status, sequence,
                                   self.pkt_self_id)

        # Sent packet and wait for a response
        while True:
            # Write packet, return false if it fails
            if not self.write_to_buf(pkt):
                return False

            # Grab result of the wait
            result = self.wait_response()

            # If wait returns false, return false
            if not result:
                return False

            # Otherwise if packet was received
            else:
                # Resend packet if an error packet was received
                if result[I2CPacket.stat_index] == b'e':
                    pass

                # Return packet if non-error
                else:
                    return result

    def file_receive(self, filename: str):
        '''
        Receive a file from the pi, write it to the jetson
        '''
        sequence = 0

        # Open new file for writing
        with open(filename, 'wb') as newfile:

            self.write_log('Created file.')
            self.write_log('Sending ready condition.')

            print('Sending ready: ', sequence)

            pkt = self.send_and_wait(b'ready', 'r', sequence)
        
            # If waiting for response errors, return false
            if not pkt:
                return False
            
            # While the Pi hasn't ended transmission
            while pkt[I2CPacket.stat_index] != b't':
                self.write_log('Received data')

                print('Received data: ', sequence)

                # Select data
                data = pkt[I2CPacket.data_index]
                data_len = pkt[I2CPacket.dlen_index]

                self.write_log('Data: \n' + data.decode(errors='ignore'))
                self.write_log('Writing packet ' + str(sequence))

                # Write data to file
                newfile.write(data[:data_len])

                # Increment packet counter
                sequence += 1

                print('Sending ready: ', sequence)
                pkt = self.send_and_wait(b'ready', 'r', sequence)

        print('Ending transmission')
        # Send termination packet so Pi packet is not left in buffer
        self.write_pkt(b'end', 't', sequence)
        return True


    def file_send(self, filename: str):
        '''
        Send a file from the jetson to the pi
        '''
        sequence = 0

        # Try to open requested file for reading
        try:
            reqfile = open(filename, 'rb')

        # Ignore File Not Found exceptions and move on to ending transmission
        except FileNotFoundError:
            self.write_log('File does not exist')

        # If open was successful, start transferring data
        else:
            with reqfile:
                # Read first chunk of data
                data = reqfile.read(I2CPacket.data_len)

                # While we are still grabbing data from the file
                while data:
                    # Write data to buffer to be sent
                    if not self.send_and_wait(data, 'd', sequence):
                        print('Error writing packet')
                        self.write_log('Error writing data')
                        return False
                
                    sequence += 1

                    # Read next chunk of data
                    data = reqfile.read(I2CPacket.data_len)

        # End transmission
        # Notify Pi transmission is over
        self.write_pkt(b'end', 't', sequence)

        self.write_log('Ending transmission')

        print('Ending transmission')

def main():
    # Make monitor program
    watcher = Monitor()        

    while True:
        watcher.check_buf()

    '''
    pkt = False
    
    while not pkt:
        pkt = watcher.wait_response()
    
    while True:
        if pkt:
            watcher.write_log('Message: \n' + pkt[0].decode(errors='ignore'))
            watcher.write_log('Message len: ' + str(pkt[1]))
            watcher.write_log('Status: ' + pkt[2].decode())
            watcher.write_log('Checksum: ' + str(pkt[3]))
            watcher.write_log('Sequence: ' + str(pkt[4]))
            watcher.write_log('Sender ID: ' + pkt[5].decode())

            pkt = watcher.send_and_wait(b'This is a response from the jetson', 'r', 45)
        else:
            pkt = watcher.wait_response()

    '''     
if __name__ == '__main__':
    main()
