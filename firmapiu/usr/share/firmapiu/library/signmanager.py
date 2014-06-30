from inspect import isfunction
from signlib import Signer
from scardlib import SmartcardHolder
from conflib import ConfigFileReader
from loglib import Logger
from certmanager import CertificateManager
from certmanager import add_cert_dir_to_certmanager
import localconfig
import filelib


class VariableNotFunctionException(Exception):
    pass


class SignManager(object):
#    __single = None
    
    # metodo per l'implementazione di un singleton
#     def __new__(cls, *args, **kwargs):
#         if cls != type(cls.__single):
#             cls.__single = object.__new__(cls, *args, **kwargs)
#         return cls.__single
            
    def __init__(self, config_handler_function, logger_write_function):
        # TODO da controllare se config_filename non e' un file
#        if not isfunction(config_handler_function) or not isfunction(logger_write_function):
#            raise VariableNotFunctionException()
        self.logger = Logger(logger_write_function)
        self.config_reader = ConfigFileReader(localconfig.CONFIG_FILE, config_handler_function, self.logger)
        self.scard_holder = SmartcardHolder(self.config_reader, self.logger)
        self.signer = Signer(self.config_reader, self.logger)
        self.certmanager = CertificateManager(localconfig.DATABASE_FILE)
    
    def __del__(self):
        print 'cleanup'
    
    def sign(self, filename):
        data = filelib.read_file(filename)
        if data is None:
            self.logger.error('failed to read %s' % filename)
            return
        
        signed_data = self.signer.sign(self.scard_holder, self.certmanager, data)
        if signed_data is None:
            self.logger.error('failed to sign file %s' % filename)
            return
        
        filelib.write_file('%s.p7m' % filename, signed_data)
        self.logger.status('file %s firmato correttamente' % filename)
    
    def verify(self, filename):
        data = filelib.read_file(filename)
        if self.signer.verify(self.certmanager, data):
            self.logger.status('file verificato %s correttamente' % filename)
        else:
            self.logger.status('il file %s non ha superato la verifica' % filename)
        
    def load_cert_dir(self):
        add_cert_dir_to_certmanager(self.certmanager, localconfig.CERTIFICATE_DIR)
        self.logger.status('cert %s dir loaded' % localconfig.CERTIFICATE_DIR)


def handler(*args):
    print args
    return None
        
if __name__ == '__main__':
    filename = '/home/samuel/Scaricati/prova.txt'
    s = SignManager(handler, handler)
    s.load_cert_dir()
    s.sign(filename)
