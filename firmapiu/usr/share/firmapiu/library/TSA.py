#!/usr/bin/python
from WebRequest import WebRequest
from TimeStampRequestPacker import TimestampRequestPacker


class TimestampClient(object):
    def __init__(self, config, logger):
        if config is None:
            raise AttributeError
        if logger is None:
            raise AttributeError
        self.config = config  # utile per estrapolare username e password
        self.logger = logger

    def send_timestamp_query(self, filename):
        # non controllo se mi restituisce eccezione perche' il self.logger non puo essere None
        tst = TimestampRequestPacker(self.logger)
        
        # creo la dichiesta decodificata in DER
        req_buff = tst.pack_der(filename)
        if req_buff is None:
            self.logger.error('no timestamp request create')
            return None
        # creo l'oggetto per la richiesta via web
        web = WebRequest("https://servizi.arubapec.it/tsa/ngrequest.php", self.logger)
        
        # recupero username
        tsa_user = self.config.get_timestamp_username()
        if tsa_user is None:
            return None
        
        # recupero password
        tsa_pass = self.config.get_timestamp_password()
        if tsa_pass is None:
            return None
        
        # setto le credenziali
        web.set_http_credential(tsa_user, tsa_pass)
        # setto il buffer da inviare

        # eseguo la richiesta
        data = web.request(buff=req_buff)

        return data  # puo essere None
