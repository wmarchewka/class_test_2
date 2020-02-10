import logging


class Speedgenerator(object):

    PRIMARY_SOURCE_FREQUENCY = None
    SECONDARY_SOURCE_FREQUENCY = None
    PRIMARY_FREQ_GEN_CONSTANT = None  # 268435456.00  # 2^28
    SECONDARY_FREQ_GEN_CONSTANT = None  # 268435456.00  # 2^28
    SPEED_GENERATOR_SET_SPEED_SPI_HEADER = None  # [0X20, 0X00]
    SPEED_0_CS = None  # 6  # SPEED SIMULATION TACH 1
    SPEED_1_CS = None  # 7  # SPEED SIMULATION TACH 2
    SPEED1_ACTUAL_FREQ = 0
    SPEED2_ACTUAL_FREQ = 0
    SPEED_FREQUENCY = [0, 0]
    SPEED_FREQUENCY_MIN = 0
    SPEED_FREQUENCY_MAX = 1000000
    FREQ_SLOW_INCREMENT = 1
    FREQ_FAST_INCREMENT = 100
    FREQ_SHAPE_SINE = 0
    FREQ_SHAPE_SQUARE = 1
    FREQ_SHAPE_TRIANGLE = 2
    SPEED_SLOW = 0
    SPEED_FAST = 1
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    SPEED_REG = 0
    FREQ_TEXT = ''
    FREQ_SHAPE = [FREQ_SHAPE_SINE, FREQ_SHAPE_SINE]


    def __init__(self, config, decoder, coderategenerator):
        self.init = True
        self.decoder = decoder
        self.coderategenerator = coderategenerator
        self.config = config
        self.logger = self.config.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.startup_processes()    
        self.log.debug("{} init complete...".format(__name__))

    def startup_processes(self):
        self.load_config()
        self.polling_prohibited = (True, self.__class__)
        #self.set_speed_signal()

    
    def set_speed_signal(self, cs: int, speed: int, direction: int) -> int:
        """depending on speed and direction, speed will be incremeneted or
        decremeneted
        :rtype: int
        :param cs: 
        :param speed: 
        :param direction: 
        :return: actual speed
        """
        speed_text = ""
        direction_text = ""
        if cs == Speedgenerator.SPEED_0_CS:
            self.speed_reg = 0
        if cs == Speedgenerator.SPEED_1_CS:
            self.speed_reg = 1
        if speed == Speedgenerator.SPEED_SLOW:
            speed_text = "SLOW"
        if speed == Speedgenerator.SPEED_FAST:
            speed_text = "FAST"
        if direction == Speedgenerator.CLOCKWISE:
            direction_text = "CLOCKWISE"
        if direction == Speedgenerator.ANTI_CLOCKWISE:
            direction_text = "ANTI CLOCKWISE"
        self.log.debug(
            'SIGGEN Setting speed with CS:{}  with speed of:{}  direction:{} '.format(cs, speed_text,
                                                                                      direction_text))
        if direction == self.CLOCKWISE:
            if speed == self.SPEED_SLOW:
                self.SPEED_FREQUENCY[self.speed_reg] = self.SPEED_FREQUENCY[
                                                           self.speed_reg] + self.FREQ_SLOW_INCREMENT
            elif speed == self.SPEED_FAST:
                self.SPEED_FREQUENCY[self.speed_reg] = self.SPEED_FREQUENCY[
                                                           self.speed_reg] + self.FREQ_FAST_INCREMENT
            if self.SPEED_FREQUENCY[self.speed_reg] > self.SPEED_FREQUENCY_MAX:
                self.SPEED_FREQUENCY[self.speed_reg] = self.SPEED_FREQUENCY_MAX
        elif direction == self.ANTI_CLOCKWISE:
            if speed == self.SPEED_SLOW:
                self.SPEED_FREQUENCY[self.speed_reg] = self.SPEED_FREQUENCY[
                                                           self.speed_reg] - self.FREQ_SLOW_INCREMENT
            elif speed == self.SPEED_FAST:
                self.SPEED_FREQUENCY[self.speed_reg] = self.SPEED_FREQUENCY[
                                                           self.speed_reg] - self.FREQ_FAST_INCREMENT
            if self.SPEED_FREQUENCY[self.speed_reg] < self.SPEED_FREQUENCY_MIN:
                self.SPEED_FREQUENCY[self.speed_reg] = self.SPEED_FREQUENCY_MIN
        self.speed1_actual_freq = self.SPEED_FREQUENCY[0]
        self.speed2_actual_freq = self.SPEED_FREQUENCY[1]
        self.log.debug('SIGGEN Speed 1 Actual Freq: {}'.format(self.speed1_actual_freq))
        self.log.debug('SIGGEN Speed 2 Actual Freq: {}'.format(self.speed2_actual_freq))
        if cs == self.SPEED_0_CS:
            return self.speed1_actual_freq
        if cs == self.SPEED_1_CS:
            return self.speed2_actual_freq

    def speed_off(self, speed_generator: int) -> object:
        """pass speed generator 1 or 2  
        :rtype:
        :param speed_generator:
        """
        cs = None
        self.log.debug("Speed {} frequency generator setting to OFF".format(speed_generator))
        self.SPEED_FREQUENCY[speed_generator] = 0
        if speed_generator == 1:
            cs = self.decoder.chip_select_speed_tach_1
        elif speed_generator == 2:
            cs = self.decoder.chip_select_speed_tach_2
        self.set_speed_signal(cs, self.SPEED_SLOW,
                              self.ANTI_CLOCKWISE)
        return True

    def load_config(self):
        self.primary_source_frequency = self.config.primary_source_frequency
        self.secondary_source_frequency = self.config.secondary_source_frequency
        self.primary_freq_gen_constant = self.config.primary_freq_gen_constant  # 268435456.00  # 2^28
        self.secondary_freq_gen_constant = self.config.secondary_freq_gen_constant  # 268435456.00  # 2^28
        self.speed_generator_set_speed_spi_header = self.config.speed_generator_set_speed_spi_header  # [0x20, 0x00]
        self.freq_shape = [self.FREQ_SHAPE_SINE, self.FREQ_SHAPE_SINE]
        self.SPEED_0_CS = self.config.SPEED_0_CS  # 6  # SPEED SIMULATION TACH 1
        self.SPEED_1_CS = self.config.SPEED_1_CS  # 7  # SPEED SIMULATION TACH 2
        Speedgenerator.primary_source_frequency = self.primary_source_frequency
        Speedgenerator.secondary_source_frequency = self.secondary_source_frequency
        Speedgenerator.primary_freq_gen_constant = self.primary_freq_gen_constant  # 26
        Speedgenerator.secondary_freq_gen_constant = self.secondary_freq_gen_constant
        Speedgenerator.speed_generator_set_speed_spi_header = self.speed_generator_set_speed_spi_header
        Speedgenerator.SPEED_0_CS = self.SPEED_0_CS  # 6  # SPEED SIMULATION TACH 1
        Speedgenerator.SPEED_1_CS = self.SPEED_1_CS  # 7  # SPEED SIMULATION TACH 2