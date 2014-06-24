import os

from MyRemoteTimestamper import MyRemoteTimestamper

from M2Crypto import SMIME
from M2Crypto import X509
from M2Crypto import BIO
from M2Crypto import m2

from loglib import Logger
from conflib import ConfigReader
from holder import Holder

from certlib import CRL_Store
from certlib import CACertificateStore
from M2Crypto.X509 import X509_Store

class Signer(object):
    
    def __init__(self, config, logger):
        assert isinstance(logger, Logger)
        assert isinstance(config, ConfigReader)
        
        self.config = config
        self.logger = logger
        self.ca_store = None
        self.crl_store = None

    def load_ca_store(self):
        store_path = self.config.get_ca_certificate_path()
        
        if store_path is None:
            self.logger.error('ca path is None')
            return False
    
        if not os.path.exists(store_path):
            self.logger.error('%s does not exist' % store_path)
            return False

        ca_store = CACertificateStore()
    
        added = 0
        for root, _dirs, files in os.walk(store_path, topdown=False, onerror=None, followlinks=False):
            for name in files:
                added += ca_store.add_ca_certificate_file(os.path.join(root, name))
        
        if added:
            self.ca_store = ca_store
        
        self.logger.status('caricate %d cetificati' % added)
        return True

    def load_crl_store(self):    
        crl_path = self.config.get_crl_path()
        
        if crl_path is None:
            self.logger.error('crl path is None')
            return False
            
        if not os.path.exists(crl_path):
            self.logger.error('%s does not exist' % crl_path)
            return False
    
        crl_store = CRL_Store()
    
        added = 0
        for root, _dirs, files in os.walk(crl_path, topdown=False, onerror=None, followlinks=False):
            for name in files:
                added += crl_store.add_crl_file(os.path.join(root, name))
    
        if added:
            self.crl_store = crl_store
        
        self.logger.status('numero di file crl caricati: %d' % added)
        return True

    def sign(self, holder, data):
        assert isinstance(holder, Holder)
                
        # ottengo la chiave privata dall'holder
        pkey = holder.get_private_key()
        # ottengo il certificato dall'holder
        cert = holder.get_certificate()

        if pkey is None or cert is None:
            return None
                
        # TODO controllare se il certificato non e' stato revocato
        self.ca_store.get_ca_cert(cert)    
            
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

    def sign_file(self, holder, filename):
        assert isinstance(holder, Holder)
        
        if not os.access(filename, os.R_OK):
            return None
        
        data = open(filename).read()
        
        return self.sign(holder, data)

    def verify(self, data, self_signed=False):
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
            ca_cert = self.ca_store.get_ca_cert(cert.pop())
            if ca_cert is None:  # se al momento non ho in memoria il certificato della CA
                print "non ho trovato nessun certificato per la CA del certificato"  # TODO 
            else:
                store.add_cert(ca_cert)
        
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

    def verify_file(self, filename, self_signed=False):        
        if not os.access(filename, os.R_OK):
            return False
        
        data = open(filename).read()
        
        return self.verify(data, self_signed)
    
    def timestamp_file(self, filename):
        if not os.access(filename, os.R_OK):
            return None
        
        data = open(filename).read()
        
        return self.timestamp(data)

    
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
    
    def verify_timestamp_file(self, filename, tsr_filename):
        if not os.access(filename, os.R_OK):
            return False
        if not os.access(tsr_filename, os.R_OK):
            return False
        
        data = open(filename).read()
        data_tsr = open(tsr_filename).read()
        
        return self.verify_timestamp(data, data_tsr)
