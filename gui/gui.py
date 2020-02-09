import signal
import sys
import logging
import subprocess

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer, QFile, QObject
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QTableWidgetItem


class Mainwindow(QObject):

    display_brightness = None
    guiname = None
    poll_timer_interval = None
    local_timer_interval = None
    sense_timer_interval = None
    switch_timer_interval = None
    screen_brightness_max = None
    screen_brightness_min = None


    def __init__(self, commander, config):
        super().__init__()
        self.commander = commander
        self.config = config
        self.logger = commander.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.config_file_load()
        self.loadscreen()
        self.signal_and_slots()
        self.exit_signalling()
        self.log.debug("{} init complete...".format(__name__))


    def startup_processes(self):
        self.log.info('Waking screen...')
        subprocess.call('xset dpms force on', shell=True)  # WAKE SCREEN
        self.set_security_level()  # SET SECURITY LEVEL
        self.pollingpermission.polling_prohibited = (False, self.__module__)
        self.coderategenerator.coderate_stop()
        self.comm_server_start()
        self.eeprom_read_data()
        self.ip_address_query()
        self.index_tab_pages()
        self.set_frequencies(self)  # send frequency values to frequency generators

    def config_file_load(self):
        Mainwindow.display_brightness = self.config.display_brightness
        Mainwindow.guiname = self.config.guiname
        Mainwindow.poll_timer_interval = self.config.poll_timer_interval
        Mainwindow.local_timer_interval = self.config.local_timer_interval
        Mainwindow.sense_timer_interval = self.config.sense_timer_interval
        Mainwindow.switch_timer_interval = self.config.switch_timer_interval
        Mainwindow.screen_brightness_max = self.config.screen_brightness_max
        Mainwindow.screen_brightness_min = self.config.screen_brightness_min

    def exit_signalling(self):
        signal.signal(signal.SIGINT, self.exit_application)
        signal.signal(signal.SIGTERM, self.exit_application)

    def loadscreen(self):
        try:
            ui_file = QFile(Mainwindow.guiname)
            ui_file.open(QFile.ReadOnly)

            loader = QUiLoader()
            self.window = loader.load(ui_file)
            ui_file.close()

            self.window.show()
            self.log.debug('Loading screen ' + self.guiname)

        except FileNotFoundError:
            self.log.debug("Could not find {}".format(self.guiname))  # CATCHES EXIT SHUTDOWN

    def signal_and_slots(self):

        self.window.buttonGroup.buttonClicked['int'].connect(self.gpio_button_clicked)  # gpio buttons catch press
        self.window.tabWidget.currentChanged.connect(self.tabwidget_changed)  # tabwidget get tab change event
        self.window.TBL_cal_values.cellClicked.connect(self.cal_values_cell_clicked)

        # primary and secondary gain encoders value change
        self.window.QDIAL_primary_gain.valueChanged.connect(self.primary_gain_change)
        self.window.QDIAL_secondary_gain.valueChanged.connect(self.secondary_gain_change)

        # speed 1 and speed2 value change
        self.window.QDIAL_speed_1.valueChanged.connect(self.speed_1_change)
        self.window.QDIAL_speed_2.valueChanged.connect(self.speed_2_change)

        # TIMER ON OFF BUTTONS
        self.window.PB_display_timer_toggle.clicked.connect(self.display_timer_toggled)  # PB to turn timers on and off
        self.window.PB_poll_timer_toggle.clicked.connect(self.poll_timer_toggled)  # PB to turn timers on and off

        # NOT CURRENTLY IMPLEMENT BUT LEFT IN
        self.window.PB_coderate_selector_down.clicked.connect(
            lambda: self.code_rate_selector_change("DOWN"))  # coderate selector buttons
        self.window.PB_coderate_selector_up.clicked.connect(lambda: self.code_rate_selector_change("UP"))

        # CATChES ADC SCALE BUTTON, THIS WILL BE REMOVED
        self.window.SPIN_adc_scale.valueChanged.connect(self.adc_scale_change)

        # set brightness value
        self.window.SPIN_brightness.valueChanged.connect(self.brightness_changed)

        # shutdown button
        self.window.PB_close.clicked.connect(self.shutdown)

        # eeprom buttons
        self.window.PB_read_all_from_eeprom.clicked.connect(self.eeprom_read_all)  # eeprom functions
        self.window.PB_write_all_to_eeprom.clicked.connect(self.eeprom_write_all)
        self.window.PB_eeprom_write.clicked.connect(self.eeprom_write)
        self.window.PB_eeprom_read.clicked.connect(self.eeprom_read)
        self.window.PB_spi_log_clear.clicked.connect(self.spi_log_clear)

        # BUTTONS TO CHHANGE SHAPE OF SPEED OUTPUTS
        self.window.BUTTON_speed1_sine.toggled.connect(
            lambda: self.speed1_buttonstate_change(self.window.BUTTON_speed1_sine))
        self.window.BUTTON_speed1_square.toggled.connect(
            lambda: self.speed1_buttonstate_change(self.window.BUTTON_speed1_square))
        self.window.BUTTON_speed1_triangle.toggled.connect(
            lambda: self.speed1_buttonstate_change(self.window.BUTTON_speed1_triangle))
        self.window.BUTTON_speed2_sine.toggled.connect(
            lambda: self.speed2_buttonstate_change(self.window.BUTTON_speed2_sine))
        self.window.BUTTON_speed2_square.toggled.connect(
            lambda: self.speed2_buttonstate_change(self.window.BUTTON_speed2_square))
        self.window.BUTTON_speed2_triangle.toggled.connect(
            lambda: self.speed2_buttonstate_change(self.window.BUTTON_speed2_triangle))

        # MANUAL GPIO AND CS TOGGLING
        self.window.PB_gpio_manual_toggle.clicked.connect(self.gpio_manual_toggled)
        self.window.PB_chip_select_manual_toggle.clicked.connect(self.manual_chip_select_toggled)

        # ******************************************************************************
        # testing functions may not included in final
        self.window.SPIN_primary_gain_percent.valueChanged.connect(self.primary_gain_set_percent)
        self.window.SPIN_secondary_gain_percent.valueChanged.connect(self.secondary_gain_set_percent)
        self.window.SPIN_primary_gain_ohms.valueChanged.connect(self.primary_gain_set_ohms)
        self.window.SPIN_secondary_gain_ohms.valueChanged.connect(self.secondary_gain_set_ohms)
        self.window.SPIN_primary_frequency.valueChanged.connect(self.set_frequencies)
        self.window.SPIN_secondary_frequency.valueChanged.connect(self.set_frequencies)
        self.window.PB_frequencies_toggle.clicked.connect(self.frequencies_toggle)
        self.window.PB_popup_test.clicked.connect(self.popup_test)
        self.window.PB_graph_left.clicked.connect(self.graph_increase)
        self.window.PB_graph_right.clicked.connect(self.graph_decrease)
        self.window.PB_store_in_nvram.clicked.connect(self.digitalpots.wiper_to_nvram)
        self.window.PB_nvram_to_wiper.clicked.connect(self.digitalpots.nvram_to_wiper)
        self.window.PB_primary_gain_value.clicked.connect(self.primary_gain_value_test)
    def exit_application(self, signum, frame):
        self.log.debug("Starting shutdown")
        self.log.debug("Received signal from signum: {} with frame:{}".format(signum, frame))
        sys.exit(0)
