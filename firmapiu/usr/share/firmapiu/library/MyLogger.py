#!/usr/bin/python

ERROR = 0
STATUS = 1
DEBUG = 2

class Logger(object):

    def __init__(self, write_function):
        if write_function is None:
            raise AttributeError
        self.write_function = write_function

    def set_write_function(self, write_function):
        self.write_function = write_function

    def write(self, type, message):
        self.write_function(type, message)

    def error(self, message):
        self.write(ERROR, message)

    def status(self, message):
        self.write(STATUS, message)

    def debug(self, message):
        self.write(DEBUG, message)
