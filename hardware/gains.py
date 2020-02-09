import logging


# **********************************************************************************************
class Gains(object):

    def __init__(self, digitalpots):
        self.digitalpots = digitalpots
        self.logger = self.digitalpots.logger
        self.log = logging.getLogger(__name__)
        self.log.debug('Gains initializing...')
        self.secondary_gain_set_percent(0)
        self.setval_and_store(0)
        self.primary_gain_saved_value = 0
        self.secondary_gain_saved_value = 0
        self.log.debug("{} init complete...".format(__name__))

    def setval_and_store(self, ohm_value):  # upon start up, set gains to 0 and
        self.primary_gain_set_percent(ohm_value)  # store to nvram, so that the pots
        self.digitalpots.wiper_to_nvram()  # always start up with gain to 0

    def primary_gain_set_ohms(self, value):
        ohm_value = value
        self.digitalpots.value[0] = ohm_value
        self.digitalpots.value_check(0)

    def secondary_gain_set_ohms(self, value):
        ohm_value = value
        self.digitalpots.value[1] = ohm_value
        self.digitalpots.value_check(1)

    def primary_gain_set_percent(self, value):
        value = value / 100
        ohm_value = self.digitalpots.total_max_ohms * value
        self.digitalpots.value[0] = ohm_value
        self.digitalpots.value_check(0)

    def secondary_gain_set_percent(self, value):
        value = value / 100
        ohm_value = self.digitalpots.total_max_ohms * value
        self.digitalpots.value[1] = ohm_value
        self.digitalpots.value_check(1)

    def primary_gain_set_value(self, coarse_ohms, fine_ohms):
        self.log.debug("Primary Gain received Coarse :{}  Fine :{}".format(coarse_ohms, fine_ohms))
        coarse = (coarse_ohms / self.digitalpots.coarse_max_ohms) * self.digitalpots.digital_pot_coarse_wiper_max_bits
        fine = (fine_ohms / self.digitalpots.coarse_fine_ohms) * self.digitalpots.digital_pot_fine_wiper_max_bits
        self.digitalpots.coarse_wiper[0] = int(coarse)
        self.digitalpots.fine_wiper[0] = int(fine)
        self.log.debug("Primary GAIN setting OHMS to COARSE: {} FINE: {} ".format(int(coarse), int(fine)))
        self.digitalpots.value_change(self.digitalpots.speed_fast, 0, 0)
        self.digitalpots.value_change(self.digitalpots.speed_slow, 0, 0)

    def secondary_gain_set_value(self, coarse_ohms, fine_ohms):
        self.log.debug("Secondary Gain received Coarse :{}  Fine :{}".format(coarse_ohms, fine_ohms))
        coarse = (coarse_ohms / self.digitalpots.coarse_max_ohms) * self.digitalpots.digital_pot_coarse_wiper_max_bits
        fine = (fine_ohms / self.digitalpots.coarse_fine_ohms) * self.digitalpots.digital_pot_fine_wiper_max_bits
        self.digitalpots.coarse_wiper[1] = int(coarse)
        self.digitalpots.fine_wiper[1] = int(fine)
        self.log.debug("Primary GAIN setting OHMS to FINE: {} COARSE: {} ".format(int(fine), int(coarse)))
        self.digitalpots.value_change(self.digitalpots.speed_slow, 0, 1)
        self.digitalpots.value_change(self.digitalpots.speed_fast, 0, 1)

    def primary_gain_off(self):
        self.log.debug("Saving PRIMARY GAIN value: {}".format(self.digitalpots.value[0]))
        self.primary_gain_saved_value = self.digitalpots.value[0]
        self.log.debug("PRIMARY GAIN setting to OFF")
        self.digitalpots.value[0] = 0
        self.digitalpots.value_change(self.digitalpots.speed_slow,
                                       self.digitalpots.anti_clockwise, 0)
        if self.digitalpots.gains_locked:
            self.secondary_gain_off()

    def secondary_gain_off(self):
        self.log.debug("Saving Secondary GAIN value: {}".format(self.digitalpots.value[1]))
        self.secondary_gain_saved_value = self.digitalpots.value[1]
        self.log.debug("Secondary GAIN setting to OFF")
        self.digitalpots.value[1] = 0
        self.digitalpots.value_change(self.digitalpots.speed_slow,
                                       self.digitalpots.anti_clockwise, 1)
        if self.digitalpots.gains_locked and self.digitalpots.off[self.digitalpots.primary_gain_pot_number] is False:
            self.primary_gain_off()





