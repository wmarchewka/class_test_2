import logging
import pigpio
from support.config import Config


class Decoder(object):
    chip_select_list = list(range(11))
    chip_select_primary_freq = 0
    chip_select_primary_coarse_gain = 1
    chip_select_secondary_freq = 2
    chip_select_secondary_coarse_gain = 3
    chip_select_secondary_fine_gain = 4
    chip_select_primary_fine_gain = 5
    chip_select_speed_tach_1 = 6
    chip_select_speed_tach_2 = 7
    chip_select_current_sense = 8
    chip_select_switches = 9
    chip_select_names = ["Primary Frequency", "Primary Gain Coarse", "Secondary Frequency",
                         "Secondary Gain Coarse",
                         "Seondary Gain Fine", "Primary Gain Fine",
                         "Speed Tach 1", "Speed Tach 2", "Current Sense", "Switches"]

    def __init__(self, config, gpio):
        self.config = config
        self.logger = self.config.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.log.debug('Decoder initializing....')
        self.GPIO = gpio.GPIO
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    def startup_processes(self):
        self.read_config_file()
        self.configure_output_pins()

    def read_config_file(self):
        self.pin_select = self.config.decoder_pin_select
        self.PIN_A = self.config.decoder_pin_A  # BCM5
        self.PIN_B = self.config.decoder_pin_B  # BCM6
        self.PIN_C = self.config.decoder_pin_C  # BCM13
        self.address_pins = [self.PIN_A, self.PIN_B, self.PIN_C]

    def configure_output_pins(self):
        try:
            # decoder pins for 3 of 8
            self.GPIO.set_mode(self.PIN_A, pigpio.OUTPUT)
            self.GPIO.set_mode(self.PIN_B, pigpio.OUTPUT)
            self.GPIO.set_mode(self.PIN_C, pigpio.OUTPUT)
        except Exception as err:
            self.log.exception('Error in gpio setup {}'.format(err.args))
        self.log.debug("Decoder setting pins " + str(self.PIN_A) + " " + str(self.PIN_B) + " " + str(
            self.PIN_C) + " as outputs...")

    def chip_select(self, cs_pin):
        pin_selection = 0
        if cs_pin == Decoder.chip_select_primary_freq:
            self.log.debug('Decoder selecting  CS 0')
            # write 000
            pin_selection = self.pin_select[0]
        elif cs_pin == Decoder.chip_select_primary_coarse_gain:
            # write 100
            self.log.debug('Decoder selecting  CS 1')
            pin_selection = self.pin_select[1]
        elif cs_pin == Decoder.chip_select_secondary_freq:
            # write 010
            self.log.debug('Decoder selecting  CS 2')
            pin_selection = self.pin_select[2]
        elif cs_pin == Decoder.chip_select_secondary_coarse_gain:
            # write 110
            self.log.debug('Decoder self.selecting CS 3')
            pin_selection = self.pin_select[3]
        elif cs_pin == Decoder.chip_select_secondary_fine_gain:
            # write 001
            self.log.debug('Decoder selecting CS 4')
            pin_selection = self.pin_select[4]
        elif cs_pin == Decoder.chip_select_primary_fine_gain:
            # write 101
            self.log.debug('Decoder selecting CS 5')
            pin_selection = self.pin_select[5]
        elif cs_pin == Decoder.chip_select_speed_tach_1:
            # write 011
            self.log.debug('Decoder selecting CS 6')
            pin_selection = self.pin_select[6]
        elif cs_pin == Decoder.chip_select_speed_tach_2:
            # write 111
            self.log.debug('Decoder selecting CS 7')
            pin_selection = self.pin_select[7]
        elif cs_pin == Decoder.chip_select_current_sense:
            # write 000
            self.log.debug('Decoder selecting CS 8')
            pin_selection = self.pin_select[8]
        elif cs_pin == Decoder.chip_select_switches:
            # write 100
            self.log.debug('Decoder selecting CS 9')
            pin_selection = self.pin_select[9]
        self.log.debug('DECODER setting pins {}  to state of {}'.format(self.address_pins, pin_selection))
        try:
            self.GPIO.write(self.address_pins[0], pin_selection[0])
            self.GPIO.write(self.address_pins[1], pin_selection[1])
            self.GPIO.write(self.address_pins[2], pin_selection[2])
        except AttributeError:
            self.log.exception("Error setting decoder chip select pins", exc_info=True)
