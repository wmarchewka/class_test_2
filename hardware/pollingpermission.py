import logging


class Pollingpermission(object):
    def __new__(cls, logger):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
            logger.log.debug("Creating new class {}".format(cls.instance))
        else:
            logger.log.debug("Creating instance class {}".format(cls.instance))
        return cls.instance

    def __init__(self, commander):
        self.init = True
        self.commander = commander
        self.logger = self.commander.logger
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.polling_prohibited = (True, self.__class__)
        self.log.debug("{} init complete...".format(__name__))

    @property
    def polling_prohibited(self):
        self.log.debug("STATUS of Polling Prohibited: {}".format(self._polling_prohibited))
        return self._polling_prohibited

    @polling_prohibited.setter
    def polling_prohibited(self, val):
        setval, caller = val
        self.log.debug("Setting Polling Prohibited to:{} from {}".format(setval, caller))
        self._polling_prohibited = val
