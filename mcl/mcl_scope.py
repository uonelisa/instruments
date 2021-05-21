from collections import namedtuple
import struct
from collections import namedtuple
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import threading

class MCL_Scope:
    datatype = 4
    datakind = 0
    is_fft = False
    nt = namedtuple(
        'MCL_scope',
        'dt_s averages_completed df_hz averagingdone waveformtype channelstoreturn_label channelstoreturn samplingreductionfactor scopesamples averagebetweensamples returnoutputinsteadofimeas data'
    )
    def __init__(self):
        self._val = self.nt(
            dt_s = float("NaN"),
            averages_completed  = float("NaN"),
            df_hz = float("NaN"),
            averagingdone = False,
            waveformtype = 0,
            channelstoreturn_label = [],
            channelstoreturn = [],
            samplingreductionfactor = 0,
            scopesamples = 0,
            averagebetweensamples = False,
            returnoutputinsteadofimeas = False,
            data = []
        )
        self._callbacks = []
    def receive(self, chunks):
        arraylen = struct.unpack('>Q', chunks[4:12])[0]
        arrayend = 12+arraylen*8
        datalength = len(chunks)
        fmt = ">%dd" % arraylen
        values = list(struct.unpack(fmt, chunks[12:arrayend]))

        metadata = chunks[arrayend:datalength].decode('ascii').rstrip('\0')
        xml                        = ET.fromstring(metadata)
        dt_s                       = float(xml.find("./DBL/[Name='dt (s)']/Val").text)
        averages_completed         = float(xml.find("./DBL/[Name='averages completed']/Val").text)
        df_hz                      = float(xml.find("./DBL/[Name='df (Hz)']/Val").text)
        averagingdone              = bool(int(xml.find("./Boolean/[Name='averaging done']/Val").text))
        waveformtype               = xml.findall("./EW/[Name='Waveform Type']/Choice")[int(xml.find("./EW/[Name='Waveform Type']/Val").text)].text
        samplingreductionfactor    = int(xml.find("./Cluster/U16/[Name='Sampling reduction factor']/Val").text)
        scopesamples               = int(xml.findall("./Cluster/EB/[Name='#scope samples']/Choice")[int(xml.find("./Cluster/EB/[Name='#scope samples']/Val").text)].text)
        averagebetweensamples      = bool(int(xml.find("./Cluster/Boolean/[Name='Average between samples']/Val").text))
        returnoutputinsteadofimeas = bool(int(xml.find("./Cluster/Boolean/[Name='Return output instead of Imeas']/Val").text))
        channelstoreturn           = []
        channelstoreturn_label     = []
        data                       = []
        dataindex = 0
        if(self.is_fft):
            chunksize = int(scopesamples/2)
        else:
            chunksize = scopesamples
        for i in xml.findall("./Cluster/Cluster/[Name='Channels to return']/Boolean"):
            channelstoreturn_label.append(i.find("Name").text)
            active = bool(int(i.find("Val").text))
            channelstoreturn.append(active)
            if active:
                data.append(values[dataindex*chunksize:(dataindex+1)*chunksize])
                dataindex += 1
            else:
                data.append([])

        self._val = self.nt(
            dt_s = dt_s,
            averages_completed  = averages_completed,
            df_hz = df_hz,
            averagingdone = averagingdone,
            waveformtype = waveformtype,
            channelstoreturn_label = channelstoreturn_label,
            channelstoreturn = channelstoreturn,
            samplingreductionfactor = samplingreductionfactor,
            scopesamples = scopesamples,
            averagebetweensamples = averagebetweensamples,
            returnoutputinsteadofimeas = returnoutputinsteadofimeas,
            data = data
        )
        self._notify_observers(waveformtype, self._val)

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, val):
        pass # readonly, do nothing.

    def _notify_observers(self, waveformtype, val):
        for callback in self._callbacks:
            threading.Thread(target=callback, args=(waveformtype, val)).start()
    def register_callback(self, callback):
        self._callbacks.append(callback)

class MCL_FFT(MCL_Scope):
    datakind = 1
    is_fft = True

