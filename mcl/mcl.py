import queue
import socket
import struct
import sys
import threading
import binascii
import time
import json

from .mcl_config import MCL_Config_GeneralLocal_Ctrl, MCL_Config_GeneralPic_Ctrl
from .mcl_lidata import MCL_LiData_DataReadings
from .mcl_scope import MCL_Scope, MCL_FFT

class MCL:
    """
    MCL class to control the MCL1-540 lockin amplifer measurement system.
    SynkTek AB, SWEDEN
    Holger Motzkau
    info@synktek.com
    version 0.1
    2021-05-19


    Properties
    ----------
    lidata_data_readings_l1 : namedtuple
    lidata_data_readings_l2 : namedtuple
        the lockin data of lockin sets 1/2
    ...

    Methods
    -------
    findSystems()
        Detect MCL systems on the local network
    connect(mcl_ip)
        Connect to the MCL system
    disconnect(mcl_ip)
        Disconnect from the MCL system

    """
    
    def __init__(self):
        self._stop = False # true to stop communication in different threads
        # ping counters for read and write connections
        self._ping_i_r = 0
        self._ping_i_w = 0
        # write command queue
        self._queue_w = queue.Queue()

        self._config_general_pic_ctrl = MCL_Config_GeneralPic_Ctrl()
        self._config_general_local_ctrl = MCL_Config_GeneralLocal_Ctrl()
        self._lidata_data_readings_l1 = MCL_LiData_DataReadings(0)
        self._lidata_data_readings_l2 = MCL_LiData_DataReadings(1)        
        self._scope = MCL_Scope()
        self._fft = MCL_FFT()
        
        self._dests = {}
        all_subclasses = [
            self._config_general_pic_ctrl,
            self._config_general_local_ctrl,
            self._lidata_data_readings_l1,
            self._lidata_data_readings_l2,
            self._scope,
            self._fft
        ]
        for x in all_subclasses:
            self._add_class(x)
       # print(self._dests)
            
    def _add_class(self, x):
       # print('adding dest %i : %i' % (x.datatype, x.datakind))
        self._dests[(x.datatype, x.datakind)] = x

    def _get_class(self, datatype, datakind):
        try:
            return self._dests[datatype, datakind]
        except:
            return False

    @property
    def config_general_pic_ctrl(self):
        "Installed modules and control functions."
        return self._config_general_pic_ctrl

    @property
    def config_general_local_ctrl(self):
        "Internal voltages and PIC hardware version."
        return self._config_general_local_ctrl

    @property
    def lidata_data_readings_l1(self):
        "Data readings of lockin set 1."
        return self._lidata_data_readings_l1

    @property
    def lidata_data_readings_l2(self):
        "Data readings of lockin set 2."
        return self._lidata_data_readings_l2

    @property
    def scope(self):
        "Scope readings."
        return self._scope

    @property
    def fft(self):
        "FFT of scope readings. Readonly."
        return self._fft

        
    def find_systems(self):
        """Detect systems on the local network.

        Parameters
        ----------
        none

        Returns
        -------
        system
            a dictionary of json strings, ip addess as key
        """
        ports = [1901, 1902]
        for port in ports:
            cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            cs.bind(('', port))
            cs.sendto(b'MCL?', ('239.255.255.250', port))
            cs.close()
        threads = []
        replies = queue.Queue()
        for port in ports:
            port += 2 # read reply from higher port #
            threads.append(threading.Thread(target=self._find_systems_reply, args=[port,replies]))
        # Wait for all threads to complete
        for t in threads:
            t.start()
            t.join()
        # Read the queue
        systems = {}
        while not replies.empty():
            ip, system = replies.get()
            systems[ip] = system
        return systems
    
    def _find_systems_reply(self,port,replies):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        mreq = struct.pack("=4sl", socket.inet_aton("239.255.255.250"), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(1)
        systems = {}
        while True:
            try:
                data, (ip, port) = sock.recvfrom(1024) # buffer size is 1024 bytes
            except: # no reply within one second
#                print('UDP read error')
#                print(sys.exc_info()[0])
                break
            if data[0:10] == b'MCL-REPLY:':
                replies.put((ip,json.loads(data[10:])))


    def connect(self, mcl_ip):
        """Connect to the MCL system

        Parameters
        ----------
        mcl_ip : str
            The IP address of the system

        Returns
        -------
        none
        """
         
        # Create a TCP/IP socket
        self._sock_r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock_w = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # event to notify when all variables from the lockin are initilized
        init_event = threading.Event()

        # connect socket to the port
        self._server_address_r = (mcl_ip, 46000)
        self._server_address_w = (mcl_ip, 46001)
        print('connecting to %s port %s' % self._server_address_r, file=sys.stderr)
        try:
            self._sock_r.connect(self._server_address_r)
        except:
            print("Error: cannot open socket.")
            time.sleep(1)
            quit()
        print('connecting to %s port %s' % self._server_address_w, file=sys.stderr)
        self._sock_w.connect(self._server_address_w)
        # start communication threads
        # reading: send ping
        threading.Thread(target=self._ping_r_timer, daemon=True).start()
        # reading: read data
        threading.Thread(target=self._data_r, daemon=True, args=[init_event]).start()
        # sending: read ping
        threading.Thread(target=self._ping_w_r, daemon=True).start()
        # sendimg: send data
        threading.Thread(target=self._data_w, daemon=True).start()
        # trigger update of user variables
        time.sleep(1)
        self._config_general_local_ctrl.val = self._config_general_local_ctrl.val._replace(updateuser = True)
        self._queue_w.put(self._config_general_local_ctrl.send())
        # wait until all data is received/initialized
        print("Waiting to syncronize config variables...")
        init_event.wait()
        print("Conected, config variables synced")
        init_event.clear()
    def _ping_r_timer(self):
        """Send a ping to the system once a second to keep the connection alive."""
        while not self._stop:
            # running timer
            time.sleep(1)
            self._ping_r()

    def _ping_r(self):
        """Send the ping/increasing integer to the system. Sending a zero resets the connection."""
        # sending pring %i" % self.ping_i_r
        self._sock_r.sendall(self._ping_i_r.to_bytes(4, byteorder='big', signed=False))
        self._ping_i_r += 1


    def _ping_w_r(self):
        chunks = bytearray()
        bytes_recd = 0
        while not self._stop:
            # waiting for ping
            chunk = self._sock_w.recv(4)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks += bytearray(chunk)
            while len(chunks) >= 4:
                # received ping %i' % i
                i = int.from_bytes(chunks[0:4], byteorder='big', signed=False)
                del chunks[0:4]

    def _data_w(self):
        chunks = bytearray()
        while not self._stop:
            tosend = self._queue_w.get()
            if tosend != b'': # skip zero bytes, used for for disconnecting
                self._sock_w.sendall(tosend)
            self._queue_w.task_done()

    def _data_r(self, init_event):
        chunks = bytearray()
        wait_for_header = True
        min_len = 7
        datalen = 0
        datakind = 0
        datatype = 0 # Controls = 0, Indicators = 1, Config = 2, Lock-in Data = 3, Waveforms = 4

        # check if datatypes are initiated, then notify init_event
        num_datatypes = [0, 0, 137, 2, 2]
        initiated_datatypes = [ [], [], [False] * num_datatypes[2], [False] * num_datatypes[3], [False] * num_datatypes[4] ]
        is_initiated = False


        while  not self._stop:
            # wating for data
            chunk = self._sock_r.recv(10000)
            # received data length = %i" %len(chunk)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks += bytearray(chunk)
            # wait until full dataset is received
            while len(chunks) >= min_len:
                if(wait_for_header):
                    datatype = int.from_bytes(chunks[0:1], byteorder='big', signed=False)
                    datakind = int.from_bytes(chunks[1:3], byteorder='big', signed=False)
                    datalen  = int.from_bytes(chunks[3:7], byteorder='big', signed=False)
                    del chunks[0:7]
                    min_len = datalen
                    wait_for_header = False
                if not wait_for_header and len(chunks) >= min_len:
                    if not is_initiated:
                        initiated_datatypes[datatype][datakind] = True
#                        if initiated_datatypes[2].count(True) + initiated_datatypes[3].count(True) + initiated_datatypes[4].count(True) >= sum(num_datatypes):
                        if initiated_datatypes[2].count(True) >= num_datatypes[2]:
                            is_initiated = True
                            init_event.set()

                    data = chunks[0:datalen]

                    dst = self._get_class(datatype, datakind)
                    if dst:
                        dst.receive(data)
                    
                    wait_for_header = True
                    min_len = 7
                    del chunks[0:datalen]


    def disconnect(self):
        """Disconnect from the MCL system

        Parameters
        ----------
        none

        Returns
        -------
        none
        """

        self._stop = True
        self._queue_w.put(bytearray())
        time.sleep(2)
        self._sock_r.close()
        self._sock_w.close()
        self._ping_i_r = 0
        self._ping_i_w = 0



