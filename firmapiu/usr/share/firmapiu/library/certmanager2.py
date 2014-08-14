from certlib2 import openssl_load_cert
from certlib2 import extract_crl_url
from certlib2 import extract_ocsp_url
from certlib2 import openssl_load_crl
from weblib2 import execute_download
from filelib import read_file 
from OpenSSL import crypto


class CertificateRevocationList(object):

    def __init__(self, data):
        assert isinstance(data, str)
        self.openssl_crl = openssl_load_crl(data)

    @property
    def openssl_crl(self):
        return self.openssl_crl

    @property
    def m2crypto_crl(self):
        return self.openssl_crl


class Certificate(object):

    def __init__(self, data):
        """
        Inizializza un oggetto di tipo Certificato
        :param data: il buffer contenente il certificato in formato DER o PEM
        :type data: str
        """
        assert isinstance(data, str)
        self.openssl_x509 = openssl_load_cert(data)
        self.subject = self.openssl_x509.get_subject()
        self.issuer = self.openssl_x509.get_issuer()
        self.crl_url = extract_crl_url(self.openssl_x509)
        self.ocsp_url = extract_ocsp_url(self.openssl_x509)

    def __str__(self):
        return crypto.dump_certificate(crypto.FILETYPE_PEM, self.openssl_x509)

    @property
    def m2crypto_cert(self):
        return self.m2crypto_x509

    @property
    def openssl_cert(self):
        return self.openssl_x509

    def get_crl(self):
        """
        Ottiene la CRL del certificato dall'url (la scarica dal web)
        :return:
        """
        if self.crl_url is None:
            return None

        crl_data = execute_download(self.crl_url)
        if crl_data is None:
            return None

        crl = CertificateRevocationList(crl_data)
        return crl


class CertificateStore(object):

    def __init__(self):
        self.certs = []

    def load_data(self, filename):
        data = read_file(filename)        
        certs = data
        for cert in certs:
            pass

    def save_data(self, filename):
        data = ''
        for cert in self.certs:
            data += cert.data()

    def get_cert_issuer(self, cert):
        """
        Restituisce il certificato del issuer (se presente nello store) del certificato passato come parametro
        :param cert:certificato da cui estrapolare l'issue
        :type cert: Certificate
        :return: certificato dell'issuer trovato nello store
        :rtype: None or Certificate
        """
        assert isinstance(cert, Certificate)

    def add_cert(self, cert):
        """
        Aggiunge un cetificato allo store
        :param cert: certificato da aggiungere
        :type cert: Certificate
        :return: l'esito dell'aggiunta del certificato
        :rtype: bool
        """
        assert isinstance(cert, Certificate)

    def get_all_certs(self):
        """
        Restituisce tutti i certificati dello store sotto forma di lista
        :return: lista di tutti i certificati
        :rtype list of Certificate
        """
        return []
