import logging
from PySide2 import QtWidgets

# *******************************************************************************
class SecurityLevel:
    def __init__(self, logger, level=None):
        self.level = level
        self.logger = logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.tab_pages = []
    # *******************************************************************************
    def set_security_level(self, level, window, ):
        if level == "admin":
            pass
        elif level == "technician":
            self.tabWidget_remove("GRAPH", window)
            self.tabWidget_remove("EEPROM", window)
            self.tabWidget_remove("SPILOG", window)
            self.tabWidget_remove("MISC", window)
            self.tabWidget_remove("CAL", window)
            window.TECH_FRAME_manual_gpio.setVisible(False)
            window.TECH_FRAME_cs_manual.move(10, 10)
            window.TECH_FRAME_gpio_manual.move(10, 85)
            window.TECH_FRAME_brightness.move(10, 170)

        elif level == "customer":
            self.tabWidget_remove("GRAPH", window)
            self.tabWidget_remove("EEPROM", window)
            self.tabWidget_remove("SPILOG", window)
            self.tabWidget_remove("TECH", window)
            self.tabWidget_remove("MISC", window)
            self.tabWidget_remove("MAIN", window)
            self.tabWidget_remove("CAL", window)
            window.SPIN_primary_gain_percent.setVisible(False)
            window.LBL_spin_primary_gain_percent.setVisible(False)
            window.SPIN_secondary_gain_percent.setVisible(False)
            window.LBL_spin_secondary_gain_percent.setVisible(False)
            window.SPIN_primary_gain_ohms.setVisible(False)
            window.LBL_spin_primary_gain_ohms.setVisible(False)
            window.SPIN_secondary_gain_ohms.setVisible(False)
            window.LBL_spin_secondary_gain_ohms.setVisible(False)
            window.SPIN_primary_frequency.setVisible(False)
            window.LBL_spin_primary_frequency.setVisible(False)
            window.SPIN_secondary_frequency.setVisible(False)
            window.LBL_spin_secondary_frequency.setVisible(False)
            window.PB_frequencies_toggle.setVisible(False)
            window.PB_primary_gain_value.setVisible(False)
            window.SPIN_primary_gain_value.setVisible(False)
            window.PB_store_in_nvram.setVisible(False)
            window.PB_nvram_to_wiper.setVisible(False)
            window.CHK_gain_lock_ohms.setVisible(False)
            window.CHK_gain_lock_percent.setVisible(False)
            window.LBL_eeprom_write_value_text.setVisible(False)
            window.LBL_eeprom_read_value_text.setVisible(False)
            window.LBL_write_page.setVisible(False)
            window.LBL_write_numbytes.setVisible(False)
            window.LBL_read_page.setVisible(False)
            window.LBL_read_value.setVisible(False)
            window.FRAME_primary_gain.setVisible(False)
            window.FRAME_secondary_gain.setVisible(False)
            window.FRAME_set_frequencies.setVisible(False)
            window.FRAME_eeprom_write.setVisible(False)
            window.FRAME_eeprom_read.setVisible(False)
            window.FRAME_stats.setVisible(False)
            window.TECH_FRAME_brightness.setVisible(False)
            window.FRAME_eeprom_data.setVisible(False)
            window.FRAME_coderate_alternate.setVisible(False)
            window.TECH_FRAME_manual_gpio.setVisible(False)
            window.TECH_FRAME_cs_manual.setVisible(True)
            window.TECH_FRAME_gpio_manual.setVisible(True)
            window.TECH_FRAME_switch_indicators.setVisible(True)
            window.FRAME_auto_gain.setVisible(False)
            window.FRAME_graph.setVisible(False)
            window.FRAME_adc_readings.setVisible(False)
            window.SPIN_eeprom_write_address.setVisible(False)
            window.SPIN_eeprom_num_bytes.setVisible(False)
            window.SPIN_eeprom_read_address.setVisible(False)
            window.LINE_eeprom_write_value.setVisible(False)
            window.LINE_eeprom_read_value.setVisible(False)
            window.CHK_eeprom_blank_value.setVisible(False)
            window.CHK_primary_frequency_auto.setVisible(False)
            window.CHK_secondary_frequency_auto.setVisible(False)
            window.PB_eeprom_write.setVisible(False)
            window.PB_popup_test.setVisible(False)
            window.PB_graph_left.setVisible(False)
            window.PB_graph_right.setVisible(False)
            window.PB_eeprom_read.setVisible(False)
            window.PB_eeprom_read_2.setVisible(False)
            window.TBL_cal_values.setVisible(False)
            window.LBL_cal_average_5.setVisible(False)
            window.LBL_display_adc_counts.setVisible(False)
            window.LBL_cal_average.setVisible(False)
            window.LBL_cal_complete.setVisible(False)
            window.LBL_cal_average_2.setVisible(False)
        # *******************************************************************************

    def tabWidget_remove(self, tabname, window):
        page = window.tabWidget.findChild(QtWidgets.QWidget, tabname)
        self.log.debug("PAGE={}".format(page))
        index = window.tabWidget.indexOf(page)
        window.tabWidget.removeTab(index)

        # *******************************************************************************

    def tabWidget_change(self, tabname, window):
        page = window.tabWidget.findChild(QtWidgets.QWidget, tabname)
        self.log.debug("PAGE={}".format(page))
        index = window.tabWidget.indexOf(page)
        window.tabWidget.setCurrentIndex(index)
        self.log.debug("Changed to TAB {}".format(page))

        # *******************************************************************************

    def tabWidget_add(self, tabname, window):
        for page, title in self.tab_pages:
            if window.tabWidget.indexOf(page) < 0:
                window.tabWidget.addTab(page, title)
                self.log.debug("Added TAB {}".format(title))

    # *******************************************************************************
    def index_tab_pages(self, window):
        self.tab_pages = []
        for index in range(window.tabWidget.count()):
            self.tab_pages.append((
                window.tabWidget.widget(index),
                window.tabWidget.tabText(index),
            ))
        self.log.debug("Tab pages {}".format(self.tab_pages))