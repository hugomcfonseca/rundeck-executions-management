#!/usr/bin/python

import logging
import sys


class Logger(object):
    '''...'''

    def __init__(self, level=3, formatter=None):
        self.level = level

        if formatter is None:
            self.formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            self.formatter = formatter

        log = logging.getLogger()

        if self.level == 1:
            log.setLevel(logging.DEBUG)
        elif self.level == 2:
            log.setLevel(logging.INFO)
        elif self.level == 3:
            log.setLevel(logging.WARNING)
        elif self.level == 4:
            log.setLevel(logging.ERROR)
        elif self.level == 5:
            log.setLevel(logging.CRITICAL)

        aux = logging.StreamHandler(sys.stdout)
        aux.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        aux.setFormatter(formatter)
        log.addHandler(aux)

    def write(self, message, log_level=3):
        '''...'''

        if log_level == 1:
            logging.debug(message)
        elif log_level == 2:
            logging.info(message)
        elif log_level == 3:
            logging.warning(message)
        elif log_level == 4:
            logging.error(message)
        elif log_level == 5:
            logging.critical(message)
