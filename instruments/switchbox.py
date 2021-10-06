import serial

__all__ = ['SwitchBox', 'BalanceBox']


class SwitchBox:
    """
    Control class for the in house made switch boxes via virtual COM ports. Uses dictionaries to make it easy to change assignments and see
    what you are switching to.
    A, B, C, D, E, F, G, H are the possible 8 outputs and "V1+" "V1-" "V2+" "V2-" "I+" "I-" are the possible inputs with
    '' and 0 being "no connection" if you wish to specify them.

    """

    def __init__(self):
        """
        Defines useful hex values for ease of coding and use.
        """
        self.start_byte = 'FE'
        self.clear_byte = '10'
        self.refresh_byte = '12'
        self.blank_byte = '00'
        self.stop_byte = 'C0'
        self.binary_dictionary = {"A": '00', "B": '01', "C": '02', "D": '03', "E": '04', "F": '05', "G": '06',
                                  "H": '07',
                                  "V1+": 32, "V1-": 16, "V2+": 8, "V2-": 4, "I+": 2, "I-": 1, "0": 0,
                                  "": 0}

    def connect(self, port):
        """
        Connects to the switchbox using RS232 on given port with baud rate 57600

        :param int port: COM port number e.g. for COM7 use 7

        :returns: None
        """
        self.sb = serial.Serial(f'COM{port}', 57600, 8)
        self.sb.close()
        self.sb.open()
        self.reset_all()

    def switch(self, assignments):
        """
        Specifies the assignments for the box to change to.

        :param  assignments: Assignment should be a dictionary of all desired pin connections with keys as one input and values as outputs. eg: {"V1+": "AE", "V1-": "B", "I+", "B"} would connect V1+ to A and E and B to V1- and I+
        :type assignments: dict{str: str}

        :returns: None
        """
        self.reset_all()
        # This funky stuff allows multiple inputs to be connected to a single sample pin such as when measuring rxx
        # and rxy by sharing a pin
        for key, out_pins in assignments.items():
            keys = [k for (k, v) in assignments.items() if v == out_pins]
            in_pins = sum(self.binary_dictionary[pin] for pin in keys)
            in_pin_hex = hex(in_pins)[2::].zfill(2)
            out_pin_binary = 0
            for pin in out_pins:
                self.sb.write(bytes.fromhex(self.start_byte + self.binary_dictionary[pin] +
                                            in_pin_hex + self.stop_byte))

        self.refresh()

    def refresh(self):
        """
        FLushes the changes and actually switches the box.

        :returns: None
        """
        self.sb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def reset_all(self):
        """
        Resets all connections to be open.

        :returns: None
        """
        self.sb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()

    def close(self):
        """
        Opens all switches and closes the com port connection.
        :returns:
        """
        self.reset_all()
        self.refresh()
        self.sb.close()


class BalanceBox:
    """
    Controls the resistance balancing box using virtual serial COM ports
    """

    def __init__(self):
        """
        Defines the required dictionaries and default assignments
        """
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

    def connect(self, port):
        """
        Connects on given COM port.

        :param int port: desired COM port number eg for COM8 use 8

        :returns: None
        """
        self.bb = serial.Serial(f'COM{port}', 57600, 8)
        self.bb.close()
        self.bb.open()
        self.reset_resistances()

    def set_resistances(self, assignments):
        """
        Set the resistance of channels A-H to an int number between 0 and 255. Assignments such as {"A":25, "B":15}.
        Does not enable pins. Use enable_some or enable_all for this.

        :param assignments: dictionary of assignments for each pin and it's resistance
        :type assignments: dict{str: int}

        :returns: None
        """
        self.reset_resistances()
        for channel, resistance in assignments.items():
            res_hex = hex(resistance)[2::].zfill(2)
            chan = self.binary_dictionary[channel[0]]
            self.bb.write(bytes.fromhex(self.start_byte + chan + res_hex + self.stop_byte))
        self.refresh()

    def enable_all(self):
        """
        Enables the connections for all channels

        :returns: None
        """
        self.bb.write(bytes.fromhex(self.start_byte + self.enable_byte + self.enable_all_byte + self.stop_byte))
        self.refresh()

    def enable_some(self, pin_string):
        """
        Takes string like '10001110' which would enable channels A, E, F, G. use when switching to reduce stray currents

        :param str pin_string: binary representation of the one/off states of each channel in the following order: ABCDEFGH

        :returns: None
        """

        pin_byte = hex(int(pin_string[::-1], 2))[2:].zfill(2)  # Reverses pin byte because of ordering.
        self.bb.write(bytes.fromhex(self.start_byte + self.enable_byte + pin_byte + self.stop_byte))
        self.refresh()

    def disable_all(self):
        """
        Disables all connections.

        :returns: None
        """
        self.bb.write(bytes.fromhex(self.start_byte + self.enable_byte + self.blank_byte + self.stop_byte))
        self.refresh()

    def refresh(self):
        """
        Refreshes the shift registers essentially updating the changes.

        :returns: None
        """
        self.bb.write(bytes.fromhex(self.start_byte + self.refresh_byte + self.blank_byte + self.stop_byte))

    def reset_resistances(self):
        """
        sets all resistances to 0. Does not enable/disable pins

        :returns: None
        """
        self.bb.write(bytes.fromhex(self.start_byte + self.clear_byte + self.blank_byte + self.stop_byte))
        self.refresh()

    def close(self):
        """
        Resets all values and disables all pins then closes the serial connection.

        :returns: None
        """
        self.reset_resistances()
        self.disable_all()
        self.refresh()
        self.bb.close()
