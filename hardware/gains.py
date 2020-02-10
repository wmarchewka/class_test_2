import logging
from hardware.digitalpots import DigitalPots
# **********************************************************************************************
class Gains(object):

    sendvalue = [0.0,0.0,0.0,0.0]

    def __init__(self, digitalpots):
        self.digitalpots = digitalpots
        self.logger = self.digitalpots.logger
        self.log = logging.getLogger(__name__)
        self.log.debug('Gains initializing...')
        self.primary_gain_saved_value = 0
        self.secondary_gain_saved_value = 0
        self.startup_functions()
        self.log.debug("{} init complete...".format(__name__))

    def startup_functions(self):
        self.gain_set_percent(DigitalPots.PRIMARY_GAIN_POT_NUMBER, 0)
        self.gain_set_percent(DigitalPots.SECONDARY_GAIN_POT_NUMBER, 0)
        self.setval_and_store(DigitalPots.PRIMARY_GAIN_POT_NUMBER, 0)
        self.setval_and_store(DigitalPots.SECONDARY_GAIN_POT_NUMBER, 0)

    def setval_and_store(self, potnumber, ohm_value):  # upon start up, set gains to 0 and
        self.gain_set_percent(potnumber, ohm_value)  # store to nvram, so that the pots
        self.digitalpots.wiper_to_nvram()  # always start up with gain to 0

    def gain_set_ohms(self, potnumber, value):
        ohm_value = value
        self.digitalpots.value_check(potnumber, ohm_value)

    def gain_set_percent(self, potnumber, value):
        value = value / 100
        ohm_value = self.digitalpots.total_max_ohms * value
        self.digitalpots.value_check(potnumber, ohm_value)

    def gain_set_value(self, potnumber, coarse_ohms, fine_ohms):
        self.log.debug("Primary Gain received Coarse :{}  Fine :{}".format(coarse_ohms, fine_ohms))
        coarse = (coarse_ohms / DigitalPots.COARSE_MAX_OHMS) * DigitalPots.COARSE_WIPER_MAX_BITS
        fine = (fine_ohms / DigitalPots.FINE_MAX_OHMS) * DigitalPots.FINE_WIPER_MAX_BITS
        DigitalPots.coarse_wiper[potnumber] = int(coarse)
        DigitalPots.fine_wiper[potnumber] = int(fine)
        self.log.debug("Primary GAIN setting OHMS to COARSE: {} FINE: {} ".format(int(coarse), int(fine)))
        self.digitalpots.value_change(DigitalPots.SPEED_FAST, 0, potnumber)
        self.digitalpots.value_change(DigitalPots.SPEED_SLOW, 0, potnumber)

    def primary_gain_off(self,):
        self.log.debug("Saving PRIMARY GAIN value: {}".format(self.digitalpots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]))
        self.primary_gain_saved_value = DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
        self.log.debug("PRIMARY GAIN setting to OFF")
        self.digitalpots.value_change(DigitalPots.SPEED_SLOW,
                                      DigitalPots.ANTI_CLOCKWISE, DigitalPots.PRIMARY_GAIN_POT_NUMBER)
        if DigitalPots.gains_locked:
            self.secondary_gain_off()

    def secondary_gain_off(self):
        self.log.debug("Saving Secondary GAIN value: {}".format(self.digitalpots.value[DigitalPots.SECONDARY_GAIN_POT_NUMBER]))
        self.secondary_gain_saved_value = self.digitalpots.value[DigitalPots.SECONDARY_GAIN_POT_NUMBER]
        self.log.debug("Secondary GAIN setting to OFF")
        DigitalPots.value_change(DigitalPots.SPEED_SLOW,
                                      self.digitalpots.ANTI_CLOCKWISE, DigitalPots.SECONDARY_GAIN_POT_NUMBER)
        if DigitalPots.gains_locked and DigitalPots.off[self.digitalpots.primary_gain_pot_number] is False:
            self.primary_gain_off()

