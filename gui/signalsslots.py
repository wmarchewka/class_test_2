import logging

class Signalslots(object):
    def __init__(self, logger):
        self.logger = logger
        self.log = self.logger
        self.log = logging.getLogger(__name__)
        self.log.debug("{} init complete...".format(__name__))

    def signal_and_slots(self, window, gui):
        window.buttonGroup.buttonClicked['int'].connect(gui.gpio_button_clicked)  # gpio buttons catch press
        window.tabWidget.currentChanged.connect(gui.tabwidget_changed)  # tabwidget get tab change event
        window.TBL_cal_values.cellClicked.connect(gui.cal_values_cell_clicked)

        # primary and secondary gain encoders value change
        window.QDIAL_primary_gain.valueChanged.connect(gui.primary_gain_change)
        window.QDIAL_secondary_gain.valueChanged.connect(gui.secondary_gain_change)

        # speed 1 and speed2 value change
        window.QDIAL_speed_1.valueChanged.connect(gui.speed_1_change)
        window.QDIAL_speed_2.valueChanged.connect(gui.speed_2_change)

        # TIMER ON OFF BUTTONS
        window.PB_display_timer_toggle.clicked.connect(gui.display_timer_toggled)  # PB to turn timers on and off
        window.PB_poll_timer_toggle.clicked.connect(gui.poll_timer_toggled)  # PB to turn timers on and off

        # NOT CURRENTLY IMPLEMENT BUT LEFT IN
        window.PB_coderate_selector_down.clicked.connect(
            lambda: window.code_rate_selector_change("DOWN"))  # coderate selector buttons
        window.PB_coderate_selector_up.clicked.connect(lambda: gui.code_rate_selector_change("UP"))

        # CATChES ADC SCALE BUTTON, THIS WILL BE REMOVED
        window.SPIN_adc_scale.valueChanged.connect(gui.adc_scale_change)

        # set brightness value
        window.SPIN_brightness.valueChanged.connect(gui.brightness_changed)

        # shutdown button
        window.PB_close.clicked.connect(gui.shutdown)

        # eeprom buttons
        window.PB_read_all_from_eeprom.clicked.connect(gui.eeprom_read_all)  # eeprom functions
        window.PB_write_all_to_eeprom.clicked.connect(gui.eeprom_write_all)
        window.PB_eeprom_write.clicked.connect(gui.eeprom_write)
        window.PB_eeprom_read.clicked.connect(gui.eeprom_read)
        window.PB_spi_log_clear.clicked.connect(gui.spi_log_clear)

        # BUTTONS TO CHHANGE SHAPE OF SPEED OUTPUTS
        window.BUTTON_speed1_sine.toggled.connect(
            lambda: window.speed1_buttonstate_change(gui.BUTTON_speed1_sine))
        window.BUTTON_speed1_square.toggled.connect(
            lambda: window.speed1_buttonstate_change(gui.BUTTON_speed1_square))
        window.BUTTON_speed1_triangle.toggled.connect(
            lambda: window.speed1_buttonstate_change(gui.BUTTON_speed1_triangle))
        window.BUTTON_speed2_sine.toggled.connect(
            lambda: window.speed2_buttonstate_change(gui.BUTTON_speed2_sine))
        window.BUTTON_speed2_square.toggled.connect(
            lambda: window.speed2_buttonstate_change(gui.BUTTON_speed2_square))
        window.BUTTON_speed2_triangle.toggled.connect(
            lambda: window.speed2_buttonstate_change(gui.BUTTON_speed2_triangle))

        # MANUAL GPIO AND CS TOGGLING
        window.PB_gpio_manual_toggle.clicked.connect(gui.gpio_manual_toggled)
        window.PB_chip_select_manual_toggle.clicked.connect(gui.manual_chip_select_toggled)

        # ******************************************************************************
        # testing functions may not included in final
        window.SPIN_primary_gain_percent.valueChanged.connect(gui.primary_gain_set_percent)
        window.SPIN_secondary_gain_percent.valueChanged.connect(gui.secondary_gain_set_percent)
        window.SPIN_primary_gain_ohms.valueChanged.connect(gui.primary_gain_set_ohms)
        window.SPIN_secondary_gain_ohms.valueChanged.connect(gui.secondary_gain_set_ohms)
        window.SPIN_primary_frequency.valueChanged.connect(gui.set_frequencies)
        window.SPIN_secondary_frequency.valueChanged.connect(gui.set_frequencies)
        window.PB_frequencies_toggle.clicked.connect(gui.frequencies_toggle)
        window.PB_popup_test.clicked.connect(gui.popup_test)
        window.PB_graph_left.clicked.connect(gui.graph_increase)
        window.PB_graph_right.clicked.connect(gui.graph_decrease)
        window.PB_store_in_nvram.clicked.connect(gui.digitalpots.wiper_to_nvram)
        window.PB_nvram_to_wiper.clicked.connect(gui.digitalpots.nvram_to_wiper)
        window.PB_primary_gain_value.clicked.connect(gui.primary_gain_value_test)
