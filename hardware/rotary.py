import logging


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

    def __init__(self, pollingpermission, gpio):

        self.init = True
        self.log = logging.getLogger(__name__)
        self.log.debug("gpio {}".format(gpio))
        self.pollingpermission = pollingpermission
        self.log.debug(" MRO  {}".format(self.__class__.__mro__))
        self.log.debug("{} init complete...".format(__name__))

