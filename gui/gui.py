import faulthandler
faulthandler.enable()
import datetime
import logging
import os
import signal
import socket
import subprocess
import sys
import threading
#import psutil
import numpy as np
from numpy import sin, pi

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QFile, QObject
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QTableWidgetItem
from communication.communication import ThreadedTCPRequestHandler, ThreadedTCPServer
from gui.signalsslots import Signalslots as signalslots

class Mainwindow(QObject):

    display_brightness = None
    guiname = None
    poll_timer_interval = None
    local_timer_interval = None
    sense_timer_interval = None
    switch_timer_interval = None
    screen_brightness_max = None
    screen_brightness_min = None


    def __init__(self, commander, config, digitalpots, securitylevel):
        super(Mainwindow, self).__init__()
        self.window = None
        self.commander = commander
        self.config = config
        self.digitalpots = digitalpots
        self.securitylevel = securitylevel
        self.logger = commander.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.signalslots = signalslots()
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))


    def startup_processes(self):
        self.config_file_load()
        self.loadscreen()
        self.signalslots.signal_and_slots(self.window, self)
        self.exit_signalling()
        self.log.info('Waking screen...')
        subprocess.call('xset dpms force on', shell=True)  # WAKE SCREEN
        #self.pollingpermission.polling_prohibited = (False, self.__module__)
        #self.comm_server_start()
        #self.eeprom_read_data()
        #self.ip_address_query()
        self.securitylevel.index_tab_pages(self.window)
        self.securitylevel.set_security_level("technician", self.window)  # SET SECURITY LEVEL
        #self.set_frequencies(self)  # send frequency values to frequency generators
        self.timers()

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

    # ******************************************************************************

    def timers(self):
        # local timer updates GUI and others
        self.poll_timer = QtCore.QTimer()
        self.poll_timer.setObjectName("POLL TIMER")
        self.poll_timer.timeout.connect(self.pollvalues.poll_read_values)
        self.pollvalues.poll_changedValue.connect(self.poll_callback_change_value)
        # self.poll_timer.start(self.sense_timer_interval)

        # ******************************************************************************
        # local timer updates GUI and others
        self.local_timer = QtCore.QTimer()
        self.local_timer.setObjectName("LOCAL TIMER")
        self.local_timer.timeout.connect(self.display_update)
        # self.local_timer.start(self.local_timer_interval)

        # ******************************************************************************
        # sense update timer sets rate of update from SENSE A/D converter
        self.sense_timer = QtCore.QTimer()
        self.sense_timer.timeout.connect(self.pollvalues.sense_read_values)
        self.pollvalues.sense_changedValue.connect(self.sense_callback_change_value)
        # self.sense_timer.start(self.sense_timer_interval)

        # ******************************************************************************
        # switch update timer sets rate to POLL for switch changes
        self.switch_timer = QtCore.QTimer()
        self.pollvalues.switch_changedValue.connect(self.switches_callback_change_value)
        self.switch_timer.timeout.connect(self.switches_run)
        # self.switch_timer.start(self.switch_timer_interval)

        # ******************************************************************************
        # used for internal functions
        self.internal_timer = QtCore.QTimer()
        self.internal_timer.timeout.connect(self.internal_timer_timeout)
        self.internal_timer.start(100)

        # ******************************************************************************
        # used for testing
        self.rotary_test_timer = QtCore.QTimer()
        self.rotary_test_timer.timeout.connect(self.rotary_test)
        # self.rotary_test_timer.start(20)

    # *******************************************************************************
    def gpio_manual_toggled(self, value):
        gpio_pin = self.SPIN_gpio_manual_select.value()
        try:
            if value:
                self.gpio.GPIO.write(gpio_pin, True)
                self.log.info("Setting GPIO {} to TRUE".format(gpio_pin))
                self.window.PB_gpio_manual_toggle.setText("ON")
            elif not value:
                self.gpio.GPIO.write(gpio_pin, False)
                self.log.info("Setting GPIO {} to FALSE".format(gpio_pin))
                self.window.PB_gpio_manual_toggle.setText("OFF")
        except Exception:
            self.log.info("GPIO ERROR")
            self.window.PB_gpio_manual_toggle.setText("ERR")

        #  ***************************************************************************************

    def speed1_buttonstate_change(self, button):
        self.log.info(button.text())
        if button.text() == "SINE":
            self.speed_generator.freq_shape[0] = 0
        if button.text() == "SQUARE":
            self.speed_generator.freq_shape[0] = 1
        if button.text() == "TRIANGLE":
            self.speed_generator.freq_shape[0] = 2

        #  ***************************************************************************************

    def speed2_buttonstate_change(self, button):
        self.log.info(button.text())
        if button.text() == "SINE":
            self.speed_generator.freq_shape[1] = 0
        if button.text() == "SQUARE":
            self.speed_generator.freq_shape[1] = 1
        if button.text() == "TRIANGLE":
            self.speed_generator.freq_shape[1] = 2

        #  ***************************************************************************************

    def adc_scale_change(self, value):
        self.adc_scale = value

        #  ***************************************************************************************

    def cal_values_cell_clicked(self, row, column):
        self.log.info("Cell clicked  ROW:{}  COLUMN:{}  ".format(row, column))
        self.cal_values[row] = self.final_adc_value
        scale_value = 0
        ad_value_str = "{:4.4f}".format(self.final_adc_value)
        if row > 0:
            delta_value = self.cal_values[row] - self.cal_values[row - 1]
            delta_value_str = "{:4.4f}".format(delta_value)
            item_delta_value = QTableWidgetItem()
            item_scale_value = QTableWidgetItem()
            item_delta_value.setText(delta_value_str)
            self.cal_deltas[row] = delta_value
            self.cal_scaled[row] = scale_value
            self.window.TBL_cal_values.setItem(row, 1, item_delta_value)
            # scale_value = 1 / self.final_adc_value
            # scale_value_str = "{:4.4f}".format(scale_value)
            # item_scale_value.setText(scale_value_str)
            # self.TBL_cal_values.setItem(row, 2, item_scale_value)

        label = self.cal_value_header_labels[row]
        self.log.info("Saved A/D Value :{:4.4}  to CAL VALUE:{}".format(ad_value_str, label))
        item_ad_value = QTableWidgetItem()
        item_ad_value.setText(ad_value_str)
        self.window.TBL_cal_values.setItem(row, column, item_ad_value)
        self.cal_average = sum(self.cal_deltas[1:10]) / (len(self.cal_deltas) - 1)
        self.window.LBL_cal_average.setText("{:4.4f}".format(self.window.cal_average))
        self.log.info("AVERAGE:{} ".format(self.cal_average))
        self.calibration_complete = True
        self.window.LBL_cal_complete.setText("CALIBRATION COMPLETE")
        for z in self.window.cal_values:
            if z is None:
                self.calibration_complete = False
                self.window.LBL_cal_complete.setText("CALIBRATION NOT COMPLETE")

        #  ***************************************************************************************

    def table_setup(self):
        self.window.TBL_cal_values.setRowCount(20)
        self.window.TBL_cal_values.setColumnCount(3)
        self.window.TBL_cal_values.setColumnWidth(0, 100)
        self.window.TBL_cal_values.setHorizontalHeaderLabels(['Measured', 'DELTA', 'SCALE'])
        self.window.TBL_cal_values.setVerticalHeaderLabels(self.cal_value_header_labels)
        # icon2 = QtGui.QIcon()
        # item = QTableWidgetItem()
        # icon2.addPixmap(QtGui.QPixmap(':/ICONS/ICONS/up 64 x 64.png'))
        # item.setIcon(icon2)
        # self.TBL_cal_values.setItem(0, 1, item)
        self.window.LBL_cal_average.setText("{:4.4f}".format(0))

        #  ***************************************************************************************

    def tabwidget_changed(self, index):
        current_tab_name = self.window.tabWidget.tabText(index)
        self.log.debug("TAB CHANGED. TAB PRESSED IS: {}   NAME:{}".format(index, current_tab_name))
        self.window.tabWidget.setCurrentIndex(index)

        #  ***************************************************************************************

    def generate_frequency_pushbuttons(self):

        """
        Turns on pre-created buttons on the screen for frequencies.  The list of buttons to be
        activated come from the coderate generator class.  button presses are caught by the
        frequency_pushbutton_change routine.
        """
        y = 0
        self.log.debug("CODERATES:{}".format(self.code_rate_generator.company_frequencies))
        # TODO figure out how to get this to work converted to Pyside from PyQt5
        for x in self.code_rate_generator.company_frequencies:
            button = getattr(self.window, 'PB_freq_%s' % y)
            button.released.connect(lambda idx=y: self.frequency_pushbutton_change(idx))
            button.setStyleSheet('background-color: red;border-radius:10px')
            button.setText(x)
            button.setVisible(True)
            self.pb_frequencies_state.append(0)
            y = y + 1
        for t in range(y, self.max_frequencies_pb):
            button = getattr(self.window, 'PB_freq_%s' % t)
            button.setVisible(False)
        self.window.LBL_current_pri_carrier.setText("OFF")
        self.window.LBL_current_sec_carrier.setText("OFF")

        #  ***************************************************************************************
        # generates coderate push buttons

    def generate_coderate_pushbuttons(self):
        """
        Turns on pre-created buttons on the screen for codrates.  The list of buttons to be
        activated come from the coderate generator class.  button presses are caught by the
        frequency_pushbutton_change routine.
        """
        y = 0
        self.log.debug("FREQUENCIES:{}".format(self.code_rate_generator.company_coderates))
        # TODO figure out how to get this to work converted to Pyside from PyQt5
        for x in self.code_rate_generator.company_coderates:
            button = getattr(self.window, 'PB_coderate_%s' % y)
            button.released.connect(lambda idx=y: self.coderate_pushbutton_change(idx))
            button.setStyleSheet('background-color: red;border-radius:10px')
            button.setText(x)
            button.setVisible(True)
            self.pb_coderates_state.append(0)
            y = y + 1
        for t in range(y, self.max_coderates_pb):
            button = getattr(self.window, 'PB_coderate_%s' % t)
            button.setVisible(False)
        self.window.LBL_current_coderate.setText("OFF")

        #  ***************************************************************************************

    def coderate_pushbutton_change(self, buttonid):
        button = getattr(self.window, 'PB_coderate_%s' % buttonid)
        self.log.debug("CODERATE PB changed BUTTON:{}".format(buttonid))
        if self.pb_coderates_state[buttonid] == 1:
            self.pb_coderates_state[buttonid] = 0
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "FALSE"))
            # button.setStyleSheet('background-color: red;border-radius:10px')
        elif self.pb_coderates_state[buttonid] == 0:
            self.pb_coderates_state[buttonid] = 1
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "TRUE"))
            # button.setStyleSheet('background-color: green;border-radius:10px')
        if self.coderate_pb is None:
            button.setStyleSheet('background-color: green;border-radius:10px')
            self.window.LBL_current_coderate.setText(self.code_rate_generator.company_coderates[buttonid])
            self.coderate_value = self.code_rate_generator.company_coderates[buttonid]
            self.coderate_pb = buttonid
        elif self.coderate_pb is not None:
            if buttonid is self.coderate_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.window.LBL_current_coderate.setText("OFF")
                self.coderate_value = 1
                self.coderate_pb = None
            elif buttonid is not self.coderate_pb:
                last_button = getattr(self, 'PB_coderate_%s' % self.coderate_pb)
                last_button.setStyleSheet('background-color: red;border-radius:10px')
                button.setStyleSheet('background-color: green;border-radius:10px')
                self.window.LBL_current_coderate.setText(self.code_rate_generator.company_coderates[buttonid])
                self.coderate_value = self.code_rate_generator.company_coderates[buttonid]
                self.coderate_pb = buttonid
        self.code_rate_generator.coderate_generate([self.coderate_value, self.pri_freq_value,
                                                    self.sec_freq_value])

        #  ***************************************************************************************

    def frequency_pushbutton_change(self, buttonid):
        button = getattr(self.window, 'PB_freq_%s' % buttonid)
        self.log.debug("FREQ PB changed BUTTON:{}".format(buttonid))
        if self.pb_frequencies_state[buttonid] == 1:
            self.pb_frequencies_state[buttonid] = 0
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "FALSE"))
            # button.setStyleSheet('background-color: red;border-radius:10px')
        elif self.pb_frequencies_state[buttonid] == 0:
            self.pb_frequencies_state[buttonid] = 1
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "TRUE"))
            # button.setStyleSheet('background-color: green;border-radius:10px')
        if self.pri_freq_pb is None and self.sec_freq_pb is None:
            button.setStyleSheet('background-color: green;border-radius:10px')
            self.pri_freq_pb = buttonid
            self.window.LBL_current_pri_carrier.setText(self.code_rate_generator.company_frequencies[buttonid])
            self.pri_freq_value = self.code_rate_generator.company_frequencies[buttonid]
        elif self.pri_freq_pb is None and self.sec_freq_pb is not None:
            if buttonid is self.sec_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.sec_freq_pb = None
                self.window.LBL_current_sec_carrier.setText("OFF")
                self.sec_freq_value = 0
            elif buttonid is not self.sec_freq_pb:
                button.setStyleSheet('background-color: green;border-radius:10px')
                self.pri_freq_pb = buttonid
                self.window.LBL_current_pri_carrier.setText(self.code_rate_generator.company_frequencies[buttonid])
                self.pri_freq_value = self.code_rate_generator.company_frequencies[buttonid]
        elif self.pri_freq_pb is not None and self.sec_freq_pb is None:
            if buttonid is self.pri_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.pri_freq_pb = None
                self.window.LBL_current_pri_carrier.setText("OFF")
                self.window.pri_freq_value = 0
            elif buttonid is not self.pri_freq_pb:
                button.setStyleSheet('background-color: yellow;border-radius:10px')
                self.sec_freq_pb = buttonid
                self.window.LBL_current_sec_carrier.setText(self.code_rate_generator.company_frequencies[buttonid])
                self.sec_freq_value = self.code_rate_generator.company_frequencies[buttonid]
        elif self.pri_freq_pb is not None and self.sec_freq_pb is not None:
            if buttonid is self.pri_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.pri_freq_pb = None
                self.window.LBL_current_pri_carrier.setText("OFF")
                self.pri_freq_value = 0
            elif buttonid is self.window.sec_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.sec_freq_pb = None
                self.window.LBL_current_sec_carrier.setText("OFF")
                self.window.sec_freq_value = 0
        elif self.sec_freq_pb is None and self.pri_freq_pb is None:
            pass
        elif self.sec_freq_pb is None and self.pri_freq_pb is not None:
            pass
        elif self.sec_freq_pb is not None and self.pri_freq_pb is None:
            if buttonid is self.sec_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.sec_freq_pb = None
                self.window.LBL_current_sec_carrier.setText("OFF")
                self.sec_freq_value = 0
        elif self.sec_freq_pb is not None and self.pri_freq_pb is not None:
            pass
        self.code_rate_generator.coderate_generate([self.coderate_value, self.pri_freq_value,
                                                    self.sec_freq_value])

        #  ***************************************************************************************

    def primary_gain_value_test(self):
        value = self.SPIN_primary_gain_value.value()
        self.digitalpots.value[0] = value
        self.digitalpots.value_check(0)

        #  ***************************************************************************************

    def ad_start_sampling(self):
        self.ad_pb_start_sampling = False

        #  ***************************************************************************************

    def graph_increase(self):
        self.cycle1 = self.cycle1 + 10

        #  ***************************************************************************************

    def graph_decrease(self):
        self.cycle1 = self.cycle1 - 10

        #  ***************************************************************************************

    def rotary_test(self):
        self.rotary_test_value = self.rotary_test_value - 1
        if self.rotary_test_value < 0:
            self.rotary_test_value = 23
        self.speed_1_change(self.rotary_test_value)

        #  ***************************************************************************************

    def spi_log_clear(self):
        self.spi.spi_log_count = 0
        self.spi.spi_log_data = ""
        self.last_spi_data = ""
        self.window.TE_spi_log.setPlainText(self.spi.spi_log_data)

        # ***************************************************************************************

    def popup_test(self):
        self.popup.display_message("Test")

        # ***************************************************************************************

    def plot(self, val1, val2):
        self.window.graphWidget.setXRange(0, self.cycle1)
        self.window.graphWidget.clear()
        self.window.graphWidget.plot(val1, val2)

        # ***************************************************************************************

    def manual_chip_select_toggled(self, value):
        cs = self.SPIN_chip_select.value()
        if value:
            self.decoder.chip_select(cs)
            self.log.info("Setting manual CS pin {} low".format(cs))
            if cs > 7:
                self.gpio.GPIO.write(18, False)
                self.window.PB_chip_select_manual_toggle.setText("OFF")
            else:
                self.gpio.GPIO.write(16, False)
                self.window.PB_chip_select_manual_toggle.setText("OFF")
        elif not value:
            self.decoder.chip_select(cs)
            self.log.info("Setting manual CS pin {} High".format(cs))
            self.window.PB_chip_select_manual_toggle.setText("ON")
            if cs > 7:
                self.gpio.GPIO.write(18, True)
                self.window.PB_chip_select_manual_toggle.setText("ON")
            else:
                self.gpio.GPIO.write(16, True)
                self.window.PB_chip_select_manual_toggle.setText("ON")

        # ***************************************************************************************

    def internal_timer_timeout(self):
        if self.window.CHK_gpio_manual_auto.isChecked():
            if self.window.gpio_test_toggle:
                self.gpio_manual_toggled(True)
                self.gpio_test_toggle = False
            else:
                self.gpio_manual_toggled(False)
                self.gpio_test_toggle = True
        if self.window.CHK_chip_select_auto.isChecked():
            if self.cs_test_toggle:
                self.manual_chip_select_toggled(True)
                self.cs_test_toggle = False
            else:
                self.manual_chip_select_toggled(False)
                self.cs_test_toggle = True

        gpio_pin = self.window.SPIN_gpio_manual_read_select.value()
        pinstate = self.gpio.GPIO.read(gpio_pin)
        if pinstate == 0:
            self.window.LBL_gpio_manual_read_value.setText("LOW")
        elif pinstate == 1:
            self.window.LBL_gpio_manual_read_value.setText("HIGH")

        # if self.CHK_primary_frequency_auto.isChecked():
        #     self.log.debug("Primary Frequency in AUTO MODE Count: {}".format(self.pri_frq_count[0]))
        #     self.pri_frq_count = self.pri_frq_count - 1
        #     if self.pri_frq_count < 1:
        #         self.pri_frq_count = 20
        #     self.speed_1_change(self.pri_frq_count)
        # if self.CHK_secondary_frequency_auto.isChecked():
        #     self.log.debug("Secondary Frequency in AUTO MODE Count: {}".format(self.sec_freq_count[0]))
        #     self.sec_freq_count = self.sec_freq_count - 1
        #     if self.sec_freq_count < 1:
        #         self.sec_freq_count = 20
        #     self.speed_2_change(self.sec_freq_count)
        # if self.CHK_primary_gain_auto.isChecked():
        #     self.log.debug("Primary GAIN in AUTO MODE Count: {}".format(self.pri_gain_count))
        #     self.pri_gain_count = self.pri_gain_count - 1
        #     if self.pri_gain_count < 1:
        #         self.pri_gain_count = 20
        #     self.primary_gain_change(self.pri_gain_count)
        # if self.CHK_secondary_gain_auto.isChecked():
        #     self.log.debug("Seondary GAIN in AUTO MODE Count: {}".format(self.sec_gain_count))
        #     self.sec_gain_count = self.sec_gain_count - 1
        #     if self.sec_gain_count < 20:
        #         self.sec_gain_count = 20
        #     self.secondary_gain_change(self.sec_gain_count)
        # if self.CHK_gpio_manual_auto.isChecked():
        #     #self.gpio_pin_state = not self.gpio_pin_state
        #     #self.log.debug("gpio Manual in AUTO MODE Count: {}".format(self.gpio_pin_state))
        #     #pin = self.SPIN_gpio_manual_select.value()
        #     #state = self.gpio_pin_state
        #     #self.gpio.GPIO.write(pin, state)
        #     pass
        # if self.CHK_chip_select_auto.isChecked():
        #     self.cs_state = not self.cs_state
        #     cs_st = self.cs_state
        #     self.chip_select_set(cs_st)
        # if self.CHK_eeprom_read_auto.isChecked():
        #     self.eeprom_read()

        # ***************************************************************************************

    def eeprom_write_all(self):
        pass

        # ***************************************************************************************

    def eeprom_read_all(self):
        x = 0
        register_names, eeprom_data = self.eeprom.read_all()
        self.log.debug("EEPROM data {} {}".format(register_names, eeprom_data))
        for register, register_data in zip(register_names, eeprom_data):
            reg = getattr(self, 'LBL_eeprom_%s' % x)
            data = getattr(self, 'LINE_eeprom_%s' % x)
            reg.setText(register)
            data.setText(register_data)
            x = x + 1

        # ***************************************************************************************

    def eeprom_read(self):
        self.log.info("Manual EEPROM Read...")
        register = self.SPIN_eeprom_read_address.value()
        register_val = self.eeprom.read_from_register(register)
        self.window.LINE_eeprom_read_value.setText(register_val)

        # ***************************************************************************************

    def eeprom_write(self):
        # self.hardware.eeprom.test_data()
        register = self.SPIN_eeprom_write_address.value() * 32
        num_bytes = self.SPIN_eeprom_num_bytes.value()
        if self.window.CHK_eeprom_blank_value.isChecked():
            data = 0xFF
        else:
            data = self.window.LINE_eeprom_write_value.text()
            num_bytes = len(data)
        self.eeprom.write_to_register_manual(register, num_bytes, data)

        # ***************************************************************************************

    def set_frequencies(self, val):
        pri_frequency = self.window.SPIN_primary_frequency.value()
        sec_frequency = self.window.SPIN_secondary_frequency.value()
        pri_cs = self.decoder.chip_select_primary_freq
        sec_cs = self.decoder.chip_select_secondary_freq
        pri_clock_freq = self.speedgenerator.primary_source_frequency
        sec_clock_freq = self.speedgenerator.secondary_source_frequency
        shape = 0
        self.coderategenerator.frequency_to_registers(pri_frequency, pri_clock_freq, shape, pri_cs)
        self.coderategenerator.frequency_to_registers(sec_frequency, sec_clock_freq, shape, sec_cs)

        # ***************************************************************************************

    def frequencies_toggle(self, value):
        self.log.debug("Frequencies toggle {}".format(value))
        if value:
            self.gpio.GPIO.write(self.coderategenerator.toggle_pin, 1)
            self.window.LBL_frequency_selected.setText("SEC")
        elif not value:
            self.gpio.GPIO.write(self.coderategenerator.toggle_pin, 0)
            self.window.LBL_frequency_selected.setText("PRI")

        # ***************************************************************************************

    def primary_gain_set_percent(self):
        primary_gain = self.window.SPIN_primary_gain_percent.value()
        self.log.debug("Set PRIMARY Gain to {}%".format(primary_gain))
        if self.window.CHK_gain_lock_percent.isChecked() is True:
            self.window.SPIN_secondary_gain_percent.setValue(primary_gain)
        self.window.gains.primary_gain_set_percent(primary_gain)

        # ***************************************************************************************

    def secondary_gain_set_percent(self):
        secondary_gain = self.window.SPIN_secondary_gain_percent.value()
        self.window.log.debug("Set SECONDARY Gain to {}%".format(secondary_gain))
        self.gains.secondary_gain_set_percent(secondary_gain)

        # ***************************************************************************************

    def primary_gain_set_ohms(self):
        primary_gain = self.window.SPIN_primary_gain_ohms.value()
        self.log.debug("Set PRIMARY Gain to {} ohms".format(primary_gain))
        if self.CHK_gain_lock_ohms.isChecked() is True:
            self.window.SPIN_secondary_gain_ohms.setValue(primary_gain)
        self.gains.primary_gain_set_ohms(primary_gain)

        # ***************************************************************************************

    def secondary_gain_set_ohms(self):
        secondary_gain = self.window.SPIN_secondary_gain_ohms.value()
        self.log.debug("Set SECONDARY Gain to {} ohms".format(secondary_gain))
        self.gains.secondary_gain_set_ohms(secondary_gain)

        # ***************************************************************************************
        # toggles encoders on screen visible

    def show_encoders(self, state):
        if state:
            self.window.QDIAL_primary_gain.setVisible(True)
            self.window.QDIAL_secondary_gain.setVisible(True)
            self.window.QDIAL_speed_1.setVisible(True)
            self.window.QDIAL_speed_2.setVisible(True)
            self.window.LBL_PRIMARY_GAIN.setVisible(True)
            self.window.LBL_SECONDARY_GAIN.setVisible(True)
        else:
            self.window.QDIAL_primary_gain.setVisible(False)
            self.window.QDIAL_secondary_gain.setVisible(False)
            self.window.QDIAL_speed_1.setVisible(False)
            self.window.QDIAL_speed_2.setVisible(False)
            self.window.LBL_PRIMARY_GAIN.setVisible(False)
            self.window.LBL_SECONDARY_GAIN.setVisible(False)

        # ************************************************************************************
        # routines
        # populates IO buttons on GUI with Text

    def gpio_buttons_create(self):
        # create io button text
        y = 0
        for x in range(1, 41):
            y = y + 1
            mode = self.gpio.GPIO.get_mode(y)
            # TODO figure out how to get this to work converted to Pyside from PyQt5
            if mode == 0:
                txtmode = "I"
                # button = getattr(self, 'gpio_%s' % x)
                # button.setText(str(y) + " (" + txtmode + ")")
                # self.window.buttonGroup.setId(button, y)
            elif mode == 1:
                txtmode = "O"
                # button = getattr(self, 'gpio_%s' % x)
                # button.setText(str(y) + " (" + txtmode + ")")
                # self.window.buttonGroup.setId(button, y)
            else:
                pass
                # txtmode = "O"
                # button = getattr(self, 'gpio_%s' % x)
                # button.setVisible(False)

        # ************************************************************************************
        # list available fonts

    def fonts_list(self):
        # fonts
        f_db = QFontDatabase()
        for family in f_db.families():
            print(family)

        # ************************************************************************************
        # load from configuration file

    def ini_file_load(self):
        self.display_brightness = self.config.getint('MAIN', 'screen_brightness')
        self.guiname = self.config.get('MAIN', 'gui')
        self.poll_timer_interval = self.config.getint('MAIN', 'poll_timer_interval')
        self.local_timer_interval = self.config.getint('MAIN', 'local_timer_interval')
        self.sense_timer_interval = self.config.getfloat('MAIN', 'sense_timer_interval')
        self.switch_timer_interval = self.config.getint('MAIN', 'switch_timer_interval')
        self.screen_brightness_max = self.config.getint('MAIN', 'screen_brightness_max')
        self.screen_brightness_min = self.config.getint('MAIN', 'screen_brightness_min')

        # ************************************************************************************

    def ip_address_query(self):
        try:
            gw = os.popen("ip -4 route show default").read().split()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((gw[2], 0))
            ipaddr = s.getsockname()[0]
            gateway = gw[2]
            host = socket.gethostname()
            self.log.info("IP: {} GW: {} Host:{}".format(str(ipaddr), str(gateway), str(host)))
            self.window.LBL_ip_address.setText("IP: {} GW: {} Host:{}".format(str(ipaddr), str(gateway), str(host)))
        except:
            self.log.exception("Failed to get ip", exc_info=True)

        # ************************************************************************************
        # startup TCP server to accept commands and control remotely

    def comm_server_start(self):
        HOST = '10.0.0.111'
        PORT = 1337
        try:
            self.server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
            # self.server.setup(self)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server.allow_reuse_address = True
            self.server_thread.start()
            ThreadedTCPRequestHandler.emitter.signal.connect(self.comm_callback)
            self.log.info('TCP Server loop running in thread: {self.server_thread.name}')
        except Exception:
            self.log.info("TCP server failed to start...")

        # ************************************************************************************
        # callback from received commands from TCP

    def comm_callback(self, data, peer_info):
        # TODO:  Try and change these to simulate the button pushes ie  "self.window.PB_display_timer_toggle.click()"
        data = data.rstrip()
        command = data.split("=")
        ip, port = peer_info
        self.log.info("Received TCP COMMAND:{} with DATA:{}".format(command[0], command[1]))
        if command[0] == "TIMERS_ON":
            self.timers_changed(True)
        elif command[0] == "TIMERS_OFF":
            self.timers_changed(False)
        elif command[0] == "QUERY_ALL":
            self.comm_send_query_data("all", peer_info)
        elif command[0] == "PULSECODES":
            self.comm_send_query_data("PULSECODES", peer_info)
        elif command[0] == "PRIGAIN":
            # self.primary_gain_change(int(command[1]))
            self.gains.primary_gain_set_percent(float(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "SECGAIN":
            self.secondary_gain_change(float(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "PRIFREQ":
            self.pri_freq_value = int(command[1])
            self.coderategenerator.coderate_generate([self.coderate_value, self.pri_freq_value, self.sec_freq_value])
        elif command[0] == "SECFREQ":
            self.sec_freq_value = int(command[1])
            self.coderategenerator.coderate_generate([self.coderate_value, self.pri_freq_value, self.sec_freq_value])
        elif command[0] == "CODERATE":
            self.coderate_value = int(command[1])
            self.coderategenerator.coderate_generate([self.coderate_value, self.pri_freq_value, self.sec_freq_value])
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "CODERATEBUTTONID":
            self.coderate_pushbutton_change(int(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        elif command[0] == "FREQBUTTONID":
            self.frequency_pushbutton_change(int(command[1]))
            # self.comm_send_query_data("OK", peer_info)
        else:
            self.comm_send_query_data("COMMAND ERROR", peer_info)

        # ************************************************************************************
        # send data to remote client

    def comm_send_query_data(self, data, peer_info):
        dataout = ""
        self.log.info("Sending Query data out")
        if data == "PULSECODES":
            dataout = ' '.join(map(str, self.company_pulsecodes)) + "\r" + '\n'
        elif data == "OK":
            dataout = "OK"
        dataout = dataout + "\r\n"
        HOST = peer_info[0]
        PORT = int(peer_info[1])
        SOCKET = socket.socket()
        SOCKET.connect((HOST, PORT))
        SOCKET.send(dataout.encode())
        SOCKET.close()
        # self.comm_server_start()

        # ************************************************************************************
        # manages button click on IO screen

    def gpio_button_clicked(self, buttonid):
        button = getattr(self, 'gpio_%s' % buttonid)
        if button.isChecked():
            state = 1
            pinvalue, pinmode = self.gpio.set_pin(buttonid, state)
            self.log.debug("gpio ON  {}  {}  {}".format(buttonid, pinmode, pinvalue))
            self.window.LBL_gpio_display.setText(
                "Button {}  is an {} and value is {}".format(buttonid, pinmode, pinvalue))
        else:
            # self.log.debug("button is released")
            state = 0
            pinvalue, pinmode = self.gpio.set_pin(buttonid, state)
            self.log.debug("gpio OFF {}  {}  {}".format(buttonid, pinmode, pinvalue))
            self.window.LBL_gpio_display.setText(
                "gpio {}  is an {} and value is {}".format(buttonid, pinmode, pinvalue))

        # ************************************************************************************
        # turns display timer on and off (mostly for debugging)

    def display_timer_toggled(self, value):
        self.log.debug("Display Timer change PB pressed {}".format(value))
        if not value:
            self.local_timer.stop()
            # self.PB_display_timer.checked(True)
        if value:
            self.local_timer.start(self.local_timer_interval)

        # ************************************************************************************
        # turns display timer on and off (mostly for debugging)

    def current_sense_timer_toggled(self, value):
        self.log.debug("Current Sense Timer change PB pressed {}".format(value))
        if not value:
            self.sense_timer.stop()
        if value:
            self.sense_timer.start(self.sense_timer_interval)

        # ************************************************************************************

    def poll_timer_toggled(self, value):
        self.log.debug("Poll Timer change PB pressed {}".format(value))
        if not value:
            self.poll_timer.stop()
        if value:
            self.poll_timer.start(self.poll_timer_interval)

        # ************************************************************************************
        # turns display timer on and off (mostly for debugging)

    def switches_timer_toggled(self, value):
        self.log.debug("Switch Timer change PB pressed {}".format(value))
        if not value:
            self.switch_timer.stop()
        if value:
            self.switch_timer.start(self.switch_timer_interval)

        # ************************************************************************************
        # CALLED WHEN SWITCH TIMER EXPIRES

    def switches_run(self):
        self.pollvalues.switch_read_values()

        # ************************************************************************************
        # CALLED WHEN SWITCH TIMER EXPIRES

    def sense_read_poll_values(self):
        self.pollvalues.poll_read_values()

        # ************************************************************************************
        # CALLED WHEN SENSE TIMER EXPIRES

    def sense_poll(self):
        self.pollvalues.current_sense()

        # ************************************************************************************
        # CALLED WHEN CODERATE TIMER EXPIRES

    def code_rate_poll(self):
        self.coderategenerator.run_coderate()

        # ************************************************************************************
        # called when either code rate selector button changes

    def code_rate_selector_change(self, value):
        display_txt = ""
        pri_freq = 0
        sec_freq = 0
        self.log.debug("Code rate selector changed {}".format(value))
        if value == "UP":
            self.coderate_selector = self.coderate_selector + 1
        elif value == "DOWN":
            self.coderate_selector = self.coderate_selector - 1
        if self.coderate_selector > len(self.company_pulsecodes) - 1:
            self.coderate_selector = len(self.company_pulsecodes) - 1
        if self.coderate_selector < 0:
            self.coderate_selector = 0
        self.log.debug("Selector Value: {}".format(self.coderate_selector))
        try:
            code_rate = self.company_pulsecodes[self.coderate_selector][0]
            pri_freq = self.company_pulsecodes[self.coderate_selector][1]
            sec_freq = self.company_pulsecodes[self.coderate_selector][3]
            display_txt = "({}) CODERATE:{:>4} | PRI FREQ:{:>4} | SEC FREQ:{:>4}".format(self.coderate_selector + 1,
                                                                                         code_rate,
                                                                                         pri_freq, sec_freq)
        except IndexError:
            self.log.exception("ERROR ", exc_info=True)
        self.window.LBL_coderate_selection.setText(display_txt)
        self.coderategenerator.coderate_generate(self.company_pulsecodes[self.coderate_selector])
        self.freq_val1 = int(pri_freq)
        self.freq_val2 = int(sec_freq)

        # ************************************************************************************
        # CALLED WHEN LOCAL TIMER EXPIRES

    def display_update(self):
        cpu_percentage_numeric = psutil.cpu_percent()
        cpu_percentage_string = 'CPU:{}'.format(psutil.getloadavg())
        cpu_temperature_numeric = psutil.sensors_temperatures(fahrenheit=True)
        cpu_temperature_degree = cpu_temperature_numeric.get("cpu-thermal")[0][1]
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        memory = psutil.virtual_memory()
        log = False
        if log:
            self.log.debug('LOCAL TIMER RUNNING...')
            self.log.debug("CPU %: {}".format(cpu_percentage_numeric))
            self.log.debug("CPU LOAD AVG : {}".format(cpu_percentage_string))
            self.log.debug("CPU Temperature : {} def F".format(cpu_temperature_numeric))
            self.log.debug("BootTime : {}".format(boot_time))
            self.log.debug("Memory : {}".format(memory))
            self.log.debug("THREADS RUNNING {0:d}".format(threading.active_count()))

            code_rate = self.company_pulsecodes[self.coderate_selector][0]
            pri_freq = self.company_pulsecodes[self.coderate_selector][1]
            sec_freq = self.company_pulsecodes[self.coderate_selector][3]
            txt = "({}) CODERATE:{:>4} | PRI FREQ:{:>4} | SEC FREQ:{:>4}".format(self.coderate_selector + 1, code_rate,
                                                                                 pri_freq, sec_freq)
            self.log.debug(txt)
        self.window.LBL_threads_value.setText(str(threading.active_count()))
        self.window.LBL_cpu_percent_value.setText("{:3.2f}".format(cpu_percentage_numeric))
        self.window.LBL_cpu_temperature_value.setText("{:3.2f}".format(cpu_temperature_degree))
        self.window.LBL_boot_time_value.setText(boot_time)
        self.window.LBL_pri_tach_freq.setText("{:5.0f}".format(self.speed_generator.speed1_actual_freq))
        self.window.LBL_sec_tach_freq.setText("{:5.0f}".format(self.speed_generator.speed2_actual_freq))
        self.window.LBL_primary_gain_percent.setText("{0:.3%}".format(self.digitalpots.wiper_total_percentage[0]))
        self.window.LBL_secondary_gain_percent.setText("{0:.3%}".format(self.digitalpots.wiper_total_percentage[1]))

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
        self.thread_info()
        self.sense_callback_loop_counter = self.sense_callback_loop_counter + 1
        if self.calibration_complete:
            self.log.debug("Need to scale the output based on the calibration data obtained")
        else:
            if self.sense_callback_loop_counter == 10:
                self.adc_average = self.adc_average / (self.sense_callback_loop_counter - 1)
                self.adc_average = self.adc_average * 1000
                self.final_adc_value = self.adc_average
                self.display_amps = (self.adc_scale * self.final_adc_value)
                self.window.LBL_display_adc.setText("{:4.2f}".format(self.adc_average))
                self.display_amps = self.display_amps / 1000
                self.window.LBL_display_amps.setText("{:2.3f}".format(self.display_amps))
                self.window.LBL_loop_current_1.setText("{:2.3f}".format(self.display_amps))
                self.window.LBL_display_adc_counts.setText("{:5.0f}".format(counts))
                self.adc_average = 0
                self.sense_callback_loop_counter = 0
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

        # self.lcd_switches.display(switch_value)
        self.thread_info()

        # ************************************************************************************
        # call back from CODE RATE CHANGE

    def code_rate_callback_change_value(self, freq, duty):
        self.log.debug('GUI received Coderate: FREQ {} DUTY {}'.format(freq, duty))
        self.thread_info()

        # ************************************************************************************
        # GET THREAD INFO FOR DEBUGGING

    def thread_info(self):
        # TODO see what this is crashing with pyside
        pass
        # val = QtCore.QThread.currentThreadId(), threading.current_thread().name
        # thread_value = str(val)
        # return thread_value

        # ************************************************************************************
        # CATCH BRIGHTNESS BUTTON CHANGE

    def brightness_changed(self, value):
        if value >= self.screen_brightness_max:
            value = self.screen_brightness_max
        if value <= self.screen_brightness_min:
            value = self.screen_brightness_min
        self.log.debug('GUI brightness changed to ' + str(value))
        self.support.brightness_set(value)

        # ************************************************************************************
        # CATCH CODE RATE FREQ SLIDER CHANGE

    def code_rate_frequency_changed(self, value):
        self.code_rate_frequency = value
        self.code_rate_freq_duty_cycle(self.code_rate_frequency, self.code_rate_duty_cycle)

        # ************************************************************************************
        # CATCH CODE RATE DUTY CYCLE CHANGE

    def code_rate_duty_cycle_changed(self, value):
        self.code_rate_duty_cycle = value
        self.code_rate_freq_duty_cycle(self.code_rate_frequency, self.code_rate_duty_cycle)

        # ************************************************************************************
        # this method is called when the primary gain SCREEN knob is turned
        # it then calls a routine in the simulation class

    def primary_gain_change(self, value):
        self.log.info('START OF PRIMARTY GAIN***********************************')
        self.log.info('Primary gain GUI knob value : ' + str(value))
        self.simulation.change_primary_gain(value)
        self.log.info('END OF PRIMARTY GAIN***********************************')

        # ************************************************************************************
        # this method is called when the SECONDARY gain SCREEN knob is turned
        # it then calls a routine in the simulation class

    def secondary_gain_change(self, value):
        self.log.debug('START OF SECONDARY GAIN***********************************')
        self.log.debug('Secondary gain GUI knob value : ' + str(value))
        self.simulation.change_secondary_gain(value)
        self.log.debug('END OF SECONDARY GAIN************************************')

        # ************************************************************************************
        # this method is called when the SPEED 1 SCREEN knob is turned
        # it then calls a routine in the simulation class

    def speed_1_change(self, value):
        self.log.debug('START OF SPEED 1******************************************')
        self.log.debug('Speed 1 GUI knob value : ' + str(value))
        self.simulation.change_speed_1(value)
        self.log.debug('END OF SPEED 1********************************************')

        # ************************************************************************************
        # this method is called when the SPEED 2 SCREEN knob is turned
        # it then calls a routine in the simulation class

    def speed_2_change(self, value):
        self.log.debug('START OF SPEED 2******************************************')
        self.log.debug('Speed 2 GUI knob value : ' + str(value))
        self.simulation.change_speed_2(value)
        self.log.debug('END OF SPEED 2********************************************')

        # ************************************************************************************
        # CATCHES CHANGE IN CARRIER FREQUENCY BUTTON

    def carrier_freq_changed(self, value):
        if not value:
            self.log.debug('START OF CHANGE CARRIER***********************************')
            self.log.debug('Change carrier Freq')
            self.simulation.carrier_freq_changed()
            self.log.debug('END OF CHANGE CARRIER***********************************')

        # ************************************************************************************
        # CATCHES SPEED 1 KNOB PUSHED

    def speed_1_dial_released(self):
        self.log.debug('Speed 1 GUI knob RELEASED')
        self.speed_generator.speed_1_off()

        # ************************************************************************************
        # CATCHES SPEED 2 KNOB PUSHED

    def speed_2_dial_released(self):
        self.log.debug('Speed 2 GUI knob RELEASED')
        # self.speed_generator.speed_2_off()

        # ************************************************************************************
        # CATCHES PRIMARY KNOB PUSHED

    def primary_gain_dial_released(self):
        self.log.debug('Primary Gain GUI knob RELEASED')
        self.switches.switch_parse_return_values(0b00000001)

        # ************************************************************************************
        # CATCHES SECONDARY KNOB PUSHED

    def secondary_gain_dial_released(self):
        self.log.debug('Secondary Gain GUI knob RELEASED')
        # self.gains.secondary_gain_off()

        # ************************************************************************************
        # catch either freq or duty cycle changed

    def code_rate_freq_duty_cycle(self, frequency, duty_cycle):
        self.coderategenerator.frequency = frequency
        self.coderategenerator.duty_cycle = duty_cycle
        if self.coderategenerator.frequency == 0 or self.coderategenerator.duty_cycle == 0:
            self.window.LBL_CODE_RATE_FREQ.setText(str('OFF'))
            self.window.LBL_CODE_RATE_DUTY.setText(str('OFF'))
        else:
            self.window.LBL_CODE_RATE_FREQ.setText(str(self.coderategenerator.frequency / 100))
            self.window.LBL_CODE_RATE_DUTY.setText(str(self.coderategenerator.duty_cycle))
        self.log.debug('Stopping coderate thread')
        self.coderategenerator.coderate_stop()
        self.log.debug('CHANGING code rate settings FREQ: {}  DUTY:  {}'.format(self.code_rate_frequency / 100,
                                                                                self.code_rate_duty_cycle))
        # self.coderate_thread.coderategenerator.run_coderate([self.code_rate_frequency, self.code_rate_duty_cycle])
        self.log.debug("CODE RATE STARTED IN THREAD {}".format(threading.current_thread()))

        # ************************************************************************************
        # CATCHES EXIT SHUTDOWN

    def exit_application(self, signum, frame):
        self.log.info("Starting shutdown")
        self.log.debug("Received signal from signum: {} with frame:{}".format(signum, frame))
        self.shutdown()

        # ************************************************************************************
        # TODO: only allow items that have previsouly run. items here are running that havent been perfromed
        # TODO: try "ATEXIT"

    def shutdown(self):
        self.gains.setval_and_store(0)
        self.gains.primary_gain_off()
        self.gains.secondary_gain_off()
        self.coderategenerator.coderate_stop()
        self.speed_generator.speed_1_off()
        self.speed_generator.speed_2_off()
        self.local_timer.stop()
        self.switch_timer.stop()
        self.sense_timer.stop()
        try:
            self.server.server_close()
        except:
            print("Error")
        # self.log.info('Turning off screen saver forced on')
        # subprocess.call('xset dpms force off', shell=True)
        self.log.info("Goodbye...")
        logging.shutdown()
        sys.exit(0)

        # ************************************************************************************
        # close event

    def closeEvent(self, event):
        self.log.info('Close event started...')
        event.accept()

        # ************************************************************************************
        # read data from EEPROM calls routine in hardware class

    def eeprom_read_data(self):
        self.log.debug('Reading data from EEPROM')
        try:
            company = self.eeprom.read_from_register('company')
        except:
            self.log.exception("EXCEPTION in eeprom_read_data", exc_info=True)
            # TODO remove this
            company = "SIEMENS MOBILITY"
        try:
            self.company_pulsecodes = self.coderategenerator.pulse_codes_from_company(company)
            self.log.debug("Pulsecode list loaded: {}".format(self.company_pulsecodes))
        except:
            self.log.exception("Exception")

        # ************************************************************************************
        # local coderate test

    def code_rate_test(self):
        values = [180, 100, 180, 250]
        self.crg.generate_test_pulse(values)

        # ************************************************************************************

    def sinewave(self):
        freq1 = 1
        freq2 = 2
        freq3 = self.freq_val1 / 100
        freq4 = self.freq_val2 / 100
        amp1 = 1
        amp2 = 4
        amp3 = 6
        amp4 = 8
        speed = .4
        cycle1 = self.cycle1
        cycle2 = self.cycle2
        end3 = 20
        end4 = 10
        start3 = 10
        start4 = 0
        t1 = np.arange(0, cycle1, 0.01)
        t2 = np.arange(0, cycle2, 0.01)
        t3 = np.arange(start3, end3, .01)
        t4 = np.arange(start4, end4, .01)
        f1 = sin(freq1 * pi * t1 + self.i) * amp1
        f2 = sin(freq2 * pi * t2 + self.i) * amp2
        f3 = sin(freq3 * pi * t3 + self.i) * amp3
        f4 = sin(freq4 * pi * t4 + self.i) * amp4
        # self.trace("sin1", t1, f1)
        # self.trace("sin2", t2, f2)
        self.trace("sin3", t3, f3)
        self.trace("sin4", t4, f4)
        self.i += speed
        self.window.LBL_graph_time.setText(str(cycle1))

    def sinewave2(self, time_plot, value_plot):
        self.plot(time_plot, value_plot)
        # self.trace("Current", time_plot, value_plot)

        # ************************************************************************************

    def trace(self, name, dataset_x, dataset_y):
        if name in self.traces:
            self.traces[name].setData(dataset_x, dataset_y)
        else:
            self.traces[name] = self.graphWidget.plot(pen='y')

    def exit_application(self, signum, frame):
        self.log.debug("Starting shutdown")
        self.log.debug("Received signal from signum: {} with frame:{}".format(signum, frame))
        sys.exit(0)
