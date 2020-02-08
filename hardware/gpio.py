import pigpio
import logging


class Gpio(object):
    __gpio = None
    __mode_input = 0
    __mode_output = 1

    def __new__(cls, config, commander):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
            ("Creating new class GPIO {}".format(cls.instance))
            Gpio.__gpio = pigpio.pi()
        else:
            print("Creating instance class GPIO {}".format(cls.instance))
        return cls.instance

    def __init__(self, config, commander):
        self.init = True
        self.GPIO = Gpio.__gpio
        self.log = commander.log
        self.log = logging.getLogger(__name__)
        self.config = config
        self.check_connection()
        self.get_status()
        self.log.debug("{} init complete...".format(__name__))

    def shutdown(self):
        if self.GPIO.connected:
            self.GPIO.wave_tx_stop()
            self.GPIO.wave_clear()
            self.GPIO.stop()
            self.log.debug("Shutting down PIGPIO...")

    def set_chip_select(self, data):
        self.GPIO.write(data[0][0], data[0][1])
        self.GPIO.write(data[1][0], data[1][1])
        self.GPIO.write(data[2][0], data[2][1])

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

    def check_connection(self):
        if not self.GPIO.connected:
            self.log.debug("PIGPIO not connected")
        else:
            self.log.debug('PIGPIO connected...')

    def get_status(self):
        try:
            self.log.debug('Getting IO status...')
            self.log.debug("gpio STATUS: Pins(0-31) {}  Pins(32-54)  {}   ".format(bin(self.GPIO.read_bank_1()),
                                                                                   bin(self.GPIO.read_bank_2())))
        except Exception:
            self.log.exception("EXCEPTION in get_status", exc_info=True)

    @staticmethod
    def edge_to_string(edge):
        if edge == 1:
            return "RISING"
        elif edge == 0:
            return "FALLING"
        elif edge == 2:
            return "ERROR"
