import serial

__all__ = ['SwitchBox']


class SwitchBox:
    def __init__(self):
        self.start_byte = 'FE'
        self.clear_byte = '10'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'
        self.binary_dictionary = {"A": '00', "B": '01', "C": '02', "D": '03', "E": '04', "F": '05', "G": '06', "H": '07',
                                  "V1+": '20', "V1-": '10', "V2+": '08', "V2-": '04', "I+": '02', "I-": '01', "0": '00',
                                  "": '00'}

    def connect(self, port):
        self.sb = serial.Serial(f'COM{port}', 57600, 8)
        self.sb.close()
        self.sb.open()
        self.clear()

    def switch(self, assignments):

        #     this will be called with a desired arrangement and will call make_command if it seems necessary
        self.clear()
        for x, y in assignments.items():
            for char in y:
                self.sb.write(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                               self.stop_byte))
                # print(bytes.fromhex(self.start_byte + self.binary_dictionary[char] + self.binary_dictionary[x] +
                #                self.stop_byte))
        self.refresh()

    def close(self):
        self.clear()
        self.refresh()
        self.sb.close()

    def refresh(self):
        # sends command to turn off all channels
        self.sb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def clear(self):
        self.sb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()
#
# class ResistanceBox()
