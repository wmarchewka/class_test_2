import threading
import logging
from PyQt5 import QtCore
from PyQt5.QtCore import *


class Pollvalues(QThread):
    sense_changedValue = QtCore.pyqtSignal(float, float, float)  # signal to send to awaiting slot
    switch_changedValue = QtCore.pyqtSignal(int)  # signal to send to awaiting slot
    poll_changedValue = QtCore.pyqtSignal(float, float, float, int)  # signal to send to awaiting slot

    def __init__(self, pollingpermission, currentsense, switches):
        super().__init__()
        self.pollingpermission = pollingpermission
        self.current_sense = currentsense
        self.switches = switches
        self.logger = self.pollingpermission.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.log.debug('Polling class initializing...')
        # TODO these need to come from ini file
        self.sense_scaling_factor_mv_amp = 0.055  # 55 milivolts per amp
        self.sense_amp_max_amps = 25
        self.sense_ad_vin = 3.299  # LM4128CQ1MF3.3/NOPB voltage reference
        self.sense_ad_max_bits = 14  # AD7940 ADC
        self.sense_ad_max_scaled_value = 2 ** self.sense_ad_max_bits
        self.log.debug("{} init complete...".format(__name__))

    # ********************************************************************************
    # runs both sense and switches polling
    def poll_read_values(self):
        raw_analog_digital_value, analog_digital_volts, scaled_value = self.sense_read_values()
        switch_value = self.switch_read_values()
        self.poll_changedValue.emit(raw_analog_digital_value, analog_digital_volts, scaled_value, switch_value)

    # ********************************************************************************
    # retrieves value from current sense A/D converter via spi (U25)
    def sense_read_values(self):
        # TODO get values from INI file
        if self.pollingpermission.polling_prohibited is False:
            self.log.debug('Running Sense Polling')
            data = self.current_sense.read_spi()
            self.log.debug("Data received {0:X}h {1:X}h".format(data[0], data[1]))
            raw_analog_digital_value = data[0] * 256 + data[1]
            self.log.debug(
                "RAW analog value {}  out of {}".format(raw_analog_digital_value, self.sense_ad_max_scaled_value))
            analog_digital_volts = self.sense_ad_vin * (raw_analog_digital_value / self.sense_ad_max_scaled_value)
            scaled_value = ((analog_digital_volts - (self.sense_ad_vin / 2)) / self.sense_scaling_factor_mv_amp)
            self.log.debug(
                "Analog_Digital converter value: {} Scaled Value({})".format(analog_digital_volts, scaled_value))
            #self.sense_changedValue.emit(raw_analog_digital_value, analog_digital_volts, scaled_value)
            val = QtCore.QThread.currentThreadId(), threading.current_thread().name
            self.log.debug("THREAD " + str(val))
            return raw_analog_digital_value, analog_digital_volts, scaled_value
        elif self.pollingpermission.polling_prohibited:
            self.log.info("Sense Polling canceled due to polling prohibited... ")

    # *********************************************************************************
    # retrieves value from switch mutiplexer via spi  (U20)
    def switch_read_values(self):
        if self.polling.polling_prohibited is False:
            self.log.debug('Running Switch Polling')
            returned_data = self.switches.spi_read_values()
            switch_value = returned_data[2]
            # self.switch_changedValue.emit(switch_value)
            return switch_value
        elif self.polling.polling_prohibited:
            self.log.info("Switch Polling canceled due to polling prohibited... ")
