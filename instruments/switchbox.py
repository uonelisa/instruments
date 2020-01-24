import serial

__all__ = ['SwitchBox', 'BalanceBox']


class SwitchBox:
    def __init__(self):
        self.start_byte = 'FE'
        self.clear_byte = '10'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'
        self.binary_dictionary = {"A": '00', "B": '01', "C": '02', "D": '03', "E": '04', "F": '05', "G": '06',
                                  "H": '07',
                                  "V1+": '20', "V1-": '10', "V2+": '08', "V2-": '04', "I+": '02', "I-": '01', "0": '00',
                                  "": '00'}

    def connect(self, port):
        self.sb = serial.Serial(f'COM{port}', 57600, 8)
        self.sb.close()
        self.sb.open()
        self.reset_all()

    def switch(self, assignments):

        #     this will be called with a desired arrangement and will call make_command if it seems necessary
        self.reset_all()
        for x, y in assignments.items():
            for char in y:
                self.sb.write(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                                            self.stop_byte))
                # print(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                #                self.stop_byte))
        self.refresh()

    def close(self):
        self.reset_all()
        self.refresh()
        self.sb.close()

    def refresh(self):
        # sends command to turn off all channels
        self.sb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def reset_all(self):
        self.sb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()


#
class BalanceBox:

    def __init__(self):
        self.enable = ["1", "1", "1", "1", "1", "1", "1", "1"]
        # self.zero_res_assignment = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0, "H": 0}
        self.binary_dictionary = {"A": '01', "B": '02', "C": '03', "D": '04', "E": '05', "F": '06', "G": '07',
                                  "H": '08'}
        self.start_byte = 'FE'
        self.clear_byte = '10'
        self.enable_byte = '14'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'

    def connect(self, port):
        self.bb = serial.Serial(f'COM{port}', 57600, 8)
        self.bb.close()
        self.bb.open()
        self.reset_resistances()

    def set_resistances(self, assignments):
        self.reset_resistances()
        for channel, resistance in assignments.items():
            res_hex = hex(resistance)[2:4]
            chan = self.binary_dictionary[channel[0]]
            self.bb.write(bytes.fromhex(self.start_byte + chan + res_hex + self.stop_byte))

    def refresh(self):
        self.bb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def reset_resistances(self):
        self.bb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()
