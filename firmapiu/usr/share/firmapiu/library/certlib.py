import os
import re
import StringIO
import requests
import ldap
import ldapurl
import M2Crypto
import OpenSSL
import socket

request_timeout = 5


def test_ldap_connection(fullurl):
    try:
        host = fullurl.split(':')
        if len(host) == 1:
            s = socket.create_connection((host[0], 389), timeout=request_timeout)
        elif len(host) == 2:
            s = socket.create_connection((host[0], host[1]), timeout=request_timeout)
        s.close()
        return True
    except socket.timeout:
        return False
    except socket.gaierror:
        return False


def execute_download(url):
    if url.startswith('http://'):
        return http_download(url)
    elif url.startswith('https://'):
        return https_download(url)
    elif url.startswith('ldap://') or url.startswith('LDAP://'):
        return ldap_download(url)
        #return None, 'ldap not implemented'
    else:
        return None, 'dowload url not recognized'

def https_download(url):
    try:
        return http_download(url)
    except requests.exceptions.SSLError:  # errore ssl nel server
        return http_download(url, verify=False)

def http_download(url, verify=True):
    try:
        res = requests.get(url, timeout=request_timeout, verify=verify)
        if res.status_code == 200:
            return res.content, ''
        else:
            return None, '%d bad response code' % res.status_code 
    except requests.exceptions.Timeout:
        return None, 'http timeout'

def ldap_download(url):
    url = url.replace('LDAP', 'ldap')
    if ldapurl.isLDAPUrl(url):
        try:
            ldap_url = ldapurl.LDAPUrl(url)
        except ValueError, e:
            return None, e
        try:
            if not test_ldap_connection(ldap_url.hostport):
                return None, 'test connection failed'
            l = ldap.initialize('ldap://%s' % ldap_url.hostport)
            
            l.simple_bind()
            try:
                lis = l.search_st(ldap_url.dn, ldap.SCOPE_BASE, timeout=request_timeout)
                if lis is None:
                    return None, 'ldap search failed'
            
                lis = lis[0][1]
                if lis.has_key('certificateRevocationList'):
                    return lis['certificateRevocationList'][0], ''
                elif lis.has_key('certificateRevocationList;binary'):
                    return lis['certificateRevocationList;binary'][0], ''
                else:
                    return None, 'ldap no certificateRevocationList found'
            except ldap.TIMEOUT:
                return None, 'ldap timeout'
                
        except ldap.LDAPError, e:
            return None, 'ldap error: %s' % e
    else:
        return None, 'no ldap url'
    

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


def extract_crl_uri(cert):
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


class NoCACertificateException(Exception):
    pass


class CACertificateNotFoundException(Exception):
    pass


class CACertificate(object):
    
    def __init__(self, cert, crldict):
        assert isinstance(cert, M2Crypto.X509.X509)
        assert isinstance(crldict, CRLDict)
        
        self.certificate = cert
        self.crl = None
        if cert.check_ca() == 0:
            raise NoCACertificateException()
        crl_url = extract_crl_uri(cert)  # se l'url non e' stato trovato e' None
        if crl_url is not None:
            crl = crldict.get_crl(crl_url)
            if crl is None:  # se il certificato non e' nel dizionario lo aggiungo
                crl = CRL(crl_url)
                crldict.add_crl(crl)
            self.crl = crl
        
    def get_certificate(self):
        return self.certificate
    
    def get_crl(self):
        return self.crl

        
class CRL(object):
    
    def __init__(self, url):
        assert isinstance(url, str)
        self.url = url
        self.revoked = None
        
        #print 'try to get crl for url', url
        data, errmsg = execute_download(url)
        if data is not None:
            crl = load_crl(data)
            if crl is not None:
                self.revoked = crl.get_revoked()
                #print "crl for %s added" % url
            else:
                print 'failed to parse crl', url 
        else:
            print 'failed to download url "%s":' % url, errmsg 
        
    def get_url(self):
        return self.url
    
    def is_revoked(self, cert):
        if self.url is None:
            print 'non posso verificare senza un url'
            return False
        if self.revoked is None:
            print 'non posso verificare senza la lista revocati'
            return False
        
        assert isinstance(cert, M2Crypto.X509.X509)
        for rev in self.revoked:
            if rev.get_serial() == cert.get_serial_number():
                return True
        return False
            
        
        
class CACertificateDict(object):
    
    def __init__(self):
        self.dict = {}
        
    def add_ca_certificate(self, ca_cert):
        assert isinstance(ca_cert, CACertificate)
        subj = ca_cert.get_certificate().get_subject()
        if self.dict.has_key(subj):  # se e' gia presente del dizionario
            return False
        self.dict[subj] = ca_cert
        return True
        
    def get_ca_certificate(self, cert):
        assert isinstance(cert, M2Crypto.X509.X509)
        subj = cert.get_subject()
        if not self.dict.has_key(subj):
            return None
        return self.dict[subj]
    
    def is_revoked(self, cert):
        assert isinstance(cert, M2Crypto.X509.X509)
        ca_cert = self.get_ca_certificate(cert)
        if ca_cert is None:  # non posso verificare senza una certificato di una CA
            raise CACertificateNotFoundException()
        ca_crl = ca_cert.get_crl()  # non puo' essere None
        return ca_crl.is_revoked(cert)

        
        
class CRLDict(object):
    
    def __init__(self):
        self.dict = {}
        
    def get_crl(self, url):
        if url is None:
            return None
        if not self.dict.has_key(url):
            return None
        return self.dict[url]
        
    def add_crl(self, crl):
        assert isinstance(crl, CRL)
        if self.dict.has_key(crl.get_url()):  # se e' gia contenuta nel dizionario
            return False
        self.dict[crl.get_url()] = crl
        return True

def load_certficate_path(dirpath):
    cad = CACertificateDict()
    cd = CRLDict()
    
    for root, _dirs, files in os.walk(dirpath):
        for name in files:
            path = os.path.join(root, name)
            with open(path) as f:
                data = f.read()
            cert_list = load_certificate(data)
            for cert in cert_list:
                ca_cert = CACertificate(cert, cd)
                cad.add_ca_certificate(ca_cert)  

    return cad, cd

if __name__ == "__main__":
    load_certficate_path('/home/samuel/Scaricati/elencopubblico')
