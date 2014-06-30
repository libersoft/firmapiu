import os

from MyRemoteTimestamper import MyRemoteTimestamper

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
        self.logger = logger

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
                self.logger.error('cert is revoked')
                return None
        except CACertificateNotFoundException:
            self.logger.error('ca non presente nella lista delle ca, non posso verificare la revoca')
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
            self.logger.error("nessun firmatario del file")
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
                self.logger.error("non ho trovato nessun certificato per la CA del certificato")
                return False
            
            store.add_cert(cacert)
        
        signer.set_x509_store(store)
            
        try:
            if self_signed:  # se il file e' autocertificato
                v = signer.verify(p7, data_bio=None, flags=SMIME.PKCS7_NOVERIFY)
            else:
                v = signer.verify(p7, data_bio=None)
        except SMIME.SMIME_Error, e:
            self.logger.error('smime error: ' + str(e))
            return False
        except SMIME.PKCS7_Error, e:
            self.logger.error('pkcs7 error: ' + str(e))
            return False

        if v is None:
            return False

        return True
    
    def timestamp(self, data):
        # ottengo il nome del server di timestamp
        tsa_url = self.config.get_timestamp_server()
        if tsa_url is None:
            return None
                
        # recupero username
        tsa_user = self.config.get_timestamp_username()
        if tsa_user is None:
            return None
        
        # recupero password
        tsa_pass = self.config.get_timestamp_password()
        if tsa_pass is None:
            return None
        
        remote_ts = MyRemoteTimestamper(
            url=tsa_url,
            certificate=None,  # viene controllato che la risposta sia giusta
            capath=None,  # Non e' usata dalla libreria
            cafile=None,  # Non e' usata dalla libreria
            username=tsa_user,
            password=tsa_pass,
            hashname='sha256',
            include_tsa_certificate=True  # serve perche la TSA di aruba lo richiede
        )
        
        res, errmsg = remote_ts.timestamp(
            data,
            digest=None,  # viene calcolato da programma
            # include_tsa_certificate, gia inserito nel costruttore
            nonce=None  # il nonce non e' richiesto da Aruba
        )

        if errmsg != '':
            self.logger.error(errmsg)
            return None
        
        return res
    
    def verify_timestamp(self, data, data_tsr):
        
        remote_ts = MyRemoteTimestamper(
            url=None,  # non usato nella verifica del timestamp
            #certificate=cert_buff,  # buffer contenente tutti i certificati di openssl
            certificate=None,  # buffer contenente tutti i certificati di openssl
            capath=None,  # non sono usati dalla libreria
            cafile=None,  # non sono usati dalla libreria
            username=None,  # non usato nella verifica del timestamp
            password=None,  # non usato nella verifica del timestamp
            hashname='sha256',
            include_tsa_certificate=True  # non usato nella verifica del timestamp
        )
        
        res, errmsg = remote_ts.check(
            tsr_buff=data_tsr,
            data=data,
            digest=None,  # viene calcolato dalla libreria
            nonce=None  # il nonce non e' richiesto da Aruba
        )
        
        if not res:
            self.logger.error(errmsg)
            return False
        
        return res
