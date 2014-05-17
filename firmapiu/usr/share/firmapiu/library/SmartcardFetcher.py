#!/usr/bin/python
import os
import sys
import logging
#import StringIO
import smartcard
import PyKCS11
import libxml2
#from M2Crypto import X509
from smartcard.util import toHexString

class NoSlotFoundException(Exception):
    pass


class NoTokenFoundException(Exception):
    pass


class NoDigitalSignaturaFoundException(Exception):
    pass


class SmartcardFetcher(object):
    def __init__(self, library_path, slot_use=-1):
        self.library_path = library_path
        self.pkcs11_obj = PyKCS11.PyKCS11Lib()
        self.pkcs11_obj.load(self.library_path)
        if slot_use == -1 :
            self.slot_use = self.__get_default_slot()
        else:
            self.slot_use = slot_use

    def __get_default_slot(self):
        slots = self.pkcs11_obj.getSlotList()
        
        if not len(slots):
            raise NoSlotFoundException()

        return slots[0]  # di default uso la prima slot

    def get_ds_id(self):
        session = self.pkcs11_obj.openSession(self.slot_use)
        cert_objects = session.findObjects( template=( 
                (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE), 
                (PyKCS11.CKA_CERTIFICATE_TYPE, PyKCS11.CKC_X_509),
                (PyKCS11.CKA_TOKEN, True),
                (PyKCS11.CKA_TRUSTED, True)
            )
        )  # ottengo i token di tipo certificato della smartcard

        cert_objects_len = len(cert_objects)

        if not cert_objects_len:  # se non ho trovato certificati
            logging.error("no token found into smartcard")
            raise NoTokenFoundException()

        ds_id = None
        # cerco nei certificati CKO_CERTIFICATE quelli che contengono DS
        for cert_obj in cert_objects:
            attrs = session.getAttributeValue(cert_obj, (PyKCS11.CKA_LABEL,PyKCS11.CKA_ID))
            if "DS" in attrs[0]:
                ds_id = ''.join([hex(elem)[2:] for elem in attrs[1]])
                # ds_id = ''.join([chr(elem) for elem in attr[1]])
                # value = attr_dict[PyKCS11.CKA_VALUE]  # ottengo una tupla contenente il DER della smartcard

        if ds_id is None:
            logging.error("no DS signature found")
            raise NoDigitalSignaturaFoundException()

        return ds_id

#        buffer_der = StringIO.StringIO()  # creo un buffer per contenere il certificato in formato DER
#        for unicode_val in value:
#            buffer_der.write(chr(unicode_val))
#        return buffer_der.getvalue()


def get_smartcard_atr():
    """return the atr of the current device"""

    try:
        readers_list = smartcard.System.readers()  # ottengo la lista dei lettori
    except smartcard.pcsc.PCSCExceptions.EstablishContextException:
        logging.error("demone pcscd not attivo")  # il lettore di smartcard potrebbe non essere inserito
        return None

    # non sono riuscito a trovare nessun lettore
    if len(readers_list) == 0:
        logging.error("nessun lettore riconosciuto")
        return None

    reader = readers_list[0]  # di default prendo il primo lettore
    connection = reader.createConnection()
    try:
        # Mi connetto e ottengo l'ATR dalla carta
        connection.connect()
        atr_str = toHexString(connection.getATR()).replace(" ", ":").lower()
        connection.disconnect()
    except smartcard.Exceptions.CardConnectionException, errmsg:
        logging.error(errmsg)
        return None

    return atr_str


def get_smartcard_library(atr):
    """in base all'atr restituisco quale libreria e' utile usare"""
    if not os.path.exists("libraries.xml"):
        logging.error("no library xml found")
        return None

    doc = libxml2.parseFile("libraries.xml")  # carico il file xml con le librerie e cerco la libreria relativa all'ATR
    library_result = doc.xpathEval("//key[text()='%s']/../@path" % atr)  # in base all'atr cerco nel file usando XPATH
    if len(library_result) == 0:  # se non trovo nessun risultato
        logging.error("no library found")
        return None

    library_used = library_result[0].get_content()  # ottengo il path della libreria
    return library_used


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
