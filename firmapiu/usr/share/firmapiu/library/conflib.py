#!/usr/bin/python
import os
import ConfigParser
from loglib import Logger

# TODO da catturare l'errore ConfigParser.NoSectionError: No section: 'certificate'
# TODO da catturare l'errore ConfigParser.NoOptionError: No option 'ca_certificate_path' in section: 'certificate'

class HandlerNotReturnStringError(Exception):
    pass

class ConfigReader(object):
    
    def __init__(self, handler, logger):
        assert isinstance(logger, Logger)
        self.handler = handler
        self.logger = logger
    
    def handler_request(self, name):
        self.logger.debug('pass request to handler for "%s"' % name)
        result = self.handler(name)  # richiamo la funzione per le richieste

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
    
    ####################### CERTIFICATE ###################################
    def get_ca_certificate_path(self):
        raise NotImplementedError("Subclass must implement abstract method")
    
    def set_ca_certificate_path(self, path):
        raise NotImplementedError("Subclass must implement abstract method")
    
    ############################ CRL #######################################
    def get_crl_path(self):
        raise NotImplementedError("Subclass must implement abstract method")
    
    def set_crl_path(self,path):
        raise NotImplementedError("Subclass must implement abstract method")    
    
    ################### SMARTCARD DRIVER ##################################
    def get_smartcard_info_path(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_smartcard_info_path(self, path):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_smartcard_driver_path(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_smartcard_driver_path(self, path):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_engine_driver_path(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_engine_driver_path(self, path):
        raise NotImplementedError("Subclass must implement abstract method")

    #################### TIMESTAMP #########################################

    def get_timestamp_server(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_timestamp_server(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_timestamp_username(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_timestamp_username(self, username):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_timestamp_password(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_timestamp_password(self, password):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_smartcard_pin(self):
        raise NotImplementedError("Subclass must implement abstract method")

    #################### SMARTCARD CREDENTIAL ##############################

    def set_smartcard_pin(self, pin):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_smartcard_puk(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_smartcard_puk(self, puk):
        raise NotImplementedError("Subclass must implement abstract method")


class ConfigFileReader(ConfigReader):

    def __init__(self, fileconfig, handler, logger):
        if not os.access(fileconfig, os.R_OK):
            raise AttributeError
        
        ConfigReader.__init__(self, handler, logger)
        self.config = ConfigParser.ConfigParser()
        self.config.read([fileconfig])

    def get_ca_certificate_path(self):
        self.logger.debug('read ca certificate path from config file')
        
        return self.try_to_obtain(
            self.config.get('certificate', 'ca_certificate_path'),
            'ca_certificate_path',
            errmsg='no ca certificate path found'
        )

    def get_crl_path(self):
        self.logger.debug('read crl path path from config file')
        
        return self.try_to_obtain(
            self.config.get('certificate', 'crl_path'),
            'crl_path',
            errmsg='no crl path found'
        )

    def get_smartcard_info_path(self):
        self.logger.debug('read smartcard library path from config file')

        return self.try_to_obtain(
            self.config.get('library', 'smartcard_info_path'),
            'smartcard_info_path',
            errmsg='no smart card info path found'
        )

    def set_smartcard_info_path(self, path):
        ConfigReader.set_smartcard_info_path(self, path)
        self.config.set('library', 'smartcard_info_path', path)

    def get_smartcard_driver_path(self):
        self.logger.debug('read smartcard driver path from config file')

        return self.try_to_obtain(
            self.config.get('library', 'smartcard_driver_path'),
            'smartcard_driver_path',
            errmsg='no smartcard driver path found'
        )

    def set_smartcard_driver_path(self, path):
        ConfigReader.set_smartcard_driver_path(self, path)
        self.config.set('library', 'smartcard_driver_path', path)

    def get_engine_driver_path(self):
        self.logger.debug('read engine path from config file')

        return self.try_to_obtain(
            self.config.get('library', 'engine_driver_path'),
            'engine_driver_path',
            errmsg='no engine path found'
        )

    def set_engine_driver_path(self, path):
        ConfigReader.set_engine_driver_path(self, path)
        self.config.set('library', 'engine_driver_path', path)


    def get_timestamp_server(self):
        self.logger.debug('read timestamp server from config file')

        return self.try_to_obtain(
            self.config.get('timestamp', 'server'),
            'timestamp_server',
            errmsg='no timestamp server found'
        )

    def set_timestamp_server(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_timestamp_username(self):
        self.logger.debug('read timestamp username from config file')

        return self.try_to_obtain(
            self.config.get('timestamp', 'username'),
            'timestamp_username',
            errmsg='no timestamp username found'
        )

    def set_timestamp_username(self, username):
        ConfigReader.set_timestamp_username(self, username)
        self.config.set('timestamp', 'username', username)

    def get_timestamp_password(self):
        self.logger.debug('read timestamp password from config file')

        return self.try_to_obtain(
            self.config.get('timestamp', 'password'),
            'timestamp_password',
            errmsg='no timestamp password found'
        )

    def set_timestamp_password(self, password):
        ConfigReader.set_timestamp_password(self, password)
        self.config.set('timestamp', 'password', password)

    def get_smartcard_pin(self):
        self.logger.debug('read smartcard pin from config file')

        return self.try_to_obtain(
            self.config.get('smartcard', 'pin'),
            'smartcard_pin',
            errmsg='no smartcard pin found'
        )

    def set_smartcard_pin(self, pin):
        ConfigReader.set_smartcard_pin(self, pin)
        self.config.set('smartcard', 'pin', pin)

    def get_smartcard_puk(self):
        self.logger.debug('read smartcard puk from config file')

        return self.try_to_obtain(
            self.config.get('smartcard', 'puk'),
            'smartcard_puk',
            errmsg='no smartcard puk found'
        )

    def set_smartcard_puk(self, puk):
        ConfigReader.set_smartcard_puk(self, puk)
        self.config.set('smartcard', 'puk', puk)

