import os
import ConfigParser
from ConfigLoader import ConfigLoader

class HandlerNotReturnStringError(Exception):
    def __init__(self, message):
        self.message = message
        

class ConfigFileLoader(ConfigLoader):

    def __init__(self, fileconfig, handler, logger):
        if not os.access(fileconfig, os.R_OK):
            raise AttributeError
        if handler is None:
            raise AttributeError
        if logger is None:
            raise AttributeError
        self.config_handler = handler
        self.logger = logger
        self.config = ConfigParser.ConfigParser()
        self.config.read([fileconfig])

    def handler_request(self, name):
        self.logger.debug('pass request to handler for "%s"' % name)
        result = self.config_handler(name)  # richiamo la funzione per le richieste

        if result is not None and not isinstance(result, str):
            raise HandlerNotReturnStringError()

        return result  # il risultato deve sempre essere di tipo stringa o None

    def try_to_obtain(self, result, name, errmsg):
        if result is not None and len(result) != 0:  # se il primo risultato e' giusto
            return result

        result = self.handler_request(name)  # tento con l'handler
        if result is not None:  # se l'handler e' giusto
            return result

        self.logger.error(errmsg)  # stampo il messaggio di errore nel logger
        return None

    def get_smartcard_info_path(self):
        self.logger.debug('read smartcard library path from config file')

        return self.try_to_obtain(
            self.config.get('library', 'smartcard_info_path'),
            'smartcard_info_path',
            errmsg='no smart card info path found'
        )

    def set_smartcard_info_path(self, path):
        ConfigLoader.set_smartcard_info_path(self, path)
        self.config.set('library', 'smartcard_info_path', path)

    def get_smartcard_driver_path(self):
        self.logger.debug('read smartcard driver path from config file')

        return self.try_to_obtain(
            self.config.get('library', 'smartcard_driver_path'),
            'smartcard_driver_path',
            errmsg='no smartcard driver path found'
        )

    def set_smartcard_driver_path(self, path):
        ConfigLoader.set_smartcard_driver_path(self, path)
        self.config.set('library', 'smartcard_driver_path', path)

    def get_engine_driver_path(self):
        self.logger.debug('read engine path from config file')

        return self.try_to_obtain(
            self.config.get('library', 'engine_driver_path'),
            'engine_driver_path',
            errmsg='no engine path found'
        )

    def set_engine_driver_path(self, path):
        ConfigLoader.set_engine_driver_path(self, path)
        self.config.set('library', 'engine_driver_path', path)

    def get_timestamp_username(self):
        self.logger.debug('read timestamp username from config file')

        return self.try_to_obtain(
            self.config.get('timestamp', 'username'),
            'timestamp_username',
            errmsg='no timestamp username found'
        )

    def set_timestamp_username(self, username):
        ConfigLoader.set_timestamp_username(self, username)
        self.config.set('timestamp', 'username', username)

    def get_timestamp_password(self):
        self.logger.debug('read timestamp password from config file')

        return self.try_to_obtain(
            self.config.get('timestamp', 'password'),
            'timestamp_password',
            errmsg='no timestamp password found'
        )

    def set_timestamp_password(self, password):
        ConfigLoader.set_timestamp_password(self, password)
        self.config.set('timestamp', 'password', password)

    def get_smartcard_pin(self):
        self.logger.debug('read smartcard pin from config file')

        return self.try_to_obtain(
            self.config.get('smartcard', 'pin'),
            'smartcard_pin',
            errmsg='no smartcard pin found'
        )

    def set_smartcard_pin(self, pin):
        ConfigLoader.set_smartcard_pin(self, pin)
        self.config.set('smartcard', 'pin', pin)

    def get_smartcard_puk(self):
        self.logger.debug('read smartcard puk from config file')

        return self.try_to_obtain(
            self.config.get('smartcard', 'puk'),
            'smartcard_puk',
            errmsg='no smartcard puk found'
        )

    def set_smartcard_puk(self, puk):
        ConfigLoader.set_smartcard_puk(self, puk)
        self.config.set('smartcard', 'puk', puk)

