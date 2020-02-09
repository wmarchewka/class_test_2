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
from hardware import digitalpots
from communication import communication
from gui import securitylevel
from hardware import pollvalues
from hardware import switches
from hardware import currentsense
from hardware import gains

class Loader(object):

    def __init__(self):

        logger_class = logger.Logger()
        config_class = config.Config(logger_class)
        secuirtylevel_class = securitylevel.SecurityLevel(logger_class)
        communication_class = communication.TCP_support(logger_class)
        commander_class = commander.Commander(logger_class)
        pollingpermission_class = pollingpermission.Pollingpermission(commander_class)
        gpio_class = gpio.Gpio(config_class, commander_class)
        decoder_class =  decoder.Decoder(config_class, gpio_class)
        spi_class = spi.SPI(config_class, decoder_class, pollingpermission_class)
        digitalpots_class = digitalpots.DigitalPots(config_class, decoder_class, spi_class)
        gains_class = gains.Gains(digitalpots_class)
        coderategenerator_class = coderategenerator.Coderategenerator(config_class, spi_class ,gpio_class)
        speedgenerator_class = speedgenerator.Speedgenerator(commander_class, config_class, decoder_class, coderategenerator_class)
        switches_class = switches.Switches(spi_class,gains_class)
        currentsense_class = currentsense.CurrentSense(spi_class)
        rotary_class = rotary.Rotary(pollingpermission_class, gpio_class, config_class, speedgenerator_class)
        gui_class = gui.Mainwindow(commander_class, config_class, digitalpots_class, secuirtylevel_class)
        pollvalues_class = pollvalues.Pollvalues(pollingpermission_class, currentsense_class, switches_class)

