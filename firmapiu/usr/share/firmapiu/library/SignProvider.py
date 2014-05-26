#!/usr/bin/python
import os
from M2Crypto import Engine, m2 # sudo apt-get install python-m2crypto
from M2Crypto import SMIME
from M2Crypto import X509
from M2Crypto import BIO

import SmartcardFetcher
import MyLogger
# per l'engine installare sudo apt-get install libengine-pkcs11-openssl

class SignProvider(object):
    def __init__(self, pkcs11_engine='/usr/lib/engines/engine_pkcs11.so', pkcs11_driver=None, pin=None, logger=None):
        self.logger = logger  # oggetto di tipo MyLogger.Logger da controllare
        self.pkcs11_engine = pkcs11_engine
        self.pkcs11_driver = pkcs11_driver
        if pin is None:  # inserire il pin serve per poter estrapolare il riferimento alla chiave privata
            self.pin = None
        else:
            self.pin = pin
        self.engine_load = False

    def __load_engine(self):
        if self.engine_load:  # se l'engine e' gia stato caricato
            return True

        if Engine.load_dynamic_engine('pkcs11', self.pkcs11_engine) is None:
            return False

        self.logger.debug('create engine using pin:%s' % self.pin)
        self.pkcs11_engine = Engine.Engine('pkcs11')
        self.pkcs11_engine.ctrl_cmd_string('MODULE_PATH', self.pkcs11_driver)
        if self.pin is not None:
            self.pkcs11_engine.ctrl_cmd_string("PIN", self.pin)  # senza il pin l'engine chiede il pin da prompt
        # TODO da controllare il login con un pin errate perche' non da' errore
        self.pkcs11_engine.init()
        self.engine_load = True
        return True

    def get_ds_private_key(self, ds_id):

        if not self.engine_load and not self.__load_engine():
            return None

        if self.pin is None:
            self.logger.error('pin not insert during initialization, I can\'t access to private key')
            return None
        try:
            priv_key = self.pkcs11_engine.load_private_key('slot_0-id_%s' % ds_id)
            return priv_key
        except Engine.EngineError:
            self.logger.error("no private key found")
            return None

    def get_ds_certificate(self, ds_id):
        if not self.engine_load and not self.__load_engine():
            return None

        try:
            cert = self.pkcs11_engine.load_certificate('slot_0-id_%s' % ds_id)
            return cert
        except Engine.EngineError:
            self.logger.error("no certificate found")
            return None


def sign_file_with_ds_certificate(library, pin, filename, logger=None):
    if not os.access(filename, os.R_OK):
        logger.error("No file to sign %s found" % filename)
        return None
    if not os.access(library, os.R_OK):
        logger.error("No library %s file found" % library)
        return None

    filename_desc = open(filename)
    input_bio = BIO.File(filename_desc)

    sign = SignProvider(pkcs11_driver=library, pin=pin, logger=logger)
    smartcard_atr = SmartcardFetcher.get_smartcard_atr(logger)
    smartcard_library = SmartcardFetcher.get_smartcard_library(smartcard_atr, logger)
    smartcard = SmartcardFetcher.SmartcardFetcher(smartcard_library, logger=logger)

    # ottengo l'id per estrarre il certificato dall smartcard
    logger.status("get digital signature id")
    ds_id = smartcard.get_ds_id()

    # ottengo la chiave privata
    logger.status("get private key reference")
    pkey = sign.get_ds_private_key(ds_id)
    if pkey is None:
        return False

    # ottengo il certificato
    logger.status("get certificate reference")
    certificate = sign.get_ds_certificate(ds_id)
    if certificate is None:
        return False

    signer = SMIME.SMIME()
    signer.pkey = pkey
    signer.x509 = certificate

    # firmo il buffer
    pkcs7 = signer.sign(input_bio)  # TODO da aggiungere try-except

    # creo un buffere di uscita
    out = BIO.MemoryBuffer()
    pkcs7.write_der(out)
    # per scriverlo in pem pkcs11.write(out)

    p7m_out = open("%s.p7m" % filename, "w")
    p7m_out.write(out.read())
    logger.status('file firmato correttamente')
    return True

def verify_file_with_ds_certificate(library, filename, p7m_file , is_self_signed=True, logger=None):
    if not os.access(filename, os.R_OK):
        logger.error("No fiename to verify %s found" % filename)
        return None
    if not os.access(p7m_file, os.R_OK):
        logger.error("No file to sign %s found" % p7m_file)
        return None
    if not os.access(library, os.R_OK):
        logger.error("No library %s file found" % library)
        return None

    sign = SignProvider(pkcs11_driver=library, logger=logger)
    smartcard_atr = SmartcardFetcher.get_smartcard_atr(logger)
    smartcard_library = SmartcardFetcher.get_smartcard_library(smartcard_atr, logger)
    smartcard = SmartcardFetcher.SmartcardFetcher(smartcard_library, logger=logger)

    ds_id = smartcard.get_ds_id()  # ottengo l'id per estrarre il certificato dall smartcard
    certificate = sign.get_ds_certificate(ds_id)  # ottengo il certificato
    if certificate is None:
        return None

    # creo uno store di certificati
    store_stack = X509.X509_Stack()
    store_stack.push(certificate)

    store = X509.X509_Store()
    store.add_x509(certificate)

    signer = SMIME.SMIME()
    signer.set_x509_stack(store_stack)
    signer.set_x509_store(store)
    #p7, data = SMIME.load_pkcs7(p7m_file)  # carico il file firmato in formato PEM

    p7m_file_descriptor = open(p7m_file, "r")
    input_bio = BIO.File(p7m_file_descriptor)

    # carico il file p7m 
    p7 = SMIME.PKCS7(m2.pkcs7_read_bio_der(input_bio._ptr()), 1)  # al momento non c'e' nessun modo per estrarre i dati del DER dal certificato
    # p7, data = SMIME.load_pkcs7_bio(input_bio)  # l'input bio deve essere in formato PEM (basa64)

    data_bio = None
    try:
        if is_self_signed:
            v = signer.verify(p7, data_bio, flags=SMIME.PKCS7_NOVERIFY)
        else:
            v = signer.verify(p7, data_bio)
    except SMIME.SMIME_Error, e:
        logger.error('smime error: ' + str(e))
        return None
    except SMIME.PKCS7_Error, e:
        logger.error('pkcs7 error: ' + str(e))
        return None

    # uso il replace perche' i file sono scritti secondo la convenzione binaria che va a capo con \r\n (windows style)
    v = v.replace('\r', '')

    if v != open(filename, "r").read():
        logger.error("signed file differ from passed file")
        return None

    signers_cert = p7.get0_signers(store_stack)  # ottengo i firmatari del file
    
    if len(signers_cert) != 1:  # se ci sono piu' firmatari
        logger.error("more than one signer present")
        return None

    if signers_cert[0].as_pem() != certificate.as_pem():  # il certificato nella smartcard e quello nelle firma non coincidono
        logger.error("smartcard certificate and p7m certificate not correspond")
        return None

    return v

if __name__ == "__main__":

    def stampa(type, mess): print mess  # stamo i log sullo standard output

    logger = MyLogger.Logger(stampa)
    sign_file_with_ds_certificate("/usr/local/lib/libbit4ipki.so", "29035896", "prova.txt", logger)
    #verify_file_with_ds_certificate("/usr/local/lib/libbit4ipki.so", "29035896", "prova.txt", "prova.txt.p7m")
