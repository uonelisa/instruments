from collections import namedtuple
import struct
import threading


class MCL_LiData_DataReadings:
    datatype = 3
    datakind = 0
    nt = namedtuple('MCL_LIData_datareadings', 'generalreadings, moduledata, dc, x, y, r, thetadeg')
    generalreadings_nt = namedtuple('MCL_LIData_generalreadings',
                                    'dt_s cyclespersample syncindex time_s lockinf_hz pll1_hz pll2_hz composite1_hz')
    moduledata_nt = namedtuple('MCL_LIData_moduledata', 'digitalInf_hz digitaloutf_hz amplitude_vrms outputoffset_v')

    def __init__(self, lockinset):
        self.datakind += lockinset
        self._lockinset = lockinset
        generalreadings = self.generalreadings_nt(
            dt_s=float("NaN"),
            cyclespersample=float("NaN"),
            syncindex=float("NaN"),
            time_s=float("NaN"),
            lockinf_hz=float("NaN"),
            pll1_hz=float("NaN"),
            pll2_hz=float("NaN"),
            composite1_hz=float("NaN")
        )
        moduledata = []
        dc = []
        x = []
        y = []
        r = []
        thetadeg = []
        self._datareadings = self.nt(generalreadings=generalreadings, moduledata=moduledata, dc=dc, x=x, y=y, r=r,
                                     thetadeg=thetadeg)
        self._callbacks = []

    def receive(self, chunks):
        generalreadings = self.generalreadings_nt._make(struct.unpack('>8d', chunks[660:700] + chunks[864:888]))
        moduledata = []
        moduledata_cnt = struct.unpack('>I', chunks[700:704])[0]
        moduledata_start_i = 704  # to 864
        for i in range(moduledata_cnt):
            moduledata.append(self.moduledata_nt._make(
                struct.unpack('>4d', chunks[moduledata_start_i + 32 * i:moduledata_start_i + 32 * i + 32])))
        x_cnt = struct.unpack('>I', chunks[0:4])[0]
        fmt = ">%dd" % 16
        dc = list(struct.unpack(fmt, chunks[4:132]))
        x = list(struct.unpack(fmt, chunks[136:264]))
        y = list(struct.unpack(fmt, chunks[268:396]))
        r = list(struct.unpack(fmt, chunks[400:528]))
        thetadeg = list(struct.unpack(fmt, chunks[532:660]))

        self._datareadings = self.nt(generalreadings=generalreadings, moduledata=moduledata, dc=dc, x=x, y=y, r=r,
                                     thetadeg=thetadeg)
        self._notify_observers(self._datareadings)

    @property
    def datareadings(self):
        return self._datareadings

    @datareadings.setter
    def datareadings(self, datareadings):
        pass  # readonly, do nothing.

    def _notify_observers(self, datareadings):
        for callback in self._callbacks:
            threading.Thread(target=callback, args=(self._lockinset, datareadings)).start()

    def register_callback(self, callback):
        self._callbacks.append(callback)
