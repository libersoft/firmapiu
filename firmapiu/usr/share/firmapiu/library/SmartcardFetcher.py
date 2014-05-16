#!/usr/bin/python2
import logging
import smartcard
import PyKCS11
import libxml2
import sys
from smartcard.util import toHexString


class SmartcardFetcher(object):
    def __init__(self, library_path):
        self.library_path = library_path
        self.pkcs11_obj = PyKCS11.PyKCS11Lib()
        self.pkcs11_obj.load(self.library_path)

    def get_slot_list(self):
        return self.pkcs11_obj.getSlotList()

    def get_slot_info(self, slot):
        assert isinstance(slot, int)
        return self.pkcs11_obj.getSlotInfo(slot)

    def get_token_info(self, slot):
        assert isinstance(slot, int)
        return self.pkcs11_obj.getTokenInfo(slot)

    def dump_ds_certificate(self, slot, outfile):
        assert isinstance(slot, int)
        assert isinstance(outfile, str)

        session = self.pkcs11_obj.openSession(slot)
        all_attributes = PyKCS11.CKA.keys()  # tutti gli attrivuti possibili per i token
        all_attributes = [e for e in all_attributes if isinstance(e, int)]
        objects = session.findObjects()  # ottengo i token della smartcard

        if not len(objects):  # se non sono presenti token
            logging.error("nessun token trovato")
            return False

        for obj in objects:
            attributes = session.getAttributeValue(obj, all_attributes)
            attr_dict = dict(zip(all_attributes, attributes))

            # cerco nei certificati CKO_CERTIFICATE quelli che contengono DS
            if attr_dict[PyKCS11.CKA_CLASS] == PyKCS11.CKO_CERTIFICATE and \
                    attr_dict[PyKCS11.CKA_TRUSTED] and \
                    attr_dict[PyKCS11.CKA_TOKEN] and \
                    attr_dict[PyKCS11.CKA_CERTIFICATE_TYPE] == PyKCS11.CKC_X_509 and \
                    "DS" in str(attr_dict[PyKCS11.CKA_LABEL]):
                # print attr_dict[PyKCS11.CKA_ID]
                # faccio un dump della sessione
                value = attr_dict[PyKCS11.CKA_VALUE]
                cert_file = open(outfile, "wb")
                for unicode_val in value:
                    cert_file.write(chr(unicode_val))
                cert_file.close()

        return True


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

    doc = libxml2.parseFile("libraries.xml")  # carico il file xml con le librerie e cerco la libreria relativa all'ATR
    library_result = doc.xpathEval("//key[text()='%s']/../@path" % atr)  # in base all'atr cerco nel file usando XPATH
    if len(library_result) == 0:  # se non trovo nessun risultato
        logging.error("non ho trovato nessuna libreria")
        return None

    library_used = library_result[0].get_content()  # ottengo il path della libreria
    return library_used


def dump_certificate(filename="certificate.der"):
    atr = get_smartcard_atr()  # ottengo l'atr della smartcard
    if atr is None:
        return 1

    library = get_smartcard_library(atr)  # ottengo la libreria per l'atr
    if library is None:
        return 1

    fetcher = SmartcardFetcher(library)  # creo la classe per ottenere le info sulla smartcard
    slot_list = fetcher.get_slot_list()  # ottengo la lista degli slot per la smartcard

    logging.debug("test number of slot found")
    if not len(slot_list):  # se non ci sono slot inserite
        logging.error("no slot found")
        return 1
    else:  # di default uso la prima
        slot_use = slot_list[0]

    if fetcher.dump_ds_certificate(slot_use, filename):
        logging.debug("dump del certificato riuscito")
        return 0
    else:
        logging.error("dump del certificato non riuscito")
        return 1

if __name__ == "__main__":
    if len(sys.argv) == 2:
        sys.exit(dump_certificate(sys.argv[1]))
    else:
        sys.exit(dump_certificate())