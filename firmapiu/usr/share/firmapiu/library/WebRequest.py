#!/usr/bin/python
import os
import sys
import pycurl
import StringIO
import logging


class WebRequest(object):
    def __init__(self, url=None):
        self.curl_obj = pycurl.Curl()
        self.url = url
        self.headers = []
        self.buffer_out = StringIO.StringIO()
        self.file_send = None
        self.file_send_size = 0
        self.file_send_buff = None

    def add_header(self, header_str):
        self.headers.append(header_str)

    def set_content_type(self, type_str):
        self.headers.append("Content-Type: %s" % type_str)

    def set_file_to_send(self, filename):
        if os.path.isfile(filename):
            self.file_send = filename
            self.file_send_size = os.path.getsize(self.file_send)

    def set_content_length(self, size):
        self.headers.append("Content-Length: %d" % size)  # e' necessario

    def set_http_credential(self, http_username, http_password):
        self.curl_obj.setopt(pycurl.USERPWD, "%s:%s" % (http_username, http_password))

    def request(self):
        self.curl_obj.setopt(pycurl.URL, self.url)  # setto l'url
        self.curl_obj.setopt(pycurl.WRITEFUNCTION, self.buffer_out.write)  # setto il buffer di uscita

        if self.file_send:  # se e' stato settato un file da inviare
            self.curl_obj.setopt(pycurl.POST, 1)
            self.file_send_buff_ = open(self.file_send, "rb")  # apro il file in lettura
            self.headers.append("Content-Length: %d" % self.file_send_size)  # e' necessario
            self.curl_obj.setopt(pycurl.INFILESIZE, self.file_send_size)  # aggiungo la grandezza del file
            self.curl_obj.setopt(pycurl.READFUNCTION, self.file_send_buff.read)  # specifico la funzione di lettura

        if len(self.headers):  # se esistone degli header
            self.curl_obj.setopt(pycurl.HTTPHEADER, self.headers)
        else:
            logging.debug("nessun header inserito")

        try:
            self.curl_obj.perform()
        except pycurl.error, errmsg:
            logging.error(errmsg)
            return None
        finally:
            self.curl_obj.close()

        data = self.buffer_out.getvalue()
        return data


def main():
    req = WebRequest(url="http://www.google.com")
    print req.request()
    return 0

if __name__ == "__main__":
    sys.exit(main())
