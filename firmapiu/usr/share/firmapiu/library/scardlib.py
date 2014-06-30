import os
import libxml2
from smartcard.util import toHexString
from smartcard import pcsc
from smartcard import System
from smartcard import Exceptions
import localconfig

import PyKCS11
import M2Crypto.Engine
from holder import Holder
from loglib import Logger

from conflib import ConfigReader

class NoSlotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class NoTokenFoundException(Exception):
    def __init__(self, message):
        self.message = message


class NoDigitalSignaturaFoundException(Exception):
    def __init__(self, message):
        self.message = message


class SmartcardHolder(Holder):
    def __init__(self, config, logger):
        assert isinstance(config, ConfigReader)
        assert isinstance(logger, Logger)

        self.pkcs11_engine = None
        self.pkcs11_obj = None
        self.config = config
        self.logger = logger

    def _load_pkcs11(self):
        if self.pkcs11_obj is not None:
            return True
        
        self.pkcs11_obj = PyKCS11.PyKCS11Lib()
        self.pkcs11_obj.load(self.smartcard_driver_path)
        slots = self.pkcs11_obj.getSlotList()
        if not len(slots):  # se non trovo slot
            return False
        # di default uso la prima slot
        self.session = self.pkcs11_obj.openSession(slots[0])
        return True
     
    def get_ds_id(self):
        if not self._load_pkcs11():
            return None

        cert_objects = self.session.findObjects(
            template=(
                (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                (PyKCS11.CKA_CERTIFICATE_TYPE, PyKCS11.CKC_X_509),
                (PyKCS11.CKA_TOKEN, True),
                (PyKCS11.CKA_TRUSTED, True)
            )
        )  # ottengo i token di tipo certificato della smartcard

        cert_objects_len = len(cert_objects)

        if not cert_objects_len:  # se non ho trovato certificati
            self.logger.error('no token found into smartcard')
            raise NoTokenFoundException()

        ds_id = None
        # cerco nei certificati CKO_CERTIFICATE quelli che contengono DS
        for cert_obj in cert_objects:
            attrs = self.session.getAttributeValue(cert_obj, (PyKCS11.CKA_LABEL,PyKCS11.CKA_ID))
            if "DS" in attrs[0]:
                ds_id = ''.join([hex(elem)[2:] for elem in attrs[1]])
                # ds_id = ''.join([chr(elem) for elem in attr[1]])
                # value = attr_dict[PyKCS11.CKA_VALUE]  # ottengo una tupla contenente il DER della smartcard

        if ds_id is None:
            self.logger.error('no DS signature found')
            raise NoDigitalSignaturaFoundException()

        return ds_id 
     
    def load_engine(self):
        # se l'engine e' gia stato caricato
        if self.pkcs11_engine is not None:
            return True

        # se settato ottengo il driver dell'engine
        engine_drv_path = self.config.get_engine_driver_path()
        if engine_drv_path is None:
            return False

        if not os.access(engine_drv_path, os.R_OK):
            self.logger.error('no engine driver path found at %s' % engine_drv_path)
            return False

        self.engine_driver_path = engine_drv_path

        scard_drv_path = self.config.get_smartcard_driver_path()  # ottengo il path della smartcard dalle config
        if scard_drv_path is None:  # se non sono riuscito ad ottenere il driver della smartcard
            scard_atr = get_smartcard_atr(self.logger)  # ottengo l'atr della smartcard
            if scard_atr is None:  # se non sono riuscito ad ottenere l'atr
                return False
            scard_drv_path = get_smartcard_library(
                scard_atr, self.config, self.logger
            )  # ottengo il path del driver della smarcard
            if scard_drv_path is None:  # se non sono ancora riuscito ad ottenere il path
                return False
        self.smartcard_driver_path = scard_drv_path

        scard_pin = self.config.get_smartcard_pin()  # ottengo il pin della smartcard
        if scard_pin is None:
            return False

        if M2Crypto.Engine.load_dynamic_engine('pkcs11', self.engine_driver_path) is None:
            self.logger.error('failed to create dynamic pkcs11 engine')
            return False
        
        self.logger.debug('create engine using pin:%s' % scard_pin)
        self.pkcs11_engine = M2Crypto.Engine.Engine('pkcs11')
        self.pkcs11_engine.ctrl_cmd_string('MODULE_PATH', self.smartcard_driver_path)
        self.pkcs11_engine.ctrl_cmd_string("PIN", scard_pin)  # senza il pin l'engine chiede il pin da prompt
        # TODO da controllare il login con un pin errate perche' non da' errore
        if not self.pkcs11_engine.init():
            return False
        else:
            return True
    
    def get_private_key(self):
        '''
        override del metodo
        '''
        if not self.load_engine():
            return None  # nel caso sia fallito il caricamento

        try:
            priv_key = self.pkcs11_engine.load_private_key('slot_0-id_%s' % self.get_ds_id())
            return priv_key
        except M2Crypto.Engine.EngineError:
            self.logger.error("chiave privata non ottenuta, forse pin sbagliato")
            return None
        
    def get_certificate(self):
        '''
        override del metodo
        '''
        if not self.load_engine():
            return None  # nel caso sia fallito il caricamento

        try:
            cert = self.pkcs11_engine.load_certificate('slot_0-id_%s' % self.get_ds_id())
            return cert
        except M2Crypto.Engine.EngineError:
            self.logger.error("no certificate found")
            return None


def get_smartcard_atr(logger):
    """return the atr of the current device"""
    if logger is None:
        raise AttributeError

    try:
        readers_list = System.readers()  # ottengo la lista dei lettori
    except pcsc.PCSCExceptions.EstablishContextException:
        logger.error("demone pcscd not attivo")  # il lettore di smartcard potrebbe non essere inserito
        return None

    # non sono riuscito a trovare nessun lettore
    if len(readers_list) == 0:
        logger.error("nessun lettore riconosciuto")
        return None

    reader = readers_list[0]  # di default prendo il primo lettore
    connection = reader.createConnection()
    try:
        # Mi connetto e ottengo l'ATR dalla carta
        connection.connect()
        atr_str = toHexString(connection.getATR()).replace(" ", ":").lower()
        connection.disconnect()
    except Exceptions.CardConnectionException:
        logger.error('No smartcard inserted')
        return None

    return atr_str


def get_smartcard_library(atr, config, logger):
    """in base all'atr restituisco quale libreria e' utile usare"""
    if config is None or logger is None:
        raise AttributeError

    smartcard_info_path = localconfig.LIBRARY_FILE

    if not os.path.exists(smartcard_info_path):
        logger.error('no file %s found' % smartcard_info_path)
        return None

    # carico il file xml con le librerie e cerco la libreria relativa all'ATR
    doc = libxml2.parseFile(smartcard_info_path)
    # in base all'atr cerco nel file usando XPATH
    smartcard_driver_paths = doc.xpathEval("//key[text()='%s']/../@path" % atr)
    if len(smartcard_driver_paths) == 0:  # se non trovo nessun risultato
        logger.error("no library found")
        return None

    smart_card_driver_used = smartcard_driver_paths[0].get_content()  # ottengo il path della libreria
    return smart_card_driver_used