import logging
class Commander(object):

    def __new__(cls, commander):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
            ("Creating new class {}".format(cls.instance))
        else:
            print("Creating instance class {}".format(cls.instance))
        return cls.instance

    def __init__(self, commander):
        self.init = True
        self.commander = commander
        self.log = self.commander.log
        self.log = logging.getLogger(__name__)
        self.log.debug("{} init complete...".format(__name__))


    def parsescreen(self, value):
        self.log.debug("Commander received value {}".format(value))