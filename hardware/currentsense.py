import logging

# **********************************************************************************************
class CurrentSense(object):
    def __init__(self, spi):
        self.spi = spi
        self.decoder = self.spi.decoder
        self.logger = self.spi.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.log.debug('Current Sense initializing...')
        self.log.debug("{} init complete...".format(__name__))


    # read from current sense a/d converter
    def read_spi(self):
        # need to send 2 bytes of dummy data to clock in the data returned
        return_data = self.spi.read(0, 2, self.decoder.chip_select_current_sense, [0xFF, 0xFF])
        return return_data