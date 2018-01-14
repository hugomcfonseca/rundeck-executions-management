#!/usr/bin/python

import logging
import sys


class Logger(object):
    '''...'''

    self._log = None

    def __init__(self, level=3, formatter=None):
        self._level = level

        if not formatter:
            self._formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            self._formatter = formatter

        self._log = logging.getLogger()

        aux = logging.StreamHandler(sys.stdout)
        aux.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        aux.setFormatter(formatter)
        log.addHandler(aux)

    def __set_log_level__(self):
        '''...'''
        if self._level == 1:
            self._log.setLevel(logging.DEBUG)
        elif self._level == 2:
            self._log.setLevel(logging.INFO)
        elif self._level == 3:
            self._log.setLevel(logging.WARNING)
        elif self._level == 4:
            self._log.setLevel(logging.ERROR)
        elif self._level == 5:
            self._log.setLevel(logging.CRITICAL)  

    def write(self, message):
        '''...'''

        if self._level == 1:
            logging.debug(message)
        elif self._level == 2:
            logging.info(message)
        elif self._level == 3:
            logging.warning(message)
        elif self._level == 4:
            logging.error(message)
        elif self._level == 5:
            logging.critical(message)
