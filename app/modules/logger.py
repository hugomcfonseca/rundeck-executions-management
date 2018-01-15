#!/usr/bin/python

from logging import getLogger, StreamHandler, Formatter, debug, info, warning, error, critical, \
                    DEBUG, INFO, WARNING, ERROR, CRITICAL
from sys import stdout


class Logger(object):
    '''
    This class provides write contents to a logging output (e.g., stdout), only if it has a lo
    level equal or higher than a minimum log level defined in the creation of Logger object. 
    '''

    _log = None

    def __init__(self, level=2, formatter=None):
        if not formatter:
            self._formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            self._formatter = formatter

        self._level = level
        self._log = getLogger()
        self.__set_level()
        self.__attach_handler()

    def __set_level(self):
        '''...'''
        if self._level == 1:
            self._log.setLevel(DEBUG)
        elif self._level == 2:
            self._log.setLevel(INFO)
        elif self._level == 3:
            self._log.setLevel(WARNING)
        elif self._level == 4:
            self._log.setLevel(ERROR)
        elif self._level == 5:
            self._log.setLevel(CRITICAL)

    def __attach_handler(self):
        '''...'''
        handler = StreamHandler(stdout)
        handler.setFormatter(Formatter(self._formatter))

        if self._level == 1:
            handler.setLevel(DEBUG)
        elif self._level == 2:
            handler.setLevel(INFO)
        elif self._level == 3:
            handler.setLevel(WARNING)
        elif self._level == 4:
            handler.setLevel(ERROR)
        elif self._level == 5:
            handler.setLevel(CRITICAL)

        self._log.addHandler(handler)

    def write(self, message, level=2):
        '''
        Only write to log output if level is equal or greater
        than minimum log level defined in the creation of class object
        '''

        if self._level <= level:
            if level == 1:
                debug(message)
            elif level == 2:
                info(message)
            elif level == 3:
                warning(message)
            elif level == 4:
                error(message)
            elif level == 5:
                critical(message)
