#!/usr/bin/python


class ConfigLoader(object):
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

    def set_smartcard_pin(self, pin):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_smartcard_puk(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_smartcard_puk(self, puk):
        raise NotImplementedError("Subclass must implement abstract method")

