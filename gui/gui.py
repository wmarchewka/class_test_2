import signal
import sys
import logging

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QTimer, QFile, QObject
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QTableWidgetItem


class Mainwindow(QObject):
    def __init__(self, commander):
        super().__init__()
        self.commander = commander
        self.log = self.commander.log
        self.log = logging.getLogger(__name__)
        self.loadscreen()
        self.signal_and_slots()
        self.exit_signalling()
        self.log.debug("{} init complete...".format(__name__))

    def exit_signalling(self):
        signal.signal(signal.SIGINT, self.exit_application)
        signal.signal(signal.SIGTERM, self.exit_application)

    def loadscreen(self):
        try:
            self.guiname = "gui/mainwindow.ui"
            ui_file = QFile(self.guiname)
            ui_file.open(QFile.ReadOnly)

            loader = QUiLoader()
            self.window = loader.load(ui_file)
            ui_file.close()

            self.window.show()
            self.log.debug('Loading screen ' + self.guiname)

        except FileNotFoundError:
            self.log.debug("Could not find {}".format(self.guiname))  # CATCHES EXIT SHUTDOWN

    def signal_and_slots(self):
        self.window.PB_1.clicked.connect(self.commander.parsescreen)  # self.)

    def exit_application(self, signum, frame):
        self.log.debug("Starting shutdown")
        self.log.debug("Received signal from signum: {} with frame:{}".format(signum, frame))
        sys.exit(0)
