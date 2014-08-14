from signlib import Signer
from timestamplib import Timestamper
from scardlib import SmartcardHolder
from certmanager import CertificateManager
import localconfig
import filelib


class FirmapiuManager(object):
    def __init__(self):
        self._scard_holder = None
        self._signer = None
        self._certmanager = None
        self._timestamper = None
    
    def __del__(self):
        print 'FirmapiuManager __del__'
    
    def cleanup(self):
        if self._certmanager is not None:
            self._certmanager.cleanup()
        print 'FirmapiuManager cleanup'
    
    def _lazy_init_timestamp(self, config, logger):
        if self._timestamper is None:
            self._timestamper = Timestamper(config, logger)
    
    def _lazy_init_certificate(self, config, logger):
        if self._certmanager is None:
            self._certmanager = CertificateManager(localconfig.DATABASE_FILE)
    
    def _lazy_init_sign(self, config, logger):
        if self._scard_holder is None:
            self._scard_holder = SmartcardHolder(config, logger)

        if self._signer is None:
            self._signer = Signer(config, logger)
            
        if self._certmanager is None:
            self._certmanager = CertificateManager(localconfig.DATABASE_FILE)
        
    def sign(self, filename, config, logger):
        self._lazy_init_sign(config, logger)
        
        data = filelib.read_file(filename)
        if data is None:
            logger.error('failed to read %s' % filename)
            return
        
        signed_data = self._signer.sign(self._scard_holder, self._certmanager, data)
        if signed_data is None:
            logger.error('failed to sign file %s' % filename)
            return
        
        filelib.write_file('%s.p7m' % filename, signed_data)
        logger.status('file %s firmato correttamente' % filename)
    
    def verify(self, filename, config, logger):
        self._lazy_init_sign(config, logger)
        
        data = filelib.read_file(filename)
        if self._signer.verify(self._certmanager, data, self_signed=True):
            logger.status('file verificato %s correttamente' % filename)
        else:
            logger.status('il file %s non ha superato la verifica' % filename)
            
    def timestamp(self, filename, config, logger):
        self._lazy_init_timestamp(config, logger)
        
        data = filelib.read_file(filename)
        if data is None:
            logger.error('failed to read %s' % filename)
            return
        
        timestamp_data = self._timestamper.timestamp(filename)
        if timestamp_data is None:
            logger.error('failed to obtain timestamp for file %s' % filename)
            return
        
        filelib.write_file('%s.p7m' % filename, timestamp_data)
        logger.status('file %s firmato correttamente' % filename)
    
    def timestamp_verify(self, filename, config, logger):
        logger.status('timestamp verificato')
  
    def show_certs(self, config, logger):
        pass
        
    def load_cert(self, filename, config, logger):
        self._lazy_init_certificate(config, logger)
        self._certmanager.add_cert_to_certmanager(filename, logger)
        
    def load_cert_dir(self, config, logger):
        self._lazy_init_sign(config, logger)
        self._certmanager.add_cert_dir_to_certmanager(localconfig.CERTIFICATE_DIR, logger)
        logger.status('cert %s dir loaded' % localconfig.CERTIFICATE_DIR)
