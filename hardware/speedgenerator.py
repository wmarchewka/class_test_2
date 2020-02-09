import logging


class Speedgenerator(object, ):
    def __init__(self, commander, config,  decoder, coderategenerator):
        self.init = True
        self.commander = commander
        self.decoder = decoder
        self.coderategenerator = coderategenerator
        self.config = config
        self.logger = self.commander.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.polling_prohibited = (True, self.__class__)
        self.log.debug("{} init complete...".format(__name__))
        self.SPEED_0_CS = self.config.SPEED_0_CS  # 6  # SPEED SIMULATION TACH 1
        self.SPEED_1_CS = self.config.SPEED_1_CS  # 7  # SPEED SIMULATION TACH 2
        self.speed1_actual_freq = 0
        self.speed2_actual_freq = 0
        self.speed_frequency = [0, 0]
        self.speed_frequency_min = 0
        self.speed_frequency_max = 1000000
        self.freq_slow_increment = 1
        self.freq_fast_increment = 100
        self.freq_shape_sine = 0
        self.freq_shape_square = 1
        self.freq_shape_triangle = 2
        self.speed_slow = 0
        self.speed_fast = 1
        self.clockwise = 1
        self.anti_clockwise = -1
        self.speed_reg = 0
        self.primary_source_frequency = self.config.primary_source_frequency
        self.secondary_source_frequency = self.config.secondary_source_frequency
        self.primary_freq_gen_constant = self.config.primary_freq_gen_constant  # 268435456.00  # 2^28
        self.secondary_freq_gen_constant = self.config.secondary_freq_gen_constant  # 268435456.00  # 2^28
        self.speed_generator_set_speed_spi_header = self.config.speed_generator_set_speed_spi_header  # [0x20, 0x00]
        self.freq_text = ''
        self.freq_shape = [self.freq_shape_sine, self.freq_shape_sine]
        # signal generator creates speed signal
        # TODO allow this to take signal shape
        self.log.debug("{} init complete...".format(__name__))


    def set_speed_signal(self, cs, speed, direction):
        speed_text = ""
        direction_text = ""
        if cs == self.SPEED_0_CS:
            self.speed_reg = 0
        if cs == self.SPEED_1_CS:
            self.speed_reg = 1
        if speed == self.speed_slow:
            speed_text = "SLOW"
        if speed == self.speed_fast:
            speed_text = "FAST"
        if direction == self.clockwise:
            direction_text = "CLOCKWISE"
        if direction == self.anti_clockwise:
            direction_text = "ANTI CLOCKWISE"
        self.log.debug(
            'SIGGEN Setting speed with CS:{}  with speed of:{}  direction:{} '.format(cs, speed_text,
                                                                                      direction_text))
        if direction == self.clockwise:
            if speed == self.speed_slow:
                self.speed_frequency[self.speed_reg] = self.speed_frequency[
                                                           self.speed_reg] + self.freq_slow_increment
            elif speed == self.speed_fast:
                self.speed_frequency[self.speed_reg] = self.speed_frequency[
                                                           self.speed_reg] + self.freq_fast_increment
            if self.speed_frequency[self.speed_reg] > self.speed_frequency_max:
                self.speed_frequency[self.speed_reg] = self.speed_frequency_max
        elif direction == self.anti_clockwise:
            if speed == self.speed_slow:
                self.speed_frequency[self.speed_reg] = self.speed_frequency[
                                                           self.speed_reg] - self.freq_slow_increment
            elif speed == self.speed_fast:
                self.speed_frequency[self.speed_reg] = self.speed_frequency[
                                                           self.speed_reg] - self.freq_fast_increment
            if self.speed_frequency[self.speed_reg] < self.speed_frequency_min:
                self.speed_frequency[self.speed_reg] = self.speed_frequency_min
        self.speed1_actual_freq = self.speed_frequency[0]
        self.speed2_actual_freq = self.speed_frequency[1]
        self.log.debug('SIGGEN Speed 1 Actual Freq:'.format(self.speed1_actual_freq))
        self.log.debug('SIGGEN Speed 2 Actual Freq:'.format(self.speed2_actual_freq))
        self.coderategenerator.frequency_to_registers(self.speed_frequency[self.speed_reg],
                                                        self.primary_source_frequency,
                                                        self.freq_shape[self.speed_reg], cs)

    def speed_1_off(self):
        self.log.debug("Speed 1 frequency generator setting to OFF")
        self.speed_frequency[0] = 0
        self.set_speed_signal(self.decoder.chip_select_speed_tach_1, self.speed_slow,
                              self.anti_clockwise)

    def speed_2_off(self):
        self.log.debug("Speed 2 frequency generator setting to OFF")
        self.speed_frequency[1] = 0
        self.set_speed_signal(self.decoder.chip_select_speed_tach_2, self.speed_slow,
                              self.anti_clockwise)

