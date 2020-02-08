import inspect
from hardware import gpio
from hardware import rotary
from hardware import pollingpermission
from support import config
from support import logger
from gui import gui
from support import commander

class Loader(object):

    def __init__(self):
        logger_class = logger.Logger()
        config_class = config.Config(logger_class)
        commander_class = commander.Commander(logger_class)
        pollingpermission_class = pollingpermission.Pollingpermission(commander_class)
        gpio_class = gpio.Gpio(config_class, commander_class)
        rotary_class = rotary.Rotary(pollingpermission_class, gpio_class)
        print(rotary_class.__dict__)


        gui_class = gui.Mainwindow(commander_class)



