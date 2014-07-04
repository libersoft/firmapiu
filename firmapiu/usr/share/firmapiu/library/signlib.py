from M2Crypto import SMIME
from M2Crypto import X509
from M2Crypto import BIO
from M2Crypto import m2

from loglib import Logger
from conflib import ConfigReader
from holder import Holder
from certmanager import CertificateManager
from certmanager import CACertificateNotFoundException

from M2Crypto.X509 import X509_Store

class Signer(object):
    
    def __init__(self, config, logger):
        assert isinstance(logger, Logger)
        assert isinstance(config, ConfigReader)
        
        self.config = config
        self._logger = logger

    def sign(self, holder, certmanager, data):
        assert isinstance(holder, Holder)
        assert isinstance(certmanager, CertificateManager)
                
        # ottengo la chiave privata dall'holder
        pkey = holder.get_private_key()
        
        if pkey is None:
            return None
        
        # ottengo il certificato dall'holder
        cert = holder.get_certificate()

        if cert is None:
            return None
        
        # controllo che il certificato non sia stato revocato prima di firmare
        try:
            if certmanager.is_revoked(cert):
                self._logger.error('cert is revoked')
                return None
        except CACertificateNotFoundException:
            self._logger.error('ca non presente nella lista delle ca, non posso verificare la revoca')
            print cert.get_issuer()
            
        bio = BIO.MemoryBuffer(data)
        signer = SMIME.SMIME()
        signer.pkey = pkey
        signer.x509 = cert

        # firmo il buffer
        try :
            pkcs7 = signer.sign(bio)
        except:
            return None

        # creo un buffere di uscita
        out = BIO.MemoryBuffer()
        pkcs7.write_der(out)

        return out.read()

    def verify(self, certmanager, data, self_signed=False):
        assert isinstance(certmanager, CertificateManager)
        
        p7_bio = BIO.MemoryBuffer(data)
        
        # carico il file p7m
        p7 = SMIME.PKCS7( 
            m2.pkcs7_read_bio_der(p7_bio._ptr()),
            1
        )
        
        # ottengo i firmatari del file
        cert = p7.get0_signers(X509.X509_Stack())
        # se non ci sono firmatari  
        if not len(cert):
            self._logger.error("nessun firmatario del file")
            return False
                
        signer = SMIME.SMIME()
        signer.set_x509_stack(cert)
        
        store = X509_Store()  # creo uno store che conterra' il certificato della CA
        
        if self_signed:  # se il certificato e' selfsigned
            store.add_cert(cert.pop())
        else:
            # ottengo il certificato della CA in base al campo
            # issuer del certificato contenuto nel p7
            cacert = certmanager.get_ca_certificate_x509(cert.pop())
            if cacert is None:  # se al momento non ho in memoria il certificato della CA
                self._logger.error("non ho trovato nessun certificato per la CA del certificato")
                return False
            
            store.add_cert(cacert)
        
        signer.set_x509_store(store)
            
        try:
            if self_signed:  # se il file e' autocertificato
                v = signer.verify(p7, data_bio=None, flags=SMIME.PKCS7_NOVERIFY)
            else:
                v = signer.verify(p7, data_bio=None)
        except SMIME.SMIME_Error, e:
            self._logger.error('smime error: ' + str(e))
            return False
        except SMIME.PKCS7_Error, e:
            self._logger.error('pkcs7 error: ' + str(e))
            return False

        if v is None:
            return False

        return True
    

