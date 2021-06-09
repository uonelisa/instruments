import pyvisa
import struct

__all__ = ['TEC1089SV']


class TEC1089SV:
    """
    All commands take the form #<address><sequence number><payload data><CRC16 checksum>
    the self.address class member contains both # and the 02 for address as shorthand
    and the payload data takes one of the following forms
    <operation><param id><instance><new value> for writing a value
    <operation><param id><instance> for reading a value
    <operation><instance> for a parameter less operation (e.g ?IF or ES)
    Everything is in ascii representation of hex (0-9,A-F) with no lowercase or extraneous characters.
    All error codes from the device contain a "+" followed by error code 00-09
    """

    def __init__(self):
        """
        Defines useful constants including xmodem table
        """
        self.__CRC16_XMODEM_TABLE = [
            0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
            0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
            0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
            0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
            0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
            0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
            0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
            0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
            0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
            0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
            0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
            0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
            0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
            0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
            0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
            0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
            0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
            0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
            0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
            0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
            0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
            0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
            0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
            0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
            0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
            0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
            0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
            0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
            0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
            0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
            0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
            0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
        ]
        self.__msg_counter = 0
        self.__address = '#02'

    def connect(self, port):
        """
        Connects to the temperature controller via virtual serial COM port

        :param int port: Desired COM port number e.g. 8 for COM 8

        :returns: None
        """
        rm = pyvisa.ResourceManager('@ivi')
        self.__tec = rm.open_resource(f'COM{port}', baud_rate=19200)
        self.__tec.close()
        self.__tec.open()
        self.__tec.baud_rate = 57600
        self.__tec.timeout = 5000
        self.__tec.write_termination = '\r'
        self.__tec.read_termination = '\r'
        self.__set_int32_param(108, 1)  # don't save data to flash
        # self.__set_int32_param(50010, 1)  # ramp start point setting
        instr_id = self.get_identity()
        print("connected to: " + instr_id)
        return instr_id

    def stop(self):
        """
        Emergency stops the instrument. Disables output etc.

        :returns: Response bytes.
        """
        start = self.__address
        seq = self.__param_hex(self.__msg_counter)
        self.__msg_counter = (self.__msg_counter + 1) % 65535
        op = 'ES'
        msg = start + seq + op
        response = self.__tec.query(msg + self.__crc16(msg.encode()))
        if '+' not in response:
            return response[7:-4]
        else:
            print('Failed to set value/read response with message:\n')
            print(response)

    def close(self):
        """
        Closes serial port connection

        :returns: None
        """
        self.__tec.close()

    def get_object_temperature(self):
        """
        Reads the current object temperature and converts it to float.

        :returns: object temperature in celsius
        :rtype: float
        """
        return self.__hex_float32(self.__get_param(1000))

    def get_sink_temperature(self):
        """
        Reads the current heatsink temperature and converts it to float.

        :returns: heatsink temperature in celsius
        :rtype: float
        """
        return self.__hex_float32(self.__get_param(1001))

    def get_target_temperature(self):
        """
        Reads the current target temperature and converts it to float.

        :returns: target temperature in celsius
        :rtype: float
        """
        return self.__hex_float32(self.__get_param(3000))

    def get_output_current(self):
        """
        Reads the current output current and converts it to float.

        :returns: output current in Amps
        :rtype: float
        """
        return self.__hex_float32(self.__get_param(1020))

    def get_output_voltage(self):
        """
        Reads the current output voltage and converts it to float.

        :returns: output voltage in Volts
        :rtype: float
        """
        return self.__hex_float32(self.__get_param(1021))

    def get_ramp_rate(self):
        """
        Reads the current set point ramp rate converts it to float.

        :returns: ramp rate in celsius per second
        :rtype: float
        """
        return self.__hex_float32(self.__get_param(3003))

    def get_temp_stability_state(self):
        """
        Asks the controller if the temperature is within stability threshold or not.

        :returns: True for stable, False for ramping
        :rtype: bool
        """
        states = {0: 'off', 1: 'unstable', 2: 'stable'}
        return states[self.__hex_int(self.__get_param(1200))]

    def set_target_temperature(self, target):
        """
        Sets the target temperature in float by converting to bytes before sending.

        :param float target: desired temperature in celsius
        :returns: Response from instrument
        """
        return self.__set_float32_param(3000, float(target))

    def set_ramp_rate(self, rate):
        """
        Converts the desired ramp rate from float to bytes before setting it.

        :param float rate: desired ramp rate in celsius per second
        :returns: Response from instrument
        """
        return self.__set_float32_param(3003, float(rate))

    def enable_control(self):
        """
        Enables temperature control. Use set_target_temperature first.

        :returns: Response from instrument
        """
        return self.__set_int32_param(2010, 1)

    def disable_control(self):
        """
        Disables temperature control

        :returns: Response from instrument
        """
        return self.__set_int32_param(2010, 0)

    def get_identity(self):
        """
        Reads the identity information from the instrument for printing on connect.

        :returns: Response from instrument
        """
        start = self.__address
        seq = self.__param_hex(self.__msg_counter)
        self.__msg_counter = (self.__msg_counter + 1) % 65535
        op = '?IF'
        msg = start + seq + op
        response = self.__tec.query(msg + self.__crc16(msg.encode()))
        if '+' not in response:
            return response[7:-4]
        else:
            print('Failed to set value/read response with message:\n')
            print(response)
        # 00ABCD?IF

    def __get_param(self, param):
        """
        Given a parameter ID, this command queries the parameter from the instrument

        :param int param: parameter ID

        :returns: The message between the preamble and the checksum or None
        """
        start = self.__address
        seq = self.__param_hex(self.__msg_counter)
        self.__msg_counter = (self.__msg_counter + 1) % 65535
        op = '?VR'
        param = self.__param_hex(param)
        instance = '01'
        msg = start + seq + op + param + instance
        response = self.__tec.query(msg + self.__crc16(msg.encode()))
        if '+' not in response:
            return response[7:-4]
        else:
            print('Failed to set value/read response with message:\n')
            print(response)

    def __set_int32_param(self, param, value):
        """
        Does appropriate conversion before setting param ID to Value

        :param int param:
        :param float value:

        :returns: Response from Instrument
        """
        start = self.__address
        seq = self.__param_hex(self.__msg_counter)
        self.__msg_counter = (self.__msg_counter + 1) % 65535
        op = 'VS'
        param = self.__param_hex(param)
        instance = '01'
        val = self.__int32_hex(value)
        msg = start + seq + op + param + instance + val
        response = self.__tec.query(msg + self.__crc16(msg.encode()))
        if '+' not in response:
            return response[7:-4]
        else:
            print('Failed to set value/read response with message:\n')
            print(response)

    def __set_float32_param(self, param, value):
        """
        Does appropriate conversion before setting param ID to Value

        :param int param:
        :param float value:

        :returns: Response from Instrument
        """
        start = self.__address
        seq = self.__param_hex(self.__msg_counter)
        self.__msg_counter = (self.__msg_counter + 1) % 65535
        op = 'VS'
        param = self.__param_hex(param)
        instance = '01'
        val = self.__float32_hex(value)
        msg = start + seq + op + param + instance + val
        response = self.__tec.query(msg + self.__crc16(msg.encode()))
        if '+' not in response:
            return response[7:-4]
        else:
            print('Failed to set value/read response with message:\n')
            print(response)

    def __param_hex(self, param):
        """
        Converts parameter number into hex form for use in queries etc.

        :param int param: the parameter number to be converted into hex

        :returns: the hex form of the parameter number in 2byte format with no 0x prefix
        """
        return f"{param:04X}"

    def __int32_hex(self, value):
        """
        Convert int32 to hex for transmission to device

        :param int32 value: The value to be converted into a 32bit hex value

        :returns: The string form of the hex with no 0x prefix, 8 characters long.
        """
        return f"{value:08X}"

    def __hex_int(self, hex_str):
        """
        Convert hex string from instrument into int32 (might not work with UInts above a large number)

        :param str hex_str:

        :returns: integer from hex
        """
        return int(hex_str, 16)

    def __float32_hex(self, value):
        """
        Convert a python float to a hex string for sending to the device

        :param float value: value to be converted into float

        :returns: hex string without 0x prefix
        """
        return hex(struct.unpack('<I', struct.pack('<f', value))[0]).lstrip('0x').upper()

    def __hex_float32(self, hex_str):
        """
        Convert hex output from device into usable numbers

        :param str hex_str: ascii hex representation of float to be converted

        :returns: the float in double precision
        """
        return struct.unpack('!f', bytes.fromhex(hex_str))[0]

    def __crc16(self, data):
        """Calculate checksum using CRC16 (standard)

        :param string data: the entire message without CRC (inc the '#' at the start)

        :returns: Return calculated value of CRC
        """
        crc = 0
        for byte in data:
            crc = ((crc << 8) & 0xFF00) ^ self.__CRC16_XMODEM_TABLE[((crc >> 8) & 0xFF) ^ byte]
        return '%04X' % (crc & 0xFFFF)
