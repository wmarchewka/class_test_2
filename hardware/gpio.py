import pigpio
import logging
import subprocess
import time

class Gpio(object):
    __gpio = None
    __mode_input = 0
    __mode_output = 1

    def __new__(cls, config):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
            ("Creating new class GPIO {}".format(cls.instance))
            try:
                pigpio.exceptions = True
                Gpio.__gpio = pigpio.pi()
            except Exception:
                print("Could not initialize PIGPIO")
        else:
            print("Creating instance class GPIO {}".format(cls.instance))
        return cls.instance

    def __init__(self, config):
        self.init = True
        self.config = config
        self.logger = self.config.logger
        self.log = self.logger.log
        self.GPIO = Gpio.__gpio
        self.log = logging.getLogger(__name__)
        self.check_connection()
        self.get_io_status()
        self.log.debug("{} init complete...".format(__name__))

    #****************************************************************************************************
    def shutdown(self):
        if self.GPIO.connected:
            self.GPIO.wave_tx_stop()
            self.GPIO.wave_clear()
            self.GPIO.stop()
            self.log.debug("Shutting down PIGPIO...")

    # ****************************************************************************************************
    def set_chip_select(self, data):
        self.GPIO.write(data[0][0], data[0][1])
        self.GPIO.write(data[1][0], data[1][1])
        self.GPIO.write(data[2][0], data[2][1])

    # ****************************************************************************************************
    def get_pin(self, pin):
        mode = self.GPIO.get_mode(pin)
        if mode == Gpio.__mode_input:
            txtmode = "INPUT"
            return self.GPIO.read(pin), txtmode
        elif mode == Gpio.__mode_output:
            txtmode = "OUTPUT"
            return self.GPIO.read(pin), txtmode
        else:
            txtmode = "UNKNOWN mode " + str(mode)
            return 0, txtmode

    # ****************************************************************************************************
    def set_pin(self, pin, state):
        mode = self.GPIO.get_mode(pin)
        if mode == Gpio.__mode_input:
            txtmode = "INPUT"
            return self.GPIO.read(pin), txtmode
        elif mode == Gpio.__mode_output:
            txtmode = "OUTPUT"
            self.GPIO.write(pin, state)
            return self.GPIO.read(pin), txtmode
        else:
            txtmode = "UNKNOWN mode " + str(mode)
            return 0, txtmode

    # ****************************************************************************************************
    def check_connection(self):
        if not self.GPIO.connected:
            self.log.debug("PIGPIO not connected, Checking Daemon....")
            self.pigpiod_daemon_status()

        else:
            self.log.debug('PIGPIO connected...')

    # ****************************************************************************************************
    def get_io_status(self):
        try:
            self.log.debug('Getting IO status...')
            self.log.debug("gpio STATUS: Pins(0-31) {}  Pins(32-54)  {}   ".format(bin(self.GPIO.read_bank_1()),
                                                                                   bin(self.GPIO.read_bank_2())))
        except Exception:
            self.log.exception("EXCEPTION in get_status", exc_info=True)

    #****************************************************************************************************
    # @staticmethod
    def edge_to_string(edge):
        if edge == 1:
            return "RISING"
        elif edge == 0:
            return "FALLING"
        elif edge == 2:
            return "ERROR"

    #****************************************************************************************************
    def pigpiod_daemon_status(self):
        try:
            self.log.info("Getting PIGPIO status...")
            del self.GPIO
            self.log.debug("Deleting PIGPIO instance...")
            # TODO check into why this is taking a long time to run at times
            self.my_cmd  = subprocess.call(["sudo", "systemctl", "stop", "pigpiod"])
            self.log.debug("Returned from shell command {}".format(self.my_cmd))
            time.sleep(0.1)
            if not self.my_cmd:
               self.log.info("Successful shutdown of PIGPIO DAEMON")
            else:
               self.log.info("Error in shutdown of PIGPIO DAEMON")
               raise NameError('Error in shutdown of PIGPIO DAEMON"')
            self.my_cmd  = subprocess.call(["sudo", "systemctl", "start", "pigpiod"])
            self.log.debug("Returned from shell command {}".format(self.my_cmd))
            if not self.my_cmd:
                self.log.info("Successful start of PIGPIO DAEMON")
            else:
                self.log.info("Error in startup of PIGPIO DAEMON")
                raise NameError('Error in startup of PIGPIO DAEMON')
            time.sleep(0.1)
            self.log.debug("Creating new PIGPIO instance...")
            self.GPIO = pigpio.pi()
            gpio_version = self.GPIO.get_pigpio_version()
            self.log.info("Using PIGPIO version: {}".format(gpio_version))
        except Exception:
            self.log.exception("Exception in pigiod_daemon_status", exc_info=True)
            return False
        else:
            return True