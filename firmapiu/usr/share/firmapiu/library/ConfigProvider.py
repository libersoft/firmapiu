#!/usr/bin/python
import ConfigParser
import os


class ConfigLoader(object):
    def get_smartcard_library_path(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_library_path(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_engine_path(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_timestamp_username(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_timestamp_password(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_smartcard_pin(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_smartcard_puk(self):
        raise NotImplementedError("Subclass must implement abstract method")


class ConfigStaticLoader(ConfigLoader):

    def get_smartcard_library_path(self):
        return '/home/samuel/Dropbox/progettoFirmaPiu/firmapiu/etc/firmapiu/libraries.xml'

    def get_library_path(self):
        return None

    def get_engine_path(self):
        return '/usr/lib/engines/engine_pkcs11.so'

    def get_timestamp_username(self):
        return 'TSA100288'
    
    def get_timestamp_password(self):
        return 'WJVMhoVv'

    def get_smartcard_pin(self):
        return '29035896'
    
    def get_smartcard_puk(self):
        return '84559078'

class ConfigStaticLoader(ConfigLoader):

    def __init__(self, fileconfig):
        if not os.access(fileconfig, os.R_OK):
            raise AttributeError
        self.config = ConfigParser.ConfigParser()
        self.config.read([fileconfig])

    def get_smartcard_library_path(self):
        return self.config.get('library', 'smartcard_library_path')

    def get_library_path(self):
        return self.config.get('library', 'library_path')

    def get_engine_path(self):
        return self.config.get('library', 'engine_path')

    def get_timestamp_username(self):
        return self.config.get('timestamp', 'username')

    def get_timestamp_password(self):
        return self.config.get('timestamp', 'password')

    def get_smartcard_pin(self):
        return self.config.get('smartcard', 'pin')

    def get_smartcard_puk(self):
        return self.config.get('smartcard', 'puk')

class ConfigSqliteLoader(ConfigLoader):
    pass
