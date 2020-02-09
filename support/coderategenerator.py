import argparse
import configparser
import os
import pigpio
import threading
import logging

class Coderategenerator(object):
    def __init__(self, config, spi, gpio):
        super().__init__()

        self.config = config
        self.logger = self.config.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.spi = spi
        self.gpio = gpio.GPIO
        self.coderate_stop()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-signal', nargs="+", type=int)
        self.args = self.parser.parse_args()
        self.log.info("Arguments passed into script: " + str(self.args.signal))
        self.passed_list = self.args.signal
        cwd = os.getcwd()
        self.log.debug('Starting up Coderate Generator...')
        self.log.debug("CWD: {}".format(cwd))
        self.config_file_path = "config/coderates.ini"
        self.log.debug('Loading coderate template configuration from ' + str(self.config_file_path))
        self.config_coderates = configparser.ConfigParser()
        self.config_coderates.sections()
        self.config_coderates.read_file(open(self.config_file_path))
        # todo: need to open made config ini file
        self.companies = self.config_coderates.sections()
        self.carrier_freq = self.config_coderates.items('CARRIERS')
        self.coderates = self.config_coderates.items('CODERATES')
        self.company_frequencies_pb = self.config_coderates.items('SIEMENS MOBILITY FREQUENCIES')
        self.company_frequencies = self.company_frequencies_pb[0]
        self.company_frequencies = self.company_frequencies[1]
        self.company_frequencies = self.company_frequencies.split(",")
        self.company_coderates_pb = self.config_coderates.items('SIEMENS MOBILITY CODERATES')
        self.company_coderates = self.company_coderates_pb[0]
        self.company_coderates = self.company_coderates[1]
        self.company_coderates = self.company_coderates.split(",")
        self.log.debug("CarrierFreq Length: {}  {}".format(len(self.carrier_freq), self.carrier_freq))
        self.log.debug("Coderates Length:   {}  {}".format(len(self.coderates), self.coderates, ))
        self.primary_source_frequency = 4915200
        self.secondary_source_frequency = 4915200
        self.companies_list = None
        self.carrier_freq_list = None
        self.coderate_list = None
        self.primary_channel_chip_select_pin = 0
        self.secondary_channel_chip_select_pin = 2
        self.waveform1 = None
        self.speed_generation_shape_override = None
        self.frequency = 0
        self.duty_cycle = 0
        self.spi_msg = []
        self.toggle_pin = self.config.code_rate_generator_toggle_pin
        self.toggle_pin_state = None
        try:
            self.gpio.set_mode(self.toggle_pin, pigpio.OUTPUT)
        except:
            self.log.exception("EXCEPTION in coderate_initialization")


    def pulsecodes_pb(self, company):
        self.log.debug("Reading pulsecode PB data from INI file for company  {}".format(company))

    def frequencies_pb(self, company):
        self.log.debug("Reading frequency PB data from INI file for company  {}".format(company))

    def pulse_codes_from_company(self, company):
        self.log.debug("Reading pulsecode data from INI file for company  {}".format(company))
        good_list = []
        values = []
        company_data = self.config_coderates.items(company)
        company_pulsecodes = filter(lambda x: x[0].startswith('pulsecode'), company_data)
        data = list(company_pulsecodes)
        for k in data:
            # print(k[0])
            # print(k[1])
            coderate_list = k[1].split(",")
            # print("Coderate list {}".format(coderate_list))
            for x in coderate_list:
                # print('x={}'.format(x))
                for y in self.coderates:
                    # print('y={}'.format(y))
                    if x == y[0]:
                        good_list.append(y[1])
                for y in self.carrier_freq:
                    # print('y={}'.format(y))
                    if x == y[0]:
                        good_list.append(y[1])
            values.append(good_list)
            good_list = []
        # print(values)
        # print(values[0])
        # print(values[1])
        # print(values[2])
        return values

    def generate_test_pulse(self, values):
        # This is used to generate the pulses from RPI pins.  This is not implemented currently.  We are using a
        # freq generator for each carrier and then switching between them to generate the coderate.
        # TODO  when we talk about shifting the duty cycle, are we shifting the duty cycle for each carriers freqeuency
        # TODO or are we shiting the carrier for the code rate, meaning less or more of each carrier?

        # we are passed a coderate (in pulses per miunute) and a frequency for one or two of the carrier frequencies.
        # the pulse train is generated by taking the coderate frequency (in hertz) and then switching on an euen portion
        # of each carrier.  if a carrier is missing, it will be turned off for that portion.
        # if we are sent a 180 coderate with a 100hz primary freq and a 250hz secondary freq, the pulse waveform would
        # look like this:  180 coderate = 180 pulses per minute or 3 pulses per second (3hz). each period is 333ms.
        # that means each positive wave is 1/2 of that at 50 % duty cycle, or 166.66 ms.
        # next we have to generate so many pulses of each waveform for the amount of the pos and neg time so since
        # the pos period is 166.66ms we take the primary freq period (100hz at 1/100 = 0.010 or 10 ms. so dividing the
        # pos period of 166.66 / 10ms we get 16.66 waveforms we need to make.  each positive will be 1/2 that for 50%
        # duty cycle, or 8.33ms for each positive and 8.33ms for each negative.
        duty_cycle = 50
        pulses_per_second = 1000000.0
        primary_code_rate_generator_toggle_pin = 27
        secondary_code_rate_generator_toggle_pin = 22

        self.log.debug("Generating Test Pulse")
        self.gpio.wave_clear()
        coderate1_ppm = values[0]
        carrier_freq1 = values[1]
        coderate2_ppm = values[2]
        carrier_freq2 = values[3]

        self.gpio.set_mode(primary_code_rate_generator_toggle_pin, pigpio.OUTPUT)
        self.gpio.set_mode(secondary_code_rate_generator_toggle_pin, pigpio.OUTPUT)
        self.gpio.wave_tx_stop()

        self.log.debug(
            "Received values to generate waveform: CODERATE 1:{}ppm  FREQUENCY 1: {}hz   CODERATE 2: {}ppm  FREQUENCY 2:  {}hz ".format(
                coderate1_ppm, carrier_freq1, coderate2_ppm, carrier_freq2))
        coderate1_period_in_microseconds = int((1 / (coderate1_ppm / 60.0)) * pulses_per_second)
        coderate2_period_in_microseconds = int((1 / (coderate2_ppm / 60.0)) * pulses_per_second)
        self.log.debug("Calculated CODERATE 1 PERIOD: {}usecs   CODERATE 2 PERIOD:  {}usecs".format(
            coderate1_period_in_microseconds, coderate2_period_in_microseconds))
        coderate1_positive_pulse = int(coderate1_period_in_microseconds * (duty_cycle / 100))
        coderate1_negative_pulse = int(coderate1_period_in_microseconds * (1 - (duty_cycle / 100)))
        coderate2_positive_pulse = int(coderate1_period_in_microseconds * (duty_cycle / 100))
        coderate2_negative_pulse = int(coderate1_period_in_microseconds * (1 - (duty_cycle / 100)))
        self.log.debug(
            'CODERATE 1 POS PULSE:{}Usecs   CODERATE 1 NEG PULSE:{}uSecs   CODERATE 2 POS PULSE:{}Usecs   CODERATE 2 NEG PULSE"{}Usecs'.format(
                coderate1_positive_pulse, coderate1_negative_pulse, coderate2_positive_pulse, coderate2_negative_pulse))
        # generate primary carrier frequency
        # assuming 50% duty cycle
        primary_carrier_positive_pulse_microseconds = int(((1 / carrier_freq1) / 2) * pulses_per_second)
        primary_carrier_negative_pulse_microseconds = int(((1 / carrier_freq1) / 2) * pulses_per_second)
        secondary_carrier_positive_pulse_microseconds = int(((1 / carrier_freq2) / 2) * pulses_per_second)
        secondary_carrier_negative_pulse_microseconds = int(((1 / carrier_freq2) / 2) * pulses_per_second)
        self.log.debug(
            "PRI CARRIER POS PULSE {}uSec PRI CARRIER NEG PULSE {}uSec   SEC CARRIER POS PULSE {}uSec SEC CARRIER NEG PULSE {}uSec".format(
                primary_carrier_positive_pulse_microseconds, primary_carrier_negative_pulse_microseconds,
                secondary_carrier_positive_pulse_microseconds, secondary_carrier_negative_pulse_microseconds))

        pulse = []
        wavelength = coderate1_positive_pulse
        while wavelength is not 0:
            # prim car pos
            if wavelength > primary_carrier_positive_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(1 << primary_code_rate_generator_toggle_pin, 0,
                                 primary_carrier_positive_pulse_microseconds))
                wavelength = wavelength - primary_carrier_positive_pulse_microseconds
                self.log.debug('ADDING  PRI CAR POS PULSE WITH LENGTH OF  {}USECS'.format(
                    primary_carrier_positive_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(1 << primary_code_rate_generator_toggle_pin, 0, wavelength))
                self.log.debug('ADDING  PRI CAR POS PULSE WITH LENGTH OF  {}USECS'.format(wavelength))
                wavelength = wavelength - wavelength

            # pri car neg
            if wavelength > primary_carrier_negative_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(0, 1 << primary_code_rate_generator_toggle_pin,
                                 primary_carrier_negative_pulse_microseconds))
                wavelength = wavelength - primary_carrier_negative_pulse_microseconds
                self.log.debug('ADDING  PRI CAR NEG PULSE WITH LENGTH OF  {}USECS'.format(
                    primary_carrier_negative_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(0, 1 << primary_code_rate_generator_toggle_pin, wavelength))
                self.log.debug('ADDING  PRI CAR NEG PULSE WITH LENGTH OF  {}USECS'.format(wavelength))
                wavelength = wavelength - wavelength
            self.log.debug('Wavelength {}'.format(wavelength))

        wavelength = coderate2_positive_pulse
        while wavelength is not 0:
            # sec car pos
            if wavelength > secondary_carrier_positive_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(1 << secondary_code_rate_generator_toggle_pin, 0,
                                 secondary_carrier_positive_pulse_microseconds))
                wavelength = wavelength - secondary_carrier_positive_pulse_microseconds
                self.log.debug('ADDING  SEC CAR POS PULSE WITH LENGTH OF  {}Usecs'.format(
                    secondary_carrier_positive_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(1 << secondary_code_rate_generator_toggle_pin, 0, wavelength))
                self.log.debug('ADDING  SEC CAR POS PULSE WITH LENGTH OF  {}Usecs'.format(wavelength))
                wavelength = wavelength - wavelength

            # sec car neg
            if wavelength > secondary_carrier_negative_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(0, 1 << secondary_code_rate_generator_toggle_pin,
                                 secondary_carrier_negative_pulse_microseconds))
                wavelength = wavelength - secondary_carrier_negative_pulse_microseconds
                self.log.debug('ADDING  SEC CAR NEG PULSE WITH LENGTH OF  {}Usecs'.format(
                    secondary_carrier_negative_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(0, 1 << secondary_code_rate_generator_toggle_pin, wavelength))
                self.log.debug('ADDING  SEC CAR NEG PULSE WITH LENGTH OF  {}Usecs'.format(
                    wavelength))
                wavelength = wavelength - wavelength
            self.log.debug('Wavelength {}'.format(wavelength))
        self.gpio.wave_add_generic(pulse)  # add waveform
        pulses = self.gpio.wave_get_pulses()
        micros = self.gpio.wave_get_micros()
        self.log.debug("Waveform PULSES {}   MICROS {}".format(pulses, micros))
        wf = self.gpio.GPIO.wave_create()
        self.gpio.gpio.GPIO.wave_send_repeat(wf)

    def code_rate_toggle(self):
        self.toggle_pin_state = not self.toggle_pin_state
        self.gpio.write(self.toggle_pin, self.toggle_pin_state)

    def coderate_generate(self, coderate_data):
        """ coderate selection will send the appropriate coderate to be generated.  to generate a coderate we must
        program both the primary and secondary carrier frequency generators with the appropriate frequency.  then
        we must select between the 2 frequencies at the coderate passed to us
        generates code rate frquency which drives 4 channel multiplexer which is used to select between
        the code rate signal frequency and the carrier frequency at the appropriate rate.
        utilizing the PIGPIO library,we build a pulse of desired frequency and duty cycle and send
        out repeatedly"""
        self.log.debug('Generating Coderate: {}'.format(coderate_data))
        duty_cycle = 50
        # todo move to initializiation and place in INI
        pulses_per_second = 1000000.0
        self.log.debug("Creating Coderate Pulse......")
        self.gpio.wave_clear()
        pulse = []
        coderate_ppm = int(coderate_data[0])
        primary_freq = int(coderate_data[1])
        secondary_freq = int(coderate_data[2])
        self.frequency_to_registers(primary_freq, self.primary_source_frequency, 0,
                                    self.primary_channel_chip_select_pin)
        self.frequency_to_registers(secondary_freq, self.secondary_source_frequency, 0,
                                    self.secondary_channel_chip_select_pin)
        if primary_freq is not 0:
            self.gpio.write(self.toggle_pin, 0)
        elif secondary_freq is not 0:
            self.gpio.write(self.toggle_pin, 1)
        self.log.debug(
            "Received values to generate waveform: CODERATE :{}ppm  FREQUENCY 1: {}hz   FREQUENCY 2:  {}hz ".format(
                coderate_ppm, primary_freq, secondary_freq))
        if coderate_ppm is not 1:
            coderate_period_in_microseconds = int((1 / (coderate_ppm / 60.0)) * pulses_per_second)
            coderate_positive_pulse = int(coderate_period_in_microseconds * (duty_cycle / 100))
            coderate_negative_pulse = int(coderate_period_in_microseconds * (1 - (duty_cycle / 100)))
            pulse.append(pigpio.pulse(1 << self.toggle_pin, 0, coderate_positive_pulse))
            pulse.append(pigpio.pulse(0, 1 << self.toggle_pin, coderate_negative_pulse))
            self.gpio.wave_clear()  # clear any existing waveforms
            self.gpio.wave_add_generic(pulse)  # add waveform
            self.waveform1 = self.gpio.wave_create()
            self.gpio.wave_send_repeat(self.waveform1)
            self.log.debug('Starting code rate')
            val = threading.current_thread(), threading.current_thread().name
            self.log.debug("THREAD " + str(val))
        elif coderate_ppm is 1:
            self.coderate_stop()

    def coderate_stop(self):
        self.gpio.wave_tx_stop()
        self.gpio.wave_clear()

    def frequency_to_registers(self, frequency, clock_frequency, shape, cs):
        self.spi_msg = []
        self.log.debug(
            "FREQ TO REG running with FREQ:{} CLK FREQ:{} SHAPE:{}  CS:{}".format(frequency, clock_frequency, shape,
                                                                                  cs))
        word = hex(int(round((frequency * 2 ** 28) / clock_frequency)))  # Calculate frequency word to send
        # TODO REMOVE THIS IS FOR TESTING ONLY
        # shape = 1
        if self.speed_generation_shape_override is not None:
            shape = self.speed_generation_shape_override
        if shape == 1:  # square
            shape_word = 0x2020
        elif shape == 2:  # triangle
            shape_word = 0x2002
        else:
            shape_word = 0x2000  # sine

        MSB = (int(word, 16) & 0xFFFC000) >> 14  # Split frequency word onto its separate bytes
        LSB = int(word, 16) & 0x3FFF
        MSB |= 0x4000  # Set control bits DB15 = 0 and DB14 = 1; for frequency register 0
        LSB |= 0x4000
        self._ad9833_append(0x2100)
        # Set the frequency
        self._ad9833_append(LSB)  # lower 14 bits
        self._ad9833_append(MSB)  # Upper 14 bits
        self._ad9833_append(shape_word)
        self.spi.write(2, self.spi_msg, cs)

    def _ad9833_append(self, integer):
        high, low = divmod(integer, 0x100)
        self.spi_msg.append(high)
        self.spi_msg.append(low)

    # # signal generator creates carrier frequency
    # # TODO :NOT SURE WE ARE USING THIS
    # def signal_generator_set_carrier_signal(self, freq, cs):
    #     freq_text = ""
    #     tmp_reg = 0
    #     # set FREQ over SPI
    #     if freq == self.FREQ_60:
    #         freq_text = '60'
    #         tmp_reg = self.REG_60
    #     elif freq == self.FREQ_100:
    #         freq_text = '100'
    #         tmp_reg = self.REG_100
    #     elif freq == self.FREQ_250:
    #         freq_text = '250'
    #         tmp_reg = self.REG_250
    #     elif freq == self.FREQ_2340:
    #         freq_text = '2340'
    #         tmp_reg = self.REG_2340
    #     elif freq == self.FREQ_4550:
    #         freq_text = '4550'
    #         tmp_reg = self.REG_4550
    #     elif freq == self.FREQ_5525:
    #         freq_text = '5525'
    #         tmp_reg = self.REG_5525
    #     elif freq == self.FREQ_OFF:
    #         freq_text = 'OFF'
    #         tmp_reg = self.REG_OFF
    #     self.log.debug('Setting carrier frequency to: ' + freq_text + ' hz with CS:' + str(cs))
    #     # TODO make sure we do the correct protocol to the AD9833 by resetting it first, etc
    #     self.spi.write(0, tmp_reg, cs)
