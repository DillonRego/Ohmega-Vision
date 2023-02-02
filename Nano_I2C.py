
import smbus2

class Nano_I2C:
    def __init__(self, bus_number, device_address):
        self.bus = smbus2.SMBus(bus_number)
        self.device_address = device_address

    def write_byte(self, value):
        self.bus.write_byte(self.device_address, value)

    def read_byte(self):
        return self.bus.read_byte(self.device_address)

    def check_task(self, task):
        '''
        System tasks:
        Start, Stop, get Picture, Get object information, Sending Information, Power off, Power on
        '''
        system_tasks = ["Sta", "Sto", "Pic", "Get", "Sen", "Pof", "Pon"]
        if task in system_tasks:
            return True
        return False
   
    def create_packet(self, task, success, data):
        '''
        Packet structure:           - 32 bytes total
        task needed                 - 3 bytes
        Object found                - 1 byte
        Data                        - 28 bytes
        '''
        packet = bytearray(3)
        packet[:len(task)] = task.encode()
        packet.append(success)
        packet.extend(data[:28])

        return packet

    def parse_packet(self, packet):
        task = packet[:3].decode().strip()
        success = packet[3]
        data = packet[4:]

        return task, success, data
   
    def read_packet(self, register):
        packet = self.bus.read_i2c_block_data(self.device_address, register, 28)
        return self.parse_packet(packet)

    def write_packet(self, register, packet):
        self.bus.write_i2c_block_data(self.device_address, register, packet)
   
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
    data = bytearray(28)
    packet = i2c.create_packet(task, success, data)
    register = 0x00
    i2c.write_packet(register, packet)
   
    # Test reading a packet
    task, success, data = i2c.read_packet(register)
    print("Read task: {}, success: {}, data: {}".format(task, success, data))
