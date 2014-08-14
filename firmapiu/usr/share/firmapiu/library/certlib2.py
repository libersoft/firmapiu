import re
import OpenSSL


_crlurl_re = re.compile('URI:(.*)')


def m2crypto_load_cert(data):
    return None


def openssl_load_cert(data):
    """
    Restituisce il certificato openssl del buffer passato
    :param data: buffer da cui legger
    :type data: str
    :return: il certificato
    :rtype: Openssl.crypto.X509 or None
    """
    return None


def openssl_load_crl(data):
    """
    Restituisce la crl letta dal buffer
    :param data: buffer da cui legger
    :type data: str
    :return: la crl
    :rtype: Openssl.crypto.CRL or None
    """
    return None


def extract_crl_url(cert):
    assert isinstance(cert, OpenSSL.crypto.X509)
    try:
        crl_str = cert.get_ext("crlDistributionPoints").get_value()
    except LookupError:  # non ho trovato l'estensione per la crl
        return None

    crl_str = crl_str.strip()
    match = _crlurl_re.search(crl_str)
    if match is None:  # non ho trovato l'url
        return None


def extract_ocsp_url(cert):
    assert isinstance(cert, OpenSSL.crypto.X509)


