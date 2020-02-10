import logging
import time


# **********************************************************************************************
class DigitalPots(object):
    PRIMARY_GAIN_POT_NUMBER = 0
    SECONDARY_GAIN_POT_NUMBER = 1
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
    value = [0,0,0,0]
    COARSE_WIPER_INCREMENT = None
    COARSE_WIPER_DECREMENT = None
    COARSE_WIPER_MAX_BITS = None
    COARSE_WIPER_MIN_BITS = None
    FINE_WIPER_INCREMENT = None
    FINE_WIPER_DECREMENT = None
    FINE_WIPER_MAX_BITS = None
    FINE_WIPER_MIN_BITS = None
    gains_locked = False

    def __init__(self, config, decoder, spi):
        self.config = config
        self.logger = self.config.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.log.debug('Digital Pots initializing...')
        self.decoder = decoder
        self.spi = spi
        self.startup_functions()
        self.log.debug("{} init complete...".format(__name__))

    def startup_functions(self):
        self.config_file_load()

    def value_change(self, speed, direction, potnumber):
        self.log.debug('CHANGE WIPER:Speed:{}   Direction:{}   Pot_Number:{}'.format(speed, direction, potnumber))
        if speed == DigitalPots.SPEED_SLOW:
            if direction == DigitalPots.CLOCKWISE:
                if DigitalPots.gains_locked:
                    DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = DigitalPots.value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] + DigitalPots.SLOW_STEP_AMOUNT
                    DigitalPots.value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not DigitalPots.gains_locked:
                    DigitalPots.value[potnumber] = DigitalPots.value[potnumber] + DigitalPots.SLOW_STEP_AMOUNT
            elif direction == DigitalPots.ANTI_CLOCKWISE:
                if DigitalPots.gains_locked:
                    DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = DigitalPots.value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] - DigitalPots.SLOW_STEP_AMOUNT
                    DigitalPots.value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not DigitalPots.gains_locked:
                    DigitalPots.value[potnumber] = DigitalPots.value[potnumber] - DigitalPots.SLOW_STEP_AMOUNT
        elif speed == DigitalPots.SPEED_FAST:
            if direction == DigitalPots.CLOCKWISE:
                if DigitalPots.gains_locked:
                    DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = DigitalPots.value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] + DigitalPots.FAST_STEP_AMOUNT
                    DigitalPots.value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not DigitalPots.gains_locked:
                    DigitalPots.value[potnumber] = DigitalPots.value[potnumber] + DigitalPots.FAST_STEP_AMOUNT
            elif direction == DigitalPots.ANTI_CLOCKWISE:
                if DigitalPots.gains_locked:
                    DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER] = DigitalPots.value[
                                                                     DigitalPots.PRIMARY_GAIN_POT_NUMBER] - DigitalPots.FAST_STEP_AMOUNT
                    DigitalPots.value[DigitalPots.SECONDARY_GAIN_POT_NUMBER] = DigitalPots.value[DigitalPots.PRIMARY_GAIN_POT_NUMBER]
                elif not DigitalPots.gains_locked:
                    DigitalPots.value[potnumber] = DigitalPots.value[potnumber] - DigitalPots.FAST_STEP_AMOUNT
        if DigitalPots.gains_locked:
            self.value_check(DigitalPots.PRIMARY_GAIN_POT_NUMBER, DigitalPots.value)
            self.value_check(DigitalPots.SECONDARY_GAIN_POT_NUMBER, DigitalPots.value)
        else:
            self.value_check(potnumber, DigitalPots.value)

    def value_check(self, potnumber, val):
        """Each click of the encoder increases the value by approximately 9.7 ohms.  To figure out what values to send
        to each digital pot, i take the total ohms needed divided by the coarse ohms amount.  The remainder then gets
        divided by the fine ohms amout.  Example:  if 210 ohms is needed, then take 210 / 49.7 = 4 coarse bits.  Then
        subtract the coarse amount from the total, to get the fine amount, ie 210 - 200 = 10.  Then take the 10 ohms
        remaining and divide by fine amount of 10 and you get 1 bit needed for the fine digital pot.

        :param value:
        :param potnumber:
        """

        DigitalPots.value[potnumber] = val
        if DigitalPots.value[potnumber] > DigitalPots.total_max_ohms:
            DigitalPots.value[potnumber] = DigitalPots.total_max_ohms
            self.log.debug("POT {} reached MAX".format(potnumber))
        elif DigitalPots.value[potnumber] < DigitalPots.TOTAL_MIN_OHMS:
            DigitalPots.value[potnumber] = DigitalPots.TOTAL_MIN_OHMS
            self.log.debug("POT {} reached MIN".format(potnumber))
            DigitalPots.coarse_wiper[potnumber] = 0
            DigitalPots.fine_wiper[potnumber] = 0
            DigitalPots.fine_wiper_ohms[potnumber] = 0
            DigitalPots.coarse_wiper_ohms[potnumber] = 0
            DigitalPots.actual_ohms[potnumber] = 0
            DigitalPots.off[potnumber] = True
        else:
            if DigitalPots.value[potnumber] < DigitalPots.COARSE_MAX_OHMS:
                DigitalPots.coarse_wiper[potnumber] = int(DigitalPots.value[potnumber] / DigitalPots.coarse_divisor)
                DigitalPots.coarse_wiper_ohms[potnumber] = int(
                    DigitalPots.coarse_wiper[potnumber] * DigitalPots.coarse_divisor)
                DigitalPots.fine_wiper_ohms[potnumber] = DigitalPots.value[potnumber] - DigitalPots.coarse_wiper_ohms[potnumber]
                DigitalPots.fine_wiper[potnumber] = int(
                    DigitalPots.fine_wiper_ohms[potnumber] / DigitalPots.fine_divisor)
                DigitalPots.fine_wiper_ohms[potnumber] = DigitalPots.fine_wiper[potnumber] * DigitalPots.fine_divisor
            if DigitalPots.value[potnumber] > DigitalPots.COARSE_MAX_OHMS:
                DigitalPots.coarse_wiper[potnumber] = min(DigitalPots.COARSE_MAX_BITS,
                                                           (int(DigitalPots.value[potnumber] / DigitalPots.coarse_divisor)))
                DigitalPots.coarse_wiper_ohms[potnumber] = int(
                    DigitalPots.coarse_wiper[potnumber] * DigitalPots.coarse_divisor)
                DigitalPots.fine_wiper_ohms[potnumber] = DigitalPots.value[potnumber] - DigitalPots.coarse_wiper_ohms[potnumber]
                DigitalPots.fine_wiper[potnumber] = int(
                    DigitalPots.fine_wiper_ohms[potnumber] / DigitalPots.fine_divisor)
                DigitalPots.off[potnumber] = False
        coarse_hex, fine_hex = self.int2hex(DigitalPots.coarse_wiper, DigitalPots.fine_wiper)
        self.digitalpots_send_spi(potnumber, coarse_hex, fine_hex)
        DigitalPots.actual_ohms[potnumber] = int(
            DigitalPots.fine_wiper_ohms[potnumber] + DigitalPots.coarse_wiper_ohms[potnumber])
        DigitalPots.wiper_total_percentage[potnumber] = DigitalPots.actual_ohms[
                                                             potnumber] / DigitalPots.total_max_ohms
        self.log.debug(
            "POT {} TOTAL GAIN % {}".format(potnumber, DigitalPots.wiper_total_percentage[potnumber] * 100))
        self.log.debug(
            "RAW: {} ohms   ACTUAL: {} ohms  POT: {} COARSE bits: {}  FINE bits: {}  COARSE ohms: {}  FINE ohms: {} ".format(
                DigitalPots.value[potnumber],
                DigitalPots.actual_ohms[potnumber],
                potnumber,
                DigitalPots.coarse_wiper[potnumber],
                DigitalPots.fine_wiper[potnumber],
                DigitalPots.coarse_wiper_ohms[potnumber],
                DigitalPots.fine_wiper_ohms[potnumber]))

    def digitalpots_send_spi(self, potnumber, coarse_hex, fine_hex):
        self.log.debug('WIPER WRITE potnumber:' + str(potnumber))
        if potnumber == DigitalPots.SECONDARY_GAIN_POT_NUMBER:
            data = DigitalPots.SPI_WRITE_COMMAND + fine_hex[0:2]
            self.spi.write(2, data, self.decoder.chip_select_primary_fine_gain)
            # time.sleep(0.010)
            data = DigitalPots.SPI_WRITE_COMMAND + coarse_hex[0:2]
            self.spi.write(2, data, self.decoder.chip_select_primary_coarse_gain)
        elif potnumber == DigitalPots.SECONDARY_GAIN_POT_NUMBER:
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

    # todo make sure this is working
    def wiper_to_nvram(self):
        """this command when sent to the pots will copy wiper contents to the NV ram,
        so that on power up the pots will go to the NV ram value.
        i want that to be 0
        """
        self.log.debug("COPY WIPER TO NVRAM")
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

    def config_file_load(self):
        DigitalPots.coarse_wiper_increment = self.config.digital_pot_coarse_wiper_increment
        DigitalPots.coarse_wiper_decrement = self.config.digital_pot_coarse_wiper_decrement
        DigitalPots.coarse_wiper_max_bits = self.config.digital_pot_coarse_wiper_max_bits
        DigitalPots.coarse_wiper_min_bits = self.config.digital_pot_coarse_wiper_min_bits
        DigitalPots.fine_wiper_increment = self.config.digital_pot_fine_wiper_increment
        DigitalPots.fine_wiper_decrement = self.config.digital_pot_fine_wiper_decrement
        DigitalPots.fine_wiper_max_bits = self.config.digital_pot_fine_wiper_max_bits
        DigitalPots.fine_wiper_min_bits = self.config.digital_pot_fine_wiper_min_bits