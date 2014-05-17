#!/usr/bin/python
import os
import logging
from M2Crypto import Engine, m2 # sudo apt-get install python-m2crypto
from M2Crypto import SMIME
from M2Crypto import X509
from M2Crypto.BIO import MemoryBuffer

import SmartcardFetcher
# per l'engine installare sudo apt-get install libengine-pkcs11-openssl


class SignProvider(object):
    def __init__(self, pkcs11_engine='/usr/lib/engines/engine_pkcs11.so', pkcs11_driver=None, pin=None):
        Engine.load_dynamic_engine('pkcs11', pkcs11_engine)
        self.pkcs11_engine = Engine.Engine('pkcs11')
        self.pkcs11_engine.ctrl_cmd_string('MODULE_PATH', pkcs11_driver)
        self.pkcs11_engine.ctrl_cmd_string("PIN", pin)  # senza il pin l'engine chiede il pin da prompt
        self.pkcs11_engine.init()

    def get_ds_private_key(self, ds_id):
        try:
            priv_key = self.pkcs11_engine.load_private_key('slot_0-id_%s' % ds_id)
            return priv_key
        except Engine.EngineError:
            logging.error("no private key found")
            return None

    def get_ds_certificate(self, ds_id):
        try:
            cert = self.pkcs11_engine.load_certificate('slot_0-id_%s' % ds_id)
            return cert
        except Engine.EngineError:
            logging.error("no certificate found")
            return None


def sign_file_with_ds_certificate(library, pin, filename):
    if not os.access(filename, os.R_OK):
        logging.error("No file to sign %s found" % filename)
        return None
    if not os.access(library, os.R_OK):
        logging.error("No library file found")
        return None

    logging.debug("opening file: " + filename)
    text = open(filename).read()
    logging.debug("convert file in memorybuffer")
    text_buffer = MemoryBuffer(text)

    sign = SignProvider(pkcs11_driver=library, pin=pin)
    smartcard_atr = SmartcardFetcher.get_smartcard_atr()
    smartcard_library = SmartcardFetcher.get_smartcard_library(smartcard_atr)
    smartcard = SmartcardFetcher.SmartcardFetcher(smartcard_library)

    # ottengo l'id per estrarre il certificato dall smartcard
    logging.debug("get digital signature id")
    ds_id = smartcard.get_ds_id()

    # ottengo la chiave privata e il ceritficato utili per firmare
    logging.debug("get private key reference")
    pkey = sign.get_ds_private_key(ds_id)
    logging.debug("get certificate reference")
    certificate = sign.get_ds_certificate(ds_id)

    signer = SMIME.SMIME()
    signer.pkey = pkey
    signer.x509 = certificate

    # firmo il buffer
    pkcs7 = signer.sign(text_buffer)

    # creo un buffere di uscita
    out = MemoryBuffer()
    pkcs7.write_der(out)
    # per scriverlo in pem pkcs11.write(out)

    p7m_out = open("%s.p7m" % filename, "w")
    p7m_out.write(out.read())
    return True

def verify_file_with_ds_certificate(library, pin, filename_p7m, is_self_signed=True):
    if not os.access(filename_p7m, os.R_OK):
        logging.error("No file to sign %s found" % filename_p7m)
        return None
    if not os.access(library, os.R_OK):
        logging.error("No library file found")
        return None

    sign = SignProvider(pkcs11_driver=library, pin=pin)
    smartcard_atr = SmartcardFetcher.get_smartcard_atr()
    smartcard_library = SmartcardFetcher.get_smartcard_library(smartcard_atr)
    smartcard = SmartcardFetcher.SmartcardFetcher(smartcard_library)

    ds_id = smartcard.get_ds_id()  # ottengo l'id per estrarre il certificato dall smartcard
    certificate = sign.get_ds_certificate(ds_id)  # ottengo il certificato

    # creo uno store di certificati
    store_stack = X509.X509_Stack()
    store_stack.push(certificate)

    store = X509.X509_Store()
    store.add_x509(certificate)

    signer = SMIME.SMIME()
    signer.set_x509_stack(store_stack)
    signer.set_x509_store(store)
    #p7, data = SMIME.load_pkcs7(filename_p7m)  # carico il file firmato in formato PEM

    p7m_buffer = open(filename_p7m).read()
    input_bio = MemoryBuffer(p7m_buffer)
    p7 = SMIME.PKCS7(m2.pkcs7_read_bio_der(input_bio._ptr()), 1)

    data_bio = None
    if is_self_signed:
        v = signer.verify(p7, data_bio, flags=SMIME.PKCS7_NOVERIFY)
    else:
        v = signer.verify(p7, data_bio)

    print v

if __name__ == "__main__":
    # sign_file_with_ds_certificate("/usr/local/lib/libbit4ipki.so", "29035896", "prova.txt")
    verify_file_with_ds_certificate("/usr/local/lib/libbit4ipki.so", "29035896", "rfc3161.pdf.p7m")
