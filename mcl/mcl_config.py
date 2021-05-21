from collections import namedtuple
import struct

class MCL_Config_GeneralLocal_Ctrl:
    datatype = 2
    datakind = 44
    nt = namedtuple(
        'MCL_config_GeneralLocalCtrl',
        'updateuser sendcalibrations installedmodule_a installedmodule_b installedmodule_c installedmodule_d installedmodule_e configuration applytodefault loadprefs saveprefs'
    )
    fmt = '>7?B3?'
    def __init__(self):
        self._val = self.nt(
            updateuser = False,
            sendcalibrations = False,
            installedmodule_a = False,
            installedmodule_b = False,
            installedmodule_c = False,
            installedmodule_d = False,
            installedmodule_e = False,
            configuration = 0,
            applytodefault = True,
            loadprefs = False,
            saveprefs = False
        )
    def receive(self, chunk):
        self._val = self.nt._make(struct.unpack(self.fmt, chunk))

    def send(self):
        data = struct.pack(self.fmt, *tuple(self._val))
        datalen = len(data)
        return bytearray(struct.pack('>BHI', self.datatype, self.datakind, datalen)) + bytearray(data)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, val):
        self._val = val


class MCL_Config_GeneralPic_Ctrl:
    datatype = 2
    datakind = 45
    nt = namedtuple('MCL_config_GeneralPIC_ctrl', 'vcc_24v vcc_3p3v_ln vcc_5v_ln vcc_9v vcc_3p3v vcc_5v i_n v_n v_p i_p hw_rev')
    fmt = '>10dB'
    def __init__(self):
        self._val = self.nt(
            vcc_24v = float("NaN"),
            vcc_3p3v_ln = float("NaN"),
            vcc_5v_ln = float("NaN"),
            vcc_9v = float("NaN"),
            vcc_3p3v = float("NaN"),
            vcc_5v = float("NaN"),
            i_n = float("NaN"),
            v_n = float("NaN"),
            v_p = float("NaN"),
            i_p = float("NaN"),
            hw_rev = float("NaN")
        )
    def receive(self, chunk):
        self._val = self.nt._make(struct.unpack(self.fmt, chunk))

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, val):
        pass # readonly, do nothing.
