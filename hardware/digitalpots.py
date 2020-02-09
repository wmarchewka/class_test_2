import logging
import time


# **********************************************************************************************
class DigitalPots(object):
    PRIMARY_GAIN_POT_NUMBER = 0
    SECONDARY_GAIN_POT_NUMBER = 1
    coarse_wiper_increment = None
    COARSE_MAX_OHMS = 50070
    COARSE_MAX_BITS = 1023
    STARTING_RESISTANCE = 180
    SPEED_SLOW = 0
    SPEED_FAST = 1
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    SLOW_STEP_AMOUNT = 5  # since each endcoder interrupts twice per click, i changed this to 5
    FAST_STEP_AMOUNT = 500
    SPI_WRITE_COMMAND = [0X00]
    SPI_WIPER_TO_NVRAM_COMMAND = [0b00100000]
    SPI_NVRAM_TO_WIPER_COMMAND = [0b00110000]
    FINE_MAX_OHMS = 10070
    FINE_MAX_BITS = 1023
    TOTAL_MIN_OHMS = 0
    fine_wiper = [0, 0]
    coarse_wiper = [0, 0]
    fine_divisor = FINE_MAX_OHMS / FINE_MAX_BITS
    total_max_ohms = COARSE_MAX_OHMS + FINE_MAX_OHMS
    coarse_divisor = COARSE_MAX_OHMS / COARSE_MAX_BITS
    coarse_wiper_percentage = [0, 0]
    coarse_wiper_resistance = [0, 0]
    coarse_wiper_ohms = [0, 0]
    fine_wiper_percentage = [0, 0]
    fine_wiper_resistance = [0, 0]
    fine_wiper_ohms = [0, 0]
    wiper_total_percentage = [0, 0]
    actual_ohms = [0, 0]
    off = [None, None]
    value = []

    def __init__(self, config, decoder, spi):
        self.config = config
        self.logger = self.config.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.log.debug('Digital Pots initializing...')
        self.decoder = decoder
        self.spi = spi
        self.gains_locked = False
        self.log.debug("{} init complete...".format(__name__))


    def value_change(self, speed, direction, pot_number, value=None):
        self.log.debug('CHANGE WIPER:Speed:{}   Direction:{}   Pot_Number:{}'.format(speed, direction, pot_number))
        if speed == DigitalPots.SPEED_SLOW:
            if direction == DigitalPots.CLOCKWISE:
                if self.gains_locked:
                    value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] + DigitalPots.SLOW_STEP_AMOUNT
                    value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not self.gains_locked:
                    value[pot_number] = value[pot_number] + DigitalPots.SLOW_STEP_AMOUNT
            elif direction == DigitalPots.ANTI_CLOCKWISE:
                if self.gains_locked:
                    value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] - DigitalPots.SLOW_STEP_AMOUNT
                    value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not self.gains_locked:
                    value[pot_number] = value[pot_number] - DigitalPots.SLOW_STEP_AMOUNT
        elif speed == DigitalPots.SPEED_FAST:
            if direction == DigitalPots.CLOCKWISE:
                if self.gains_locked:
                    value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] + DigitalPots.FAST_STEP_AMOUNT
                    value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not self.gains_locked:
                    value[pot_number] = value[pot_number] + DigitalPots.FAST_STEP_AMOUNT
            elif direction == DigitalPots.ANTI_CLOCKWISE:
                if self.gains_locked:
                    value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] - DigitalPots.FAST_STEP_AMOUNT
                    value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not self.gains_locked:
                    value[pot_number] = value[pot_number] - DigitalPots.FAST_STEP_AMOUNT
        if self.gains_locked:
            self.value_check(DigitalPots.PRIMARY_GAIN_POT_NUMBER, value)
            self.value_check(DigitalPots.SECONDARY_GAIN_POT_NUMBER, value)
        else:
            self.value_check(pot_number, value)

    def value_check(self, pot_number, value):
        """Each click of the encoder increases the value by approximately 9.7 ohms.  To figure out what values to send
        to each digital pot, i take the total ohms needed divided by the coarse ohms amount.  The remainder then gets
        divided by the fine ohms amout.  Example:  if 210 ohms is needed, then take 210 / 49.7 = 4 coarse bits.  Then
        subtract the coarse amount from the total, to get the fine amount, ie 210 - 200 = 10.  Then take the 10 ohms
        remaining and divide by fine amount of 10 and you get 1 bit needed for the fine digital pot.

        :param pot_number:
        """
        if value[pot_number] > DigitalPots.total_max_ohms:
            value[pot_number] = DigitalPots.total_max_ohms
            self.log.debug("POT {} reached MAX".format(pot_number))
        elif value[pot_number] < DigitalPots.TOTAL_MIN_OHMS:
            value[pot_number] = DigitalPots.TOTAL_MIN_OHMS
            self.log.debug("POT {} reached MIN".format(pot_number))
            DigitalPots.coarse_wiper[pot_number] = 0
            DigitalPots.fine_wiper[pot_number] = 0
            DigitalPots.fine_wiper_ohms[pot_number] = 0
            DigitalPots.coarse_wiper_ohms[pot_number] = 0
            DigitalPots.actual_ohms[pot_number] = 0
            DigitalPots.off[pot_number] = True
        else:
            if value[pot_number] < DigitalPots.COARSE_MAX_OHMS:
                DigitalPots.coarse_wiper[pot_number] = int(value[pot_number] / DigitalPots.coarse_divisor)
                DigitalPots.coarse_wiper_ohms[pot_number] = int(
                    DigitalPots.coarse_wiper[pot_number] * DigitalPots.coarse_divisor)
                DigitalPots.fine_wiper_ohms[pot_number] = value[pot_number] - DigitalPots.coarse_wiper_ohms[pot_number]
                DigitalPots.fine_wiper[pot_number] = int(
                    DigitalPots.fine_wiper_ohms[pot_number] / DigitalPots.fine_divisor)
                DigitalPots.fine_wiper_ohms[pot_number] = DigitalPots.fine_wiper[pot_number] * DigitalPots.fine_divisor
            if value[pot_number] > DigitalPots.COARSE_MAX_OHMS:
                DigitalPots.coarse_wiper[pot_number] = min(DigitalPots.COARSE_MAX_BITS,
                                                           (int(value[pot_number] / DigitalPots.coarse_divisor)))
                DigitalPots.coarse_wiper_ohms[pot_number] = int(
                    DigitalPots.coarse_wiper[pot_number] * DigitalPots.coarse_divisor)
                DigitalPots.fine_wiper_ohms[pot_number] = value[pot_number] - DigitalPots.coarse_wiper_ohms[pot_number]
                DigitalPots.fine_wiper[pot_number] = int(
                    DigitalPots.fine_wiper_ohms[pot_number] / DigitalPots.fine_divisor)
                DigitalPots.off[pot_number] = False
        coarse_hex, fine_hex = self.int2hex(DigitalPots.coarse_wiper, DigitalPots.fine_wiper)

        # ***********************************************
        self.digitalpots_send_spi(pot_number, coarse_hex, fine_hex)
        DigitalPots.actual_ohms[pot_number] = int(
            DigitalPots.fine_wiper_ohms[pot_number] + DigitalPots.coarse_wiper_ohms[pot_number])
        DigitalPots.wiper_total_percentage[pot_number] = DigitalPots.actual_ohms[
                                                             pot_number] / DigitalPots.total_max_ohms
        self.log.debug(
            "POT {} TOTAL GAIN % {}".format(pot_number, DigitalPots.wiper_total_percentage[pot_number] * 100))
        self.log.debug(
            "RAW: {} ohms   ACTUAL: {} ohms  POT: {} COARSE bits: {}  FINE bits: {}  COARSE ohms: {}  FINE ohms: {} ".format(
                value[pot_number],
                DigitalPots.actual_ohms[pot_number],
                pot_number,
                DigitalPots.coarse_wiper[pot_number],
                DigitalPots.fine_wiper[pot_number],
                DigitalPots.coarse_wiper_ohms[pot_number],
                DigitalPots.fine_wiper_ohms[pot_number]))

    def digitalpots_send_spi(self, pot_number, coarse_hex, fine_hex):
        self.log.debug('WIPER WRITE pot_number:' + str(pot_number))
        if pot_number == DigitalPots.PRIMARY_GAIN_POT_NUMBER:
            data = DigitalPots.SPI_WRITE_COMMAND + fine_hex[0:2]
            self.spi.write(2, data, self.decoder.chip_select_primary_fine_gain)
            # time.sleep(0.010)
            data = DigitalPots.SPI_WRITE_COMMAND + coarse_hex[0:2]
            self.spi.write(2, data, self.decoder.chip_select_primary_coarse_gain)
        elif pot_number == DigitalPots.SECONDARY_GAIN_POT_NUMBER:
            data = DigitalPots.SPI_WRITE_COMMAND + fine_hex[2:4]
            self.spi.write(2, data, self.decoder.chip_select_secondary_fine_gain)
            # time.sleep(0.010)
            data = DigitalPots.SPI_WRITE_COMMAND + coarse_hex[2:4]
            self.spi.write(2, data, self.decoder.chip_select_secondary_coarse_gain)

    # support routine to convert intergers to hex
    def int2hex(self, coarse_wiper, fine_wiper):
        coarse_hex = [(coarse_wiper[0] >> 2), (coarse_wiper[0] & 0b11) << 6,
                      (coarse_wiper[1] >> 2), (coarse_wiper[1] & 0b11) << 6]
        fine_hex = [(fine_wiper[0] >> 2), (fine_wiper[0] & 0b11) << 6,
                    (fine_wiper[1] >> 2), (fine_wiper[1] & 0b11) << 6]
        self.log.debug("Coarse HEX {} | Fine HEX {}".format(coarse_hex, fine_hex))
        return coarse_hex, fine_hex

    def nvram_to_wiper(self):
        # todo make sure this is working
        self.log.debug("COPY NVRAM TO WIPER")
        # this command when sent to the pots will copy wiper contents to the NV ram,
        # so that on power up the pots will go to the NV ram value.
        # i want that to be 0
        spi_msg = DigitalPots.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_coarse_gain)
        time.sleep(0.020)  # delay per data sheet
        spi_msg = DigitalPots.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_fine_gain)
        time.sleep(0.020)
        spi_msg = DigitalPots.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_coarse_gain)
        time.sleep(0.020)
        spi_msg = DigitalPots.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_fine_gain)
        time.sleep(0.020)

    def wiper_to_nvram(self):
        # todo make sure this is working
        self.log.debug("COPY WIPER TO NVRAM")
        # this command when sent to the pots will copy wiper contents to the NV ram,
        # so that on power up the pots will go to the NV ram value.
        # i want that to be 0
        spi_msg = DigitalPots.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_coarse_gain)
        time.sleep(0.020)
        spi_msg = DigitalPots.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_fine_gain)
        time.sleep(0.020)
        spi_msg = DigitalPots.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_coarse_gain)
        time.sleep(0.020)
        spi_msg = DigitalPots.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_fine_gain)
        time.sleep(0.020)