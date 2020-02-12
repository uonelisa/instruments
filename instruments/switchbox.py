import serial

__all__ = ['SwitchBox', 'BalanceBox']


class SwitchBox:

    # Defines useful hex values for ease of coding and use.
    def __init__(self):
        self.start_byte = 'FE'
        self.clear_byte = '10'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'
        self.binary_dictionary = {"A": '00', "B": '01', "C": '02', "D": '03', "E": '04', "F": '05', "G": '06',
                                  "H": '07',
                                  "V1+": 32, "V1-": 16, "V2+": 8, "V2-": 4, "I+": 2, "I-": 1, "0": 0,
                                  "": 0}

    # connects to sb on given port with baud rate 57600
    def connect(self, port):
        self.sb = serial.Serial(f'COM{port}', 57600, 8)
        self.sb.close()
        self.sb.open()
        self.reset_all()

    # Switches the box. Assignment should be a dictionary of all desired pin connections. eg: {"V1+": "A", "V1-": "B"}
    # would connect a to V1+ and B to V1-.
    def switch(self, assignments):
        self.reset_all()
        # This funky stuff allows multiple inputs to be connected to a single sample pin such as when measureing rxx
        # and rxy by sharing a pin
        for key, out_pin in assignments.items():
            keys = [k for (k, v) in assignments.items() if v == out_pin]
            in_pins = sum(self.binary_dictionary[pin] for pin in keys)
            in_pin_hex = hex(in_pins)[2::].zfill(2)
            self.sb.write(bytes.fromhex(self.start_byte + self.binary_dictionary[out_pin] +
                                        in_pin_hex + self.stop_byte))
        self.refresh()

    def refresh(self):
        # sends command to turn off all channels
        self.sb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def reset_all(self):
        self.sb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()

    def close(self):
        self.reset_all()
        self.refresh()
        self.sb.close()


class BalanceBox:

    # Defines the required dictionaries and default assignments
    def __init__(self):
        self.enable_all_byte = "FF"
        # Reverse becuase of enable byte format (in powers of 2) "7:h 6:G 5:F 4:E 3:D 2:C 1:B 0:A"
        # A is channel 1, B is channel 2, C is channel 3 etc.
        self.binary_dictionary = {"A": '01', "B": '02', "C": '03', "D": '04', "E": '05', "F": '06', "G": '07',
                                  "H": '08'}
        # self.reset_assignments = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0, "H": 0}
        self.start_byte = 'FE'
        self.clear_byte = '11'
        self.enable_byte = '14'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'

    # Connects on given COM port
    def connect(self, port):
        self.bb = serial.Serial(f'COM{port}', 57600, 8)
        self.bb.close()
        self.bb.open()
        self.reset_resistances()

    # Set the resistance of channels A-H to an int number between 0 and 255. Assignments such as {"A":25, "B":15}
    def set_resistances(self, assignments):
        self.reset_resistances()
        for channel, resistance in assignments.items():
            res_hex = hex(resistance)[2::].zfill(2)
            chan = self.binary_dictionary[channel[0]]
            self.bb.write(bytes.fromhex(self.start_byte + chan + res_hex + self.stop_byte))
        self.refresh()

    # opens the connections for all channels
    def enable_all(self):
        self.bb.write(bytes.fromhex(self.start_byte + self.enable_byte + self.enable_all_byte + self.stop_byte))

    # Takes string like '10001110' which would enable channels A, E, F, G. use when switching to reduce stray currents.
    def enable_some(self, pin_string):
        # Reverses pin byte because of ordering.
        pin_byte = hex(int(pin_string[::-1], 2))[2:].zfill(2)
        self.bb.write(bytes.fromhex(self.start_byte + self.enable_byte + pin_byte + self.stop_byte))

    # closes all connections.
    def disable_all(self):
        self.bb.write(bytes.fromhex(self.start_byte + self.enable_byte + self.blank_byte + self.stop_byte))

    # Refreshes the shift registers essentially activating the
    def refresh(self):
        self.bb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    # sets all resistances to 0
    def reset_resistances(self):
        self.bb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()

    def close(self):
        self.reset_resistances()
        self.refresh()
        self.bb.close()
