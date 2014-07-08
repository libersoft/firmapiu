from signlib import Signer
from timestamplib import Timestamper
from scardlib import SmartcardHolder
from certmanager import CertificateManager
from certmanager import add_cert_dir_to_certmanager
import localconfig
import filelib


class FirmapiuManager(object):
#    __single = None
    
    # metodo per l'implementazione di un singleton
#     def __new__(cls, *args, **kwargs):
#         if cls != type(cls.__single):
#             cls.__single = object.__new__(cls, *args, **kwargs)
#         return cls.__single
            
    def __init__(self):
        # TODO da controllare se config_filename non e' un file
#        if not isfunction(config_handler_function) or not isfunction(logger_write_function):
#            raise VariableNotFunctionException()
        self._scard_holder = None
        self._signer = None
        self._certmanager = None
        self._timestamper = None
    
    def __del__(self):
        print 'cleanup'
    
    def _lazy_init_timestamp(self, config, logger):
        if self._timestamper is None:
            self._timestamper = Timestamper(config, logger)
    
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
        if self._signer.verify(self._certmanager, data):
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
        
    def load_cert_dir(self, config, logger):
        self._lazy_init_sign(config, logger)
        
        add_cert_dir_to_certmanager(self._certmanager, localconfig.CERTIFICATE_DIR, logger)
        logger.status('cert %s dir loaded' % localconfig.CERTIFICATE_DIR)
