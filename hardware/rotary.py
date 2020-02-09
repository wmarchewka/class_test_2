import pigpio
import logging
import time

class Rotary(object):

    SPEED_FAST = 1
    SPEED_SLOW = 0
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    last_interrupt_time_rotary0_pin0 = 0
    last_interrupt_time_rotary0_pin1 = 0
    last_interrupt_time_rotary1_pin0 = 0
    last_interrupt_time_rotary1_pin1 = 0
    last_interrupt_time_rotary2_pin0 = 0
    last_interrupt_time_rotary2_pin1 = 0
    last_interrupt_time_rotary3_pin0 = 0
    last_interrupt_time_rotary3_pin1 = 0
    zone = [0, 0, 0, 0]  # used to calculate direction
    prevZone = [0, 0, 0, 0]
    rotary_num = [0, 1, 2, 3]  # ID for each encoder

    def __init__(self, pollingpermission, gpio, config, speedgenerator):

        self.init = True
        self.gpio = gpio
        self.GPIO = gpio.GPIO
        self.config = config
        self.speedgenerator = speedgenerator
        self.pollingpermission = pollingpermission
        self.commander = pollingpermission.commander
        self.logger = self.commander.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.log.debug("gpio {}".format(gpio))
        self.log.debug(self.__dict__)
        self.rotary_interrupts(True)
        self.enable_callbacks()
        self.log.debug("{} init complete...".format(__name__))

        # these pins are for the encoders

    def enable_interrupts(self):
        self.log.debug('ROTARY INTERRUPTS ENABLING...')
        try:
            # switch 3 ENCODER SPEED 1
            self.GPIO.set_mode(self.config.rotary_0_pins[0], pigpio.INPUT)  # BCM4
            self.GPIO.set_pull_up_down(self.config.rotary_0_pins[0], pigpio.PUD_OFF)
            # switch 3 ENCODER SPEED 1
            self.GPIO.set_mode(self.config.rotary_0_pins[1], pigpio.INPUT)  # BCM14
            self.GPIO.set_pull_up_down(self.config.rotary_0_pins[1], pigpio.PUD_OFF)

            # switch 4 ENCODER SPEED 2
            self.GPIO.set_mode(self.config.rotary_1_pins[0], pigpio.INPUT)  # BMC15
            self.GPIO.set_pull_up_down(self.config.rotary_1_pins[0], pigpio.PUD_OFF)
            # switch 4 ENCODER SPEED 2
            self.GPIO.set_mode(self.config.rotary_1_pins[1], pigpio.INPUT)  # BMC22
            self.GPIO.set_pull_up_down(self.config.rotary_1_pins[1], pigpio.PUD_OFF)

            # switch 5 PRIMARY GAIN
            self.GPIO.set_mode(self.config.rotary_2_pins[0], pigpio.INPUT)  # BCM23
            self.GPIO.set_pull_up_down(self.config.rotary_2_pins[0], pigpio.PUD_OFF)
            # switch 5 PRIMARY GAIN
            self.GPIO.set_mode(self.config.rotary_2_pins[1], pigpio.INPUT)  # BCM24
            self.GPIO.set_pull_up_down(self.config.rotary_2_pins[1], pigpio.PUD_OFF)

            # switch 6 SECONDARY GAIN
            self.GPIO.set_mode(self.config.rotary_3_pins[0], pigpio.INPUT)  # BCM25
            self.GPIO.set_pull_up_down(self.config.rotary_3_pins[0], pigpio.PUD_OFF)
            # switch 6 SECONDARY GAIN
            self.GPIO.set_mode(self.config.rotary_3_pins[1], pigpio.INPUT)  # BCM12
            self.GPIO.set_pull_up_down(self.config.rotary_3_pins[1], pigpio.PUD_OFF)
        except Exception as err:
            self.log.exception('Error in gpio setup {}'.format(err.args))

    def enable_callbacks(self):
        try:
            # SW3-B ENCODER SPEED 1
            self.rotary_0_0_callback = self.GPIO.callback(self.config.rotary_0_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_0_pin_0)
            self.rotary_0_1_callback = self.GPIO.callback(self.config.rotary_0_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_0_pin_1)
            self.GPIO.set_glitch_filter(self.config.rotary_0_pins[0],
                                        self.config.rotary_0_pin_0_debounce)  # microseconds
            self.GPIO.set_glitch_filter(self.config.rotary_0_pins[1],
                                        self.config.rotary_0_pin_1_debounce)  # microseconds

            # SW4-B ENCODER SPEED 2
            self.rotary_1_0_callback = self.GPIO.callback(self.config.rotary_1_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_1_pin_0)
            self.rotary_1_1_callback = self.GPIO.callback(self.config.rotary_1_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_1_pin_1)
            self.GPIO.set_glitch_filter(self.config.rotary_1_pins[0],
                                        self.config.rotary_1_pin_0_debounce)  # microseconds
            self.GPIO.set_glitch_filter(self.config.rotary_1_pins[1],
                                        self.config.rotary_1_pin_1_debounce)  # microseconds

            # SW5-B PRIMARY CARRIER GAIN
            self.rotary_2_0_callback = self.GPIO.callback(self.config.rotary_2_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_2_pin_0)
            self.rotary_2_1_callback = self.GPIO.callback(self.config.rotary_2_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_2_pin_1)
            self.GPIO.set_glitch_filter(self.config.rotary_2_pins[0],
                                        self.config.rotary_2_pin_0_debounce)  # microseconds
            self.GPIO.set_glitch_filter(self.config.rotary_2_pins[1],
                                        self.config.rotary_2_pin_1_debounce)  # microseconds

            # SW6-B SECONDARY CARRIER GAIN
            self.rotary_3_0_callback = self.GPIO.callback(self.config.rotary_3_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_3_pin_0)
            self.rotary_3_1_callback = self.GPIO.callback(self.config.rotary_3_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_3_pin_1)
            self.GPIO.set_glitch_filter(self.config.rotary_3_pins[0],
                                        self.config.rotary_3_pin_0_debounce)  # microseconds
            self.GPIO.set_glitch_filter(self.config.rotary_3_pins[1],
                                        self.config.rotary_3_pin_1_debounce)  # microseconds

            self.interrupts_enabled = True
        except AttributeError:
            self.log.exception("Error setting up gpio callbacks", exc_info=True)

    def disable_interrupts(self):
        # SW3-B ENCODER SPEED 1
        self.rotary_0_0_callback.cancel()
        self.rotary_0_1_callback.cancel()

        # SW4-B ENCODER SPEED 2
        self.rotary_1_0_callback.cancel()
        self.rotary_1_1_callback.cancel()

        # SW5-B PRIMARY CARRIER GAIN
        self.rotary_2_0_callback.cancel()
        self.rotary_2_1_callback.cancel()

        # SW6-B SECONDARY CARRIER GAIN
        self.rotary_3_0_callback.cancel()
        self.rotary_3_1_callback.cancel()

    def rotary_interrupts(self, value):
        if value is False:
            self.log.debug('Disabling rotary interrupts')
            self.disable_interrupts()
        elif value is True:
            self.log.debug('Enabling rotary interrupts')
            self.enable_interrupts()

    def speed_signal_changed(self, cs, speed, direction):
        self.log.debug(
            'Speed value changed - Received Speed:{}  Direction:{}  CS:{}'.format(speed, direction, cs))
        self.speedgenerator.set_speed_signal(self.speedgenerator.SPEED_0_CS, speed, direction)

    def digital_pot_value_changed(self, speed, direction, pot):
        self.log.debug(
            'Digital pot value changed - Received Speed:{}  Direction:{}  Pot:{}'.format(speed, direction, pot))
        # self.digitalpots.value_change(speed, direction, pot, value=None)
        pass

    def get_speed(self, delta):
        if delta < self.config.speed_threshold:  # threshold for fast rotation xx ms between interrupts
            speed = Rotary.SPEED_FAST
            speed_text = 'FAST'
        else:
            speed = Rotary.SPEED_SLOW
            speed_text = 'SLOW'
        self.log.debug(
            'Speed:{}  Time:{}  Threshold:{} seconds'.format(speed_text, delta, self.config.speed_threshold))
        return speed

    def get_direction(self, pins, rotary_number_tmp):
        str_direction = ""
        direction = 0  # zero is the default error value 1=CLOCKWISE -1=anticlockwise
        self.log.debug('Pins:{}  Rotary_num:{}'.format(pins, rotary_number_tmp))
        if pins == [0, 0]:  # determine direction from quadrature input
            Rotary.zone[rotary_number_tmp] = 0
            if Rotary.prevZone[rotary_number_tmp] == 1:  # done
                direction = Rotary.CLOCKWISE
            elif Rotary.prevZone[rotary_number_tmp] == 2:  # done
                direction = Rotary.ANTI_CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        elif pins == [0, 1]:
            Rotary.zone[rotary_number_tmp] = 1
            if Rotary.prevZone[rotary_number_tmp] == 3:  # done
                direction = Rotary.CLOCKWISE
            elif Rotary.prevZone[rotary_number_tmp] == 0:  # done
                direction = Rotary.ANTI_CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        elif pins == [1, 0]:
            Rotary.zone[rotary_number_tmp] = 2
            if Rotary.prevZone[rotary_number_tmp] == 0:  # done
                direction = Rotary.CLOCKWISE
            elif Rotary.prevZone[rotary_number_tmp] == 3:  # done
                direction = Rotary.ANTI_CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        elif pins == [1, 1]:
            Rotary.zone[rotary_number_tmp] = 3
            if Rotary.prevZone[rotary_number_tmp] == 1:  # done
                direction = Rotary.ANTI_CLOCKWISE
            elif Rotary.prevZone[rotary_number_tmp] == 2:  # done
                direction = Rotary.CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        if direction == Rotary.CLOCKWISE:
            str_direction = "CLOCKWISE"
        elif direction == Rotary.ANTI_CLOCKWISE:
            str_direction = "ANTICLOCKWISE"
        elif direction == 0:
            str_direction = "ERROR"
        self.log.debug('ZONE:{}    PREVZONE:{}   DIRECTION:{}'.format(Rotary.zone[rotary_number_tmp],
                                                                      Rotary.prevZone[rotary_number_tmp], str_direction))
        Rotary.prevZone[rotary_number_tmp] = Rotary.zone[rotary_number_tmp]
        return direction

        # ENCODER SPEED 1				BCM4

    def rotary_0_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 1 Rotary 0 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        self.log.debug("Interrupt Time : {}".format(interrupt_time))
        delta = interrupt_time - Rotary.last_interrupt_time_rotary0_pin0
        if simulate:
            pins = sim_pins
            self.log.debug('self.simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_0_pins[0]), self.GPIO.read(self.config.rotary_0_pins[1])]
            self.log.debug("Pin read time {}".format(time.time()))
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_0_pins[0], pins[0],
                                                               self.config.rotary_0_pins[1],
                                                               pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[0])
        speed = self.get_speed(delta)
        self.speed_signal_changed(self.speedgenerator.SPEED_0_CS, speed, direction)
        Rotary.last_interrupt_time_rotary0_pin0 = interrupt_time

        # ENCODER SPEED 1				BCM14

    def rotary_0_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 1 Rotary 1 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        self.log.debug("Interrupt Time : {}".format(interrupt_time))
        delta = interrupt_time - Rotary.last_interrupt_time_rotary0_pin1
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated Interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_0_pins[0]), self.GPIO.read(self.config.rotary_0_pins[1])]
            self.log.debug("Pin read time {}".format(time.time()))
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_0_pins[0], pins[0],
                                                               self.config.rotary_0_pins[1],
                                                               pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[0])
        speed = self.get_speed(delta)
        self.speed_signal_changed(self.speedgenerator.SPEED_0_CS, speed, direction)
        Rotary.last_interrupt_time_rotary0_pin1 = interrupt_time

        # ENCODER SPEED 2				BMC15

    def rotary_1_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 2 Rotary 1 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary1_pin0
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_1_pins[0]), self.GPIO.read(self.config.rotary_1_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_1_pins[0], pins[0],
                                                               self.config.rotary_1_pins[1],
                                                               pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[1])
        speed = self.get_speed(delta)
        self.speed_signal_changed(self.speedgenerator.SPEED_1_CS, speed, direction)
        Rotary.last_interrupt_time_rotary1_pin0 = interrupt_time

        # ENCODER SPEED 2				BMC22

    def rotary_1_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 2 Rotary 1 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary1_pin1
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_1_pins[0]), self.GPIO.read(self.config.rotary_1_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_1_pins[0], pins[0],
                                                               self.config.rotary_1_pins[1],
                                                               pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[1])
        speed = self.get_speed(delta)
        self.speed_signal_changed(self.speedgenerator.SPEED_1_CS, speed, direction)
        Rotary.last_interrupt_time_rotary1_pin1 = interrupt_time

        # ENCODER PRIMARY GAIN			BMC23

    def rotary_2_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 2 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary2_pin0
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_2_pins[0]), self.GPIO.read(self.config.rotary_2_pins[1])]
        self.log.debug(
            "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_2_pins[0], pins[0],
                                                           self.config.rotary_2_pins[1],
                                                           pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[2])
        speed = self.get_speed(delta)
        self.digital_pot_value_changed(speed, direction, 0)
        Rotary.last_interrupt_time_rotary2_pin0 = interrupt_time

        # ENCODER PRIMARY GAIN			BCM24

    def rotary_2_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 2 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary2_pin1
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_2_pins[0]), self.GPIO.read(self.config.rotary_2_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_2_pins[0], pins[0],
                                                               self.config.rotary_2_pins[1],
                                                               pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[2])
        speed = self.get_speed(delta)
        self.digital_pot_value_changed(speed, direction, 0)
        Rotary.last_interrupt_time_rotary2_pin1 = interrupt_time

        # ENCODER SECONDARY GAIN			BCM25

    def rotary_3_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 3 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary3_pin0
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_3_pins[0]), self.GPIO.read(self.config.rotary_3_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_3_pins[0], pins[0],
                                                               self.config.rotary_3_pins[1],
                                                               pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[3])
        speed = self.get_speed(delta)
        self.digital_pot_value_changed(speed, direction, 1)
        Rotary.last_interrupt_time_rotary3_pin0 = interrupt_time

        # ENCODER SECONDARY GAIN			BCM12

    def rotary_3_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 3 PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollingpermission.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary3_pin1
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.GPIO.read(self.config.rotary_3_pins[0]), self.GPIO.read(self.config.rotary_3_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_3_pins[0], pins[0],
                                                               self.config.rotary_3_pins[1],
                                                               pins[1]))
        direction = self.get_direction(pins, Rotary.rotary_num[3])
        speed = self.get_speed(delta)
        self.digital_pot_value_changed(speed, direction, 1)
        Rotary.last_interrupt_time_rotary3_pin1 = interrupt_time


