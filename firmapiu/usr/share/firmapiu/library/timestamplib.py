from MyRemoteTimestamper import MyRemoteTimestamper
from loglib import Logger
from conflib import ConfigReader

class Timestamper(object):
    
    def __init__(self, config, logger):
        assert isinstance(logger, Logger)
        assert isinstance(config, ConfigReader)
        
        self.config = config
        self._logger = logger
    
    
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
            self._logger.error(errmsg)
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
            self._logger.error(errmsg)
            return False
        
        return res