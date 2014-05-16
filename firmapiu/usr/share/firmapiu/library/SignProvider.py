import logging
from M2Crypto import Engine, m2 # sudo apt-get install python-m2crypto
from M2Crypto.X509 import load_cert, FORMAT_DER
from M2Crypto.SMIME import SMIME
from M2Crypto.BIO import MemoryBuffer
# per l'engine installare sudo apt-get install libengine-pkcs11-openssl


class SignProvider(object):
    def __init__(self, pkcs11_engine='/usr/lib/engines/engine_pkcs11.so', pkcs11_driver=None, pin=None):
        Engine.load_dynamic_engine('pkcs11', pkcs11_engine)
        self.pkcs11_engine = Engine.Engine('pkcs11')
        self.pkcs11_engine.ctrl_cmd_string('MODULE_PATH', pkcs11_driver)
        self.pkcs11_engine.ctrl_cmd_string("PIN", pin)  # senza il pin l'engine chiede il pin da prompt
        self.pkcs11_engine.init()

    def get_private_key(self, slot_id):
        try:
            priv_key = self.pkcs11_engine.load_private_key(slot_id)
            return priv_key
        except Engine.EngineError:
            logging.error("no private key found")
            return None

    def get_certificate(self, slot_id):
        try:
            cert = self.pkcs11_engine.load_certificate(slot_id)
            return cert
        except Engine.EngineError:
            logging.error("no certificate found")
            return None

    def sign_file_with_certificate(self):
        pass

    def verify_file_with_certificate(self):
        pass

if __name__ == "__main__":
    sign = SignProvider(pkcs11_driver='/usr/local/lib/libbit4ipki.so', pin='29035896')
    certificate = sign.get_certificate('445330')
    pkey = sign.get_private_key('445330')
    # print certificate
    # print priv_key
    #x509_obj = load_cert("certificate.der", FORMAT_DER)  # carico il certificato in formato DER
    # text = open("Resoconto.ods").read()
    # text_buffer = MemoryBuffer(text)
    # signer = SMIME()
    # signer.sign(text_buffer)
    # out = MemoryBuffer()
    # signature = out.getvalue()
    # pkcs11_engine.finish()