#!/usr/bin/python
import pycurl
import StringIO


class WebRequest(object):
    def __init__(self, url, logger):
        if url is None or not len(url):
            raise AttributeError
        if logger is None:
            raise AttributeError

        self.curl_obj = pycurl.Curl()
        self.url = url  # TODO da controllare che venga inserito un url
        self.headers = []
        self.buffer_out = StringIO.StringIO()

        self.file_send = None
        self.logger = logger

        # setto l'url
        self.curl_obj.setopt(pycurl.URL, self.url)
        # setto il buffer di uscita
        self.curl_obj.setopt(pycurl.WRITEFUNCTION, self.buffer_out.write)

    def add_header(self, header_str):
        self.headers.append(header_str)

    def set_http_credential(self, http_username, http_password):
        self.curl_obj.setopt(pycurl.USERPWD, "%s:%s" % (http_username, http_password))

    def request(self, buff=None):
        
        if buff is not None:  # se nella richiesta invio qualcosa
            self.curl_obj.setopt(pycurl.POST, 1)
            buff_size = len(buff)
            self.curl_obj.setopt(pycurl.INFILESIZE, buff_size)
            self.headers.append("Content-Length: %d" % buff_size)  # e' necessario
            self.curl_obj.setopt(pycurl.POSTFIELDS, buff)

        # scrivo gli header nella richiesta
        self.curl_obj.setopt(pycurl.HTTPHEADER, self.headers)

        try:
            self.curl_obj.perform()
        except pycurl.error, errmsg:
            self.logger.error(errmsg)
            return None
        finally:
            self.curl_obj.close()

        return self.buffer_out.getvalue()

