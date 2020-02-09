import inspect
from hardware import gpio
from hardware import rotary
from hardware import pollingpermission
from support import config
from support import logger
from gui import gui
from support import commander
from hardware import speedgenerator
from hardware import decoder
from support import coderategenerator
from hardware import spi

class Loader(object):

    def __init__(self):
        logger_class = logger.Logger()
        config_class = config.Config(logger_class)
        commander_class = commander.Commander(logger_class)
        pollingpermission_class = pollingpermission.Pollingpermission(commander_class)
        gpio_class = gpio.Gpio(config_class, commander_class)
        decoder_class =  decoder.Decoder(config_class, gpio_class)
        spi_class = spi.SPI(config_class, decoder_class, pollingpermission_class)
        coderategenerator_class = coderategenerator.Coderategenerator(config_class, spi_class ,gpio_class)
        speedgenerator_class = speedgenerator.Speedgenerator(commander_class, config_class, decoder_class, coderategenerator_class)
        rotary_class = rotary.Rotary(pollingpermission_class, gpio_class, config_class, speedgenerator_class)
        gui_class = gui.Mainwindow(commander_class, config_class)


