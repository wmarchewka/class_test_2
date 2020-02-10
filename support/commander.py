import logging
from PySide2 import QtCore


class Commander(object):

    poll_timer_interval = 1000
    sense_callback_loop_counter = 0
    ADC_SCALE = 10.38
    adc_average = 0
    final_adc_value = 0
    display_amps = 0

    def __new__(cls, config, pollvalues, gui):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
            ("Creating new class {}".format(cls.instance))
        else:
            print("Creating instance class {}".format(cls.instance))
        return cls.instance

    def __init__(self, config, pollvalues, gui):
        self.init = True
        self.pollvalues = pollvalues
        self.switches = self.pollvalues.switches
        self.gui = gui
        self.config = config
        self.logger = self.config.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))


    # *********************************************************************************
    def startup_processes(self):
        self.read_config_file()
        self.timer_init()
        self.timer_start()
        self.window = self.gui.window

    # *********************************************************************************
    def parsescreen(self, value):
        self.log.debug("Commander received value {}".format(value))

    # *********************************************************************************
    def timer_init(self):
        # local timer updates GUI and others
        self.poll_timer = QtCore.QTimer()
        self.poll_timer.setObjectName("POLL TIMER")
        self.poll_timer.timeout.connect(self.pollvalues.poll_read_values)
        self.pollvalues.poll_changedValue.connect(self.poll_callback_change_value)

    # *********************************************************************************
    def timer_start(self):
        self.poll_timer.start(Commander.poll_timer_interval)

    # *********************************************************************************
    def read_config_file(self):
        Commander.poll_timer_interval = self.config.poll_timer_interval

    # ************************************************************************************
    def poll_callback_change_value(self, counts, analog_digital_value, scaled_value, switch_value):
        self.sense_callback_change_value(counts, analog_digital_value, scaled_value)
        self.switches_callback_change_value(switch_value)

   # ************************************************************************************
   # call back from current_sense poll
    def sense_callback_change_value(self, counts, analog_digital_value, scaled_value):
        self.log.debug('GUI received sense values...')
        self.log.debug(
            'SENSE CALLBACK SCALED VALUE:  {}    ANALOG VALUE  {}  :'.format(scaled_value, analog_digital_value))
        self.log.debug("A/D value: {} ({}V  {} counts)".format(analog_digital_value, scaled_value, counts))
        Commander.sense_callback_loop_counter = Commander.sense_callback_loop_counter + 1
        if Commander.sense_callback_loop_counter == 10:
            Commander.adc_average = Commander.adc_average / (Commander.sense_callback_loop_counter - 1)
            Commander.adc_average = Commander.adc_average * 1000
            Commander.final_adc_value = Commander.adc_average
            Commander.display_amps = (Commander.ADC_SCALE * Commander.final_adc_value)
            self.window.LBL_display_adc.setText("{:4.2f}".format(Commander.adc_average))
            Commander.display_amps = Commander.display_amps / 1000
            self.window.LBL_display_amps.setText("{:2.3f}".format(Commander.display_amps))
            self.window.LBL_loop_current_1.setText("{:2.3f}".format(Commander.display_amps))
            self.window.LBL_display_adc_counts.setText("{:5.0f}".format(counts))
            Commander.adc_average = 0
            Commander.sense_callback_loop_counter = 0
        else:
            self.adc_average = self.adc_average + analog_digital_value

        # ************************************************************************************
        # call back from switch_polling

    def switches_callback_change_value(self, value):
        self.log.debug("onSwitchChangeValues :{}".format(value))
        if value & 0b00000001:
            self.window.switch3_green.setVisible(True)
            self.window.switch3_red.setVisible(False)
        else:
            self.window.switch3_green.setVisible(False)
            self.window.switch3_red.setVisible(True)
        if value & 0b00000010:
            self.window.switch4_green.setVisible(True)
            self.window.switch4_red.setVisible(False)
        else:
            self.window.switch4_green.setVisible(False)
            self.window.switch4_red.setVisible(True)
        if value & 0b00000100:
            self.window.switch5_green.setVisible(True)
            self.window.switch5_red.setVisible(False)
        else:
            self.window.switch5_green.setVisible(False)
            self.window.switch5_red.setVisible(True)
        if value & 0b00001000:
            self.window.switch6_green.setVisible(True)
            self.window.switch6_red.setVisible(False)
        else:
            self.window.switch6_green.setVisible(False)
            self.window.switch6_red.setVisible(True)

        if self.switches.primary_gain_pb_status == "ON":
            self.window.LBL_primary_gain_pb_status.setText("ON")
            self.digitalpots.gains_locked = False
            self.window.LBL_frequency_selected.setText("SEC")
        if self.switches.primary_gain_pb_status == "OFF":
            self.window.LBL_primary_gain_pb_status.setText("OFF")
            self.digitalpots.gains_locked = False
        if self.switches.primary_gain_pb_status == "CODERATE":
            self.window.LBL_primary_gain_pb_status.setText("CODERATE")
            self.digitalpots.gains_locked = False
        if self.switches.primary_gain_pb_status == "LOCKED":
            self.window.LBL_primary_gain_pb_status.setText("LOCKED")
            self.digitalpots.gains_locked = True
        self.primary_gain_pb_status = "NONE"

        if self.switches.secondary_gain_pb_status == "ON":
            self.window.LBL_secondary_gain_pb_status.setText("ON")
        if self.switches.secondary_gain_pb_status == "OFF":
            self.window.LBL_secondary_gain_pb_status.setText("OFF")
        if self.switches.secondary_gain_pb_status == "CODERATE":
            self.window.LBL_secondary_gain_pb_status.setText("CODERATE")
        if self.switches.secondary_gain_pb_status == "LOCKED":
            self.window.LBL_secondary_gain_pb_status.setText("LOCKED")
        self.secondary_gain_pb_status = "NONE"

        # # self.lcd_switches.display(switch_value)
        # self.thread_info()

