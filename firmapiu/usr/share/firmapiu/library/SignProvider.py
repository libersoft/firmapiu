#!/usr/bin/python
import os
from M2Crypto import Engine, m2  # sudo apt-get install python-m2crypto
from M2Crypto import SMIME
from M2Crypto import X509
from M2Crypto import BIO

import SmartcardFetcher
# per l'engine installare sudo apt-get install libengine-pkcs11-openssl


class SignProvider(object):
    def __init__(self, config, logger, fetch_pin=False):
        if config is None:
            raise AttributeError
        if logger is None:
            raise AttributeError
        self.config = config  # istanza del file di configurazione
        self.logger = logger  # oggetto di tipo Logger.Logger da controllare
        self.must_fetch_pin = fetch_pin
        self.pkcs11_engine = None
        self.smartcard_driver_path = None
        self.engine_driver_path = None

    def load_engine(self):
        if self.pkcs11_engine is not None:  # se l'engine e' gia stato caricato
            return True

        engine_drv_path = self.config.get_engine_driver_path()
        if engine_drv_path is None:
            return False

        self.engine_driver_path = engine_drv_path

        scard_drv_path = self.config.get_smartcard_driver_path()  # ottengo il path della smartcard dalle config
        if scard_drv_path is None:  # se non sono riuscito ad ottenere il driver della smartcard
            scard_atr = SmartcardFetcher.get_smartcard_atr(self.logger)  # ottengo l'atr della smartcard
            if scard_atr is None:  # se non sono riuscito ad ottenere l'atr
                return False
            scard_drv_path = SmartcardFetcher.get_smartcard_library(
                scard_atr, self.config, self.logger
            )  # ottengo il path del driver della smarcard
            if scard_drv_path is None:  # se non sono ancora riuscito ad ottenere il path
                return False

        self.smartcard_driver_path = scard_drv_path

        if Engine.load_dynamic_engine('pkcs11', self.engine_driver_path) is None:
            return False

        self.pkcs11_engine = Engine.Engine('pkcs11')
        self.pkcs11_engine.ctrl_cmd_string('MODULE_PATH', self.smartcard_driver_path)

        if self.must_fetch_pin:  # se e' rischiesto un inserimento del pin
            pin = self.config.get_smartcard_pin()
            if pin is None:
                return False
            self.logger.debug('create engine using pin:%s' % pin)
            self.pkcs11_engine.ctrl_cmd_string("PIN", pin)  # senza il pin l'engine chiede il pin da prompt
        # TODO da controllare il login con un pin errate perche' non da' errore

        self.pkcs11_engine.init()
        return True

    def get_ds_private_key(self, ds_id):
        if not self.load_engine():
            return None  # nel caso sia fallito il caricamento

        if not self.must_fetch_pin:  # se non ho avuto accesso al pin
            self.logger.error('pin not insert during initialization, I can\'t access to private key')
            return None
        try:
            priv_key = self.pkcs11_engine.load_private_key('slot_0-id_%s' % ds_id)
            return priv_key
        except Engine.EngineError:
            self.logger.error("no private key found")
            return None

    def get_ds_certificate(self, ds_id):
        if not self.load_engine():
            return None  # nel caso sia fallito il caricamento

        try:
            cert = self.pkcs11_engine.load_certificate('slot_0-id_%s' % ds_id)
            return cert
        except Engine.EngineError:
            self.logger.error("no certificate found")
            return None

    def sign_file_with_ds_certificate(self, filename):
        if not os.access(filename, os.R_OK):  # se riesco a leggere il file da firmare
            self.logger.error("No file to sign '%s' found" % filename)
            return None

        if not self.load_engine():
            return None  # nel caso sia fallito il caricamento

        scard_pin = self.config.get_smartcard_pin()  # ottengo il pin della smartcard
        if scard_pin is None:
            return None

        filename_desc = open(filename)
        input_bio = BIO.File(filename_desc)

        smartcard = SmartcardFetcher.SmartcardFetcher(self.smartcard_driver_path, self.logger)

        self.logger.status("get digital signature id")
        ds_id = smartcard.get_ds_id()  # ottengo l'id per estrarre il certificato dall smartcard

        # ottengo la chiave privata
        self.logger.status("get private key reference")
        pkey = self.get_ds_private_key(ds_id)  # otteno la chiave privata tramite l'id
        if pkey is None:
            return False

        # ottengo il certificato
        self.logger.status("get certificate reference")
        certificate = self.get_ds_certificate(ds_id)
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
        self.logger.status('file firmato correttamente')
        return True

    def verify_file_with_ds_certificate(self, filename, p7filename, is_self_signed=True):
        if not os.access(filename, os.R_OK):
            self.logger.error("No filename to verify '%s' found" % filename)
            return None
        if not os.access(p7filename, os.R_OK):
            self.logger.error("No filename to verify '%s' found" % filename)
            return None

        if not self.load_engine():
            return None  # nel caso sia fallito il caricamento

        smartcard_atr = SmartcardFetcher.get_smartcard_atr(self.logger)
        smartcard_library = SmartcardFetcher.get_smartcard_library(
            smartcard_atr, self.config, self.logger
        )
        smartcard = SmartcardFetcher.SmartcardFetcher(smartcard_library, self.logger)

        self.logger.status('get ds id')
        ds_id = smartcard.get_ds_id()  # ottengo l'id per estrarre il certificato dall smartcard

        self.logger.status('get ds certificate')
        certificate = self.get_ds_certificate(ds_id)  # ottengo il certificato
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

        self.logger.status('read p7mfile %s' % p7filename)
        p7m_fd = open(p7filename, "rb")
        p7_input_bio = BIO.File(p7m_fd)

        # carico il file p7m
        p7 = SMIME.PKCS7(m2.pkcs7_read_bio_der(p7_input_bio._ptr()),
                         1)  # al momento non c'e' nessun modo per estrarre i dati del DER dal certificato
        # p7, data = SMIME.load_pkcs7_bio(p7_input_bio)  # l'input bio deve essere in formato PEM (basa64)

        data_bio = None
        try:
            if is_self_signed:
                self.logger.status('verifing file')
                v = signer.verify(p7, data_bio, flags=SMIME.PKCS7_NOVERIFY)
            else:
                v = signer.verify(p7, data_bio)
        except SMIME.SMIME_Error, e:
            self.logger.error('smime error: ' + str(e))
            return None
        except SMIME.PKCS7_Error, e:
            self.logger.error('pkcs7 error: ' + str(e))
            return None

        # uso il replace perche' i file sono scritti secondo la convenzione binaria che va
        # a capo con \r\n (windows style)
        # v = v.replace('\r', '')
        #
        # logger.status('check difference betweet file and file-signed')
        #
        # log_filename = '%s.log' % filename
        # open(log_filename, 'w').write(v)
        # orig_file_buff = open(filename, "r").read()
        # print len(v)
        # print len(orig_file_buff)
        #
        # if v != orig_file_buff:
        #     logger.error("signed file differ from passed file")
        #     return None

        signers_cert = p7.get0_signers(store_stack)  # ottengo i firmatari del file

        if len(signers_cert) != 1:  # se ci sono piu' firmatari
            self.logger.error("more than one signer present")
            return None

        # il certificato nella smartcard e quello nelle firma non coincidono
        if signers_cert[0].as_pem() != certificate.as_pem():
            self.logger.error("smartcard certificate and p7m certificate not correspond")
            return None

        self.logger.status('All Ok')
        return v
