import configparser
import ast
import logging


class Config(object):


    def __init__(self, logger):
        self.init = True
        self.logger = logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.config_file_path = "config/config.ini"
        self.log.info("Logging config file path {}".format(self.config_file_path))
        self.log.info('Loading log configuration from {}'.format(self.config_file_path))
        self.config = configparser.ConfigParser()
        self.config.sections()
        self.config.read_file(open(self.config_file_path))

        # GPIO
        self.ports = self.config.get('GPIO', 'ports')  # read in from INI file
        self.ports = ast.literal_eval(self.ports)

        # ROTARY SECTION
        self.speed_threshold = self.config.getfloat('ROTARY', 'threshold')  # read in from INI file
        self.bouncetime = self.config.getint('ROTARY', 'bouncetime')
        self.rotary_0_pins = self.config.get('ROTARY', 'rotary_0_pins')
        self.rotary_0_pins = ast.literal_eval(self.rotary_0_pins)
        self.rotary_1_pins = self.config.get('ROTARY', 'rotary_1_pins')
        self.rotary_1_pins = ast.literal_eval(self.rotary_1_pins)
        self.rotary_2_pins = self.config.get('ROTARY', 'rotary_2_pins')
        self.rotary_2_pins = ast.literal_eval(self.rotary_2_pins)
        self.rotary_3_pins = self.config.get('ROTARY', 'rotary_3_pins')
        self.rotary_3_pins = ast.literal_eval(self.rotary_3_pins)
        self.rotary_0_pin_0_debounce = self.config.getint('ROTARY', 'rotary_0_pin_0_debounce_microseconds')
        self.rotary_0_pin_1_debounce = self.config.getint('ROTARY', 'rotary_0_pin_1_debounce_microseconds')
        self.rotary_1_pin_0_debounce = self.config.getint('ROTARY', 'rotary_1_pin_0_debounce_microseconds')
        self.rotary_1_pin_1_debounce = self.config.getint('ROTARY', 'rotary_1_pin_1_debounce_microseconds')
        self.rotary_2_pin_0_debounce = self.config.getint('ROTARY', 'rotary_2_pin_0_debounce_microseconds')
        self.rotary_2_pin_1_debounce = self.config.getint('ROTARY', 'rotary_2_pin_1_debounce_microseconds')
        self.rotary_3_pin_0_debounce = self.config.getint('ROTARY', 'rotary_3_pin_0_debounce_microseconds')
        self.rotary_3_pin_1_debounce = self.config.getint('ROTARY', 'rotary_3_pin_1_debounce_microseconds')

        # DIGITAL POT SECTION
        self.digital_pot_fine_wiper_increment = self.config.getint('DIGITAL_POT', 'fine_wiper_increment')
        self.digital_pot_fine_wiper_decrement = self.config.getint('DIGITAL_POT', 'fine_wiper_decrement')
        self.digital_pot_coarse_wiper_increment = self.config.getint('DIGITAL_POT', 'coarse_wiper_increment')
        self.digital_pot_coarse_wiper_decrement = self.config.getint('DIGITAL_POT', 'coarse_wiper_decrement')
        self.digital_pot_fine_wiper_max_bits = self.config.getint('DIGITAL_POT', 'fine_wiper_max_bits')
        self.digital_pot_fine_wiper_min_bits = self.config.getint('DIGITAL_POT', 'fine_wiper_min_bits')
        self.digital_pot_coarse_wiper_max_bits = self.config.getint('DIGITAL_POT', 'coarse_wiper_max_bits')
        self.digital_pot_coarse_wiper_min_bits = self.config.getint('DIGITAL_POT', 'coarse_wiper_min_bits')

        # SPEED GENERATOR SECTION
        self.freq_regs_max = self.config.getint('SPEED_GENERATOR', 'freq_regs_max')
        self.freq_regs_min = self.config.getint('SPEED_GENERATOR', 'freq_regs_min')
        self.primary_source_frequency = self.config.getfloat('SPEED_GENERATOR', 'primary_source_frequency')
        self.secondary_source_frequency = self.config.getfloat('SPEED_GENERATOR', 'secondary_source_frequency')
        self.primary_freq_gen_constant = self.config.getfloat('SPEED_GENERATOR', 'primary_freq_gen_constant')
        self.secondary_freq_gen_constant = self.config.getfloat('SPEED_GENERATOR', 'secondary_freq_gen_constant')
        self.REG_60 = self.config.get('SPEED_GENERATOR', 'REG_60')
        self.REG_60 = ast.literal_eval(self.REG_60)
        self.REG_100 = self.config.get('SPEED_GENERATOR', 'REG_100')
        self.REG_100 = ast.literal_eval(self.REG_100)
        self.REG_250 = self.config.get('SPEED_GENERATOR', 'REG_250')
        self.REG_250 = ast.literal_eval(self.REG_250)
        self.REG_2340 = self.config.get('SPEED_GENERATOR', 'REG_2340')
        self.REG_2340 = ast.literal_eval(self.REG_2340)
        self.REG_4550 = self.config.get('SPEED_GENERATOR', 'REG_4550')
        self.REG_4550 = ast.literal_eval(self.REG_4550)
        self.REG_5525 = self.config.get('SPEED_GENERATOR', 'REG_5525')
        self.REG_5525 = ast.literal_eval(self.REG_5525)
        self.REG_OFF = self.config.get('SPEED_GENERATOR', 'REG_OFF')
        self.REG_OFF = ast.literal_eval(self.REG_OFF)
        self.freq_regs_slow_increment = self.config.getint('SPEED_GENERATOR', 'freq_regs_slow_increment')
        self.freq_regs_fast_increment = self.config.getint('SPEED_GENERATOR', 'freq_regs_fast_increment')
        self.freq_regs_slow_decrement = self.config.getint('SPEED_GENERATOR', 'freq_regs_slow_decrement')
        self.freq_regs_fast_decrement = self.config.getint('SPEED_GENERATOR', 'freq_regs_fast_decrement')
        self.speed_generator_set_speed_spi_header = self.config.get("SPEED_GENERATOR",
                                                                    'set_speed_spi_header')
        self.speed_generator_set_speed_spi_header = list(ast.literal_eval(self.speed_generator_set_speed_spi_header))
        self.PRI_CAR_CS = self.config.getint('SPEED_GENERATOR', 'PRI_CAR_CS')
        self.SEC_CAR_CS = self.config.getint('SPEED_GENERATOR', 'SEC_CAR_CS')
        self.SPEED_0_CS = self.config.getint('SPEED_GENERATOR', 'SPEED_0_CS')
        self.SPEED_1_CS = self.config.getint('SPEED_GENERATOR', 'SPEED_1_CS')

        # DECODER SECTION
        self.decoder_pin_select = self.config.get('DECODER', 'pin_select')
        self.decoder_pin_select = ast.literal_eval(self.decoder_pin_select)
        self.decoder_pin_A = self.config.get('DECODER', 'decoder_pin_A')
        self.decoder_pin_A = ast.literal_eval(self.decoder_pin_A)
        self.decoder_pin_B = self.config.get('DECODER', 'decoder_pin_B')
        self.decoder_pin_B = ast.literal_eval(self.decoder_pin_B)
        self.decoder_pin_C = self.config.get('DECODER', 'decoder_pin_C')
        self.decoder_pin_C = ast.literal_eval(self.decoder_pin_C)

        # SPI SECTION
        self.spi_bus = self.config.getint('SPI', 'spi_bus')
        self.spi_chip_select = list(range(3))
        self.spi_chip_select[0] = self.config.getint('SPI', 'spi1_0_chip_select')
        self.spi_chip_select[2] = self.config.getint('SPI', 'spi1_2_chip_select')
        self.spi1_0_max_speed_hz = self.config.getint('SPI', 'spi1_0_max_speed_hz')
        self.spi1_2_max_speed_hz = self.config.getint('SPI', 'spi1_2_max_speed_hz')
        self.spi1_0_mode = self.config.getint('SPI', 'spi1_0_mode')
        self.spi1_2_mode = self.config.getint('SPI', 'spi1_2_mode')

        # CODERATE
        self.code_rate_generator_toggle_pin = self.config.getint('CODE RATE', 'code_rate_mux_pin')
        self.log.debug("{} init complete...".format(__name__))

        #GUI
        self.display_brightness = self.config.getint('MAIN', 'screen_brightness')
        self.guiname = self.config.get('MAIN', 'gui')
        self.poll_timer_interval = self.config.getint('MAIN', 'poll_timer_interval')
        self.local_timer_interval = self.config.getint('MAIN', 'local_timer_interval')
        self.sense_timer_interval = self.config.getfloat('MAIN', 'sense_timer_interval')
        self.switch_timer_interval = self.config.getint('MAIN', 'switch_timer_interval')
        self.screen_brightness_max = self.config.getint('MAIN', 'screen_brightness_max')
        self.screen_brightness_min = self.config.getint('MAIN', 'screen_brightness_min')