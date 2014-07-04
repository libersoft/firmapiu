#!/usr/bin/python

ERROR = 0
STATUS = 1
DEBUG = 2

class Logger(object):

    def __init__(self):
        self._write_function = None
        
    @property
    def function(self):
        return self._write_function
        
    @function.setter
    def function(self, new_function):
        self._write_function = new_function

    def write(self, message_type, message):
        self._write_function(message_type, message)

    def error(self, message):
        self.write(ERROR, message)

    def status(self, message):
        self.write(STATUS, message)

    def debug(self, message):
        self.write(DEBUG, message)
