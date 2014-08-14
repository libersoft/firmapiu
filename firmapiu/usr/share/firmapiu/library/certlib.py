import re
import StringIO
import requests
import ldap
import ldapurl
import M2Crypto
import OpenSSL
import socket


_newlines_re = re.compile(r'(\r\n|\r|\r)')
_crlurl_re = re.compile('URI:(.*)')


def _normalize_newlines(string):
    return _newlines_re.sub('\n', string)


def load_crl(buff):
    crl = _load_der_crl_buff(buff)
    if crl is not None:
        return crl
    
    crl = _load_pem_crl_buff(buff)
    if crl is not None:
        return crl
    
    return None

def load_certificate(buff):
    cert = _load_der_cert_buff(buff)
    if cert is not None:
        return cert
    
    cert = _load_pem_cert_buff(buff)
    if cert is not None:
        return cert
    
    return None


def _load_pem_crl_buff(buff):
    try:
        crl = OpenSSL.crypto.load_crl(OpenSSL.crypto.FILETYPE_PEM, buff)
    except:
        return None
    return crl


def _load_der_crl_buff(buff):
    try:
        crl = OpenSSL.crypto.load_crl(OpenSSL.crypto.FILETYPE_ASN1, buff)
    except:
        return None
    return crl


def _load_der_cert_buff(buff):
    try:
        cert = M2Crypto.X509.load_cert_string(buff, M2Crypto.X509.FORMAT_DER)
    except M2Crypto.X509.X509Error:
        return None
    return [cert]


def _load_pem_cert_buff(buff_str):
    cert_list = []
    cert_buff = ''
    buff = StringIO.StringIO(buff_str)
    
    for line in buff.readlines():
        line = _normalize_newlines(line)
        if line == '-----BEGIN CERTIFICATE-----\n':
            cert_buff = line
        else:
            cert_buff += line
              
        if line == '-----END CERTIFICATE-----\n':
            try :
                cert = M2Crypto.X509.load_cert_string(cert_buff, M2Crypto.X509.FORMAT_PEM)
                cert_list.append(cert)
            except:
                print 'failed to load cert:'
                print cert_buff
                
    return cert_list


def extract_crl_url(cert):
    assert isinstance(cert, M2Crypto.X509.X509)
    try:
        crl_str = cert.get_ext("crlDistributionPoints").get_value()
    except LookupError:  # non ho trovato l'estensione per la crl
        return None
    
    crl_str = crl_str.strip()
    match = _crlurl_re.search(crl_str)
    if match is None:  # non ho trovato l'url
        return None
    
    return match.group(1)

def extract_rev_list(crl):
    assert isinstance(crl, OpenSSL.crypto.CRL)
    return crl.get_revoked()


def obtain_crl(url):
    assert isinstance(url, str)
    data, errmsg = execute_download(url)
    if data is None:
        print errmsg
        return None
    return load_crl(data)

