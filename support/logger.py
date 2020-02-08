import os
import logging
import logging.config


class Logger(object):

    def __init__(self):

        self.init = True
        self.log_config_file_path = "config/logging.ini"
        cwd = os.getcwd()
        try:
            logging.config.fileConfig(self.log_config_file_path)
        except FileNotFoundError:
            self.logging_error = "Could not find " + str(self.log_config_file_path)
        self.log = logging.getLogger(__name__)
        self.log.info('Starting up portable tester...')
        self.log.info("CWD: {}".format(cwd))
        self.log.debug("{} init complete...".format(__name__))

