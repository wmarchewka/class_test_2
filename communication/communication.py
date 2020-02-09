import socketserver
import threading
import logging

from PyQt5.QtCore import *


# emitter class used to send signal through thread
class Emitter(QObject):
    signal = pyqtSignal(str, tuple)


# class that handles tcp requests
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

        self.received = None

    emitter = Emitter()

    # **************************************************************************
    # handler called automatically when data is received from client
    def handle(self):
        self.received = self.request.recv(1024).decode()
        # self.log = self.support.log
        # self.log.debug("init TCP Request Handler")
        # self.log.debug("Received: ".format(self.received))
        peer_info = self.request.getpeername()
        self.emitter.signal.emit(self.received, peer_info)

    def finish(self):
        pass


# class that handles the tcp server
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def start_tcp_server(self, logger):
        self.logger = logger
        self.log = self.logger.log

        HOST = '10.0.0.84'
        PORT = 1337
        self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        # self.server.setup(self)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server.allow_reuse_address = True
        self.server_thread.start()
        ThreadedTCPRequestHandler.emitter.signal.connect(self.callback_from_comms)
        self.log.debug('Server loop running in thread: {self.server_thread.name}')

# ************************************************************************************
class TCP_support:

    def __init__(self, logger):
        self.logger = logger
        self.log = logger.log
        self.log = logging.getLogger(__name__)

    # startup TCP server to accept commands and control remotely
    def comm_server_start(self):
        HOST = '10.0.0.111'
        PORT = 1337
        try:
            self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
            # self.server.setup(self)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server.allow_reuse_address = True
            self.server_thread.start()
            ThreadedTCPRequestHandler.emitter.signal.connect(self.comm_callback)
            self.log.info('TCP Server loop running in thread: {self.server_thread.name}')
        except Exception:
            self.log.info("TCP server failed to start...")

    # ************************************************************************************
    # callback from received commands from TCP
    def comm_callback(self, data, peer_info):
        #TODO:  Try and change these to simulate the button pushes ie  "self.window.PB_display_timer_toggle.click()"
        data = data.rstrip()
        command = data.split("=")
        ip, port = peer_info
        self.log.info("Received TCP COMMAND:{} with DATA:{}".format(command[0], command[1]))
        if command[0] == "TIMERS_ON":
            self.timers_changed(True)
        elif command[0] == "TIMERS_OFF":
            self.timers_changed(False)
        elif command[0] == "QUERY_ALL":
            self.comm_send_query_data("all", peer_info)
        elif command[0] == "PULSECODES":
            self.comm_send_query_data("PULSECODES", peer_info)
        elif command[0] == "PRIGAIN":
            # self.primary_gain_change(int(command[1]))
            self.gains.primary_gain_set_percent(float(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "SECGAIN":
            self.secondary_gain_change(float(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "PRIFREQ":
            self.pri_freq_value = int(command[1])
            self.coderategenerator.coderate_generate([self.coderate_value, self.pri_freq_value, self.sec_freq_value])
        elif command[0] == "SECFREQ":
            self.sec_freq_value = int(command[1])
            self.coderategenerator.coderate_generate([self.coderate_value, self.pri_freq_value, self.sec_freq_value])
        elif command[0] == "CODERATE":
            self.coderate_value = int(command[1])
            self.coderategenerator.coderate_generate([self.coderate_value, self.pri_freq_value, self.sec_freq_value])
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "CODERATEBUTTONID":
            self.coderate_pushbutton_change(int(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "FREQBUTTONID":
            self.frequency_pushbutton_change(int(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        else:
            self.comm_send_query_data("COMMAND ERROR", peer_info)

    # ************************************************************************************
    # send data to remote client
    def comm_send_query_data(self, data, peer_info):
        dataout = ""
        self.log.info("Sending Query data out")
        if data == "PULSECODES":
            dataout = ' '.join(map(str, self.company_pulsecodes)) + "\r" + '\n'
        elif data == "OK":
            dataout = "OK"
        dataout = dataout + "\r\n"
        HOST = peer_info[0]
        PORT = int(peer_info[1])
        SOCKET = socket.socket()
        SOCKET.connect((HOST, PORT))
        SOCKET.send(dataout.encode())
        SOCKET.close()
        # self.comm_server_start()