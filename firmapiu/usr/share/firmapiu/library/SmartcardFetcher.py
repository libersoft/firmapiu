#!/usr/bin/python
import os
import sys
import smartcard
import PyKCS11
import libxml2
from smartcard.util import toHexString
from smartcard import pcsc


class NoSlotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class NoTokenFoundException(Exception):
    def __init__(self, message):
        self.message = message


class NoDigitalSignaturaFoundException(Exception):
    def __init__(self, message):
        self.message = message


class SmartcardFetcher(object):
    def __init__(self, smartcard_driver_path, logger):
        if smartcard_driver_path is None:
            raise AttributeError
        if logger is None:
            raise AttributeError

        self.smartcard_driver_path = smartcard_driver_path
        self.logger = logger
        self.pkcs11_obj = None
        self.session = None

    def __load_pkcs11(self):
        self.pkcs11_obj = PyKCS11.PyKCS11Lib()
        self.pkcs11_obj.load(self.smartcard_driver_path)
        slots = self.pkcs11_obj.getSlotList()
        if not len(slots):
            raise NoSlotFoundException()
        self.session = self.pkcs11_obj.openSession(slots[0])  # di default uso la prima slot

    def get_ds_id(self):
        if self.pkcs11_obj is None:
            self.__load_pkcs11()

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

#        buffer_der = StringIO.StringIO()  # creo un buffer per contenere il certificato in formato DER
#        for unicode_val in value:
#            buffer_der.write(chr(unicode_val))
#        return buffer_der.getvalue()


def get_smartcard_atr(logger):
    """return the atr of the current device"""
    if logger is None:
        raise AttributeError

    try:
        readers_list = smartcard.System.readers()  # ottengo la lista dei lettori
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
    except smartcard.Exceptions.CardConnectionException, errmsg:
        logger.error(errmsg)
        return None

    return atr_str


def get_smartcard_library(atr, config, logger):
    """in base all'atr restituisco quale libreria e' utile usare"""
    if config is None or logger is None:
        raise AttributeError

    smartcard_info_path = config.get_smartcard_info_path()
    if smartcard_info_path is None:
        logger.error("smartcard library not set in config")
        return None

    if not os.path.exists(smartcard_info_path):
        logger.error("no library xml found")
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


def dump_digital_signature_id():
    atr = get_smartcard_atr()  # ottengo l'atr della smartcard
    if atr is None:
        return 1

    library = get_smartcard_library(atr)  # ottengo la libreria per l'atr
    if library is None:
        return 1

    fetcher = SmartcardFetcher(library)  # creo la classe per ottenere le info sulla smartcard
    print fetcher.get_ds_id()

    return 0
    # ottengo il buffer in formato DER
#    buffer_certificate_der = fetcher.dump_ds_der_certificate(slot_use)
#    if buffer_certificate_der is None:
#        return 1
#
#    # salvo il certificato in formato PEM
#    x509_obj = X509.load_cert_string(buffer_certificate_der, X509.FORMAT_DER)
#    if not x509_obj.save_pem(filename):
#        logging.error("unable to save PEM certificate")
#        return 1

if __name__ == "__main__":
    sys.exit(dump_digital_signature_id())
