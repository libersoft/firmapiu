import os
import sqlite3
from storm.locals import create_database
from storm.locals import Store
from storm.locals import Unicode
from storm.locals import DateTime
from storm.locals import Int
from storm.locals import Reference
from storm.locals import ReferenceSet
import M2Crypto
from certlib import extract_crl_url
from certlib import obtain_crl
from certlib import extract_rev_list
from certlib import load_certificate


class CACertificateNotFoundException(Exception):
    pass


class CertificateManager(object):
    
    def __init__(self, db_filename):
        database = create_database('sqlite:%s' % db_filename)
        self.store = Store(database)
        try:
            if self.store.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crl';").get_one() is None:
                self.store.execute(CREATE_DB_CRL)
            if self.store.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ca_certificate';").get_one() is None:
                self.store.execute(CREATE_DB_CA_CERTIFICATE)
            if self.store.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='revoke';").get_one() is None:
                self.store.execute(CREATE_DB_REVOKE)
        except sqlite3.OperationalError:
            print 'errore'
    
    def __del__(self):
        print 'execute commit'
        self.store.commit()
    
    def _add_crl(self,crl_url):
        assert isinstance(crl_url, str)
        cacrl = self.store.find(CRL, CRL.crl_url == unicode(crl_url)).one()
        if cacrl is None:
            cacrl = CRL(crl_url)
            crl = obtain_crl(crl_url)  # ottengo la crl
            if crl is None:  # non ho trovato nessuna crl
                print 'non sono riuscito ad ottenere la lista revocati'
                return False
            
            rev_list = extract_rev_list(crl)  # TODO da controllare perche' restituisce None
            if rev_list is None:
                print 'non sono riuscito ad ottenere l\'oggetto crl'
                return False
            
            for rev in rev_list:  # aggiungo i seriali revocati
                revoke = Revoke(rev.get_serial())
                revoke.crl = cacrl
                self.store.add(revoke)
            self.store.add(cacrl)

        return cacrl
    
    def add_ca_certificate(self, cert):
        assert isinstance(cert, M2Crypto.X509.X509)
        if cert.check_ca() == 0:
            return False

        x509_subject = cert.get_subject()
        x509_subject_hash = x509_subject.as_hash()

        cacert = self.store.find(CACertificate, CACertificate.cert_hash == unicode(x509_subject_hash)).one()
        if cacert is None:  # se il certificato non e' presente
            cacert = CACertificate(str(x509_subject_hash), cert.as_pem())
            # cerco di trovare l'url della crl
            crl_url = extract_crl_url(cert)
            
            if crl_url is not None:
                cacrl = self._add_crl(crl_url)
                cacert.crl = cacrl
            self.store.add(cacert)
            try:
                self.store.flush()
            except sqlite3.IntegrityError, e:
                print 'errore sqlite', e
                return False
        else:
            print "certificate of:", cert.get_subject().as_text(), "already present"
            return False
    
    def _get_ca_certificate(self, cert):
        assert isinstance(cert, M2Crypto.X509.X509)
        x509_issuer = cert.get_issuer()
        x509_issuer_hash = x509_issuer.as_hash()
        
        cacert = self.store.find(CACertificate, CACertificate.cert_hash == unicode(x509_issuer_hash)).one()
        if cacert is None:
            return None
        return cacert
    
    def get_ca_certificate_x509(self, cert):
        assert isinstance(cert, M2Crypto.X509.X509)
        cacert = self._get_ca_certificate(cert)
        if cacert is None:
            return None
        x509_cert = load_certificate(str(cacert.cert_data))
        if not len(x509_cert):
            return None
        
        return x509_cert[0]
        
    def is_revoked(self, cert):
        assert isinstance(cert, M2Crypto.X509.X509)
        cacert = self._get_ca_certificate(cert)
        if cacert is None:  # se non trovo nessuna ca per quel certificato
            raise CACertificateNotFoundException()
        for rev in cacert.crl.revokes:
            if rev.rev_serial == cert.get_serial_number():
                return True
        return False
        
class CRL(object):
    __storm_table__ = "crl"
    crl_url = Unicode(primary=True)
    
    def __init__(self, crl_url):
        self.crl_url = unicode(crl_url) 


class Revoke(object):
    __storm_table__ = "revoke"
    
    id = Int(primary=True)
    rev_serial = Unicode()
    rev_date = DateTime()
    
    crl_url = Unicode()
    crl = Reference(crl_url, CRL.crl_url)
    
    def __init__(self, serial):
        self.rev_serial = unicode(serial)
        self.rev_date = None

    

class CACertificate(object):
    __storm_table__ = "ca_certificate"
    
    cert_hash = Unicode(primary=True)
    cert_data = Unicode()
    
    crl_url = Unicode()
    crl = Reference(crl_url, CRL.crl_url)
    
    def __init__(self, hash_data, data):
        assert isinstance(hash_data, str)
        assert isinstance(data, str)
        self.cert_hash = unicode(hash_data)
        self.cert_data = unicode(data)
    
    
CRL.revokes = ReferenceSet(CRL.crl_url, Revoke.crl_url)
CRL.cacerts = ReferenceSet(CRL.crl_url, CACertificate.crl_url)
    
CREATE_DB_CRL = """
CREATE TABLE crl (
    crl_url VARCHAR PRIMARY KEY
);
"""
CREATE_DB_CA_CERTIFICATE = """
CREATE TABLE ca_certificate (
    cert_hash VARCHAR PRIMARY KEY,
    cert_data VARCHAR,
    crl_url INTEGER,
    FOREIGN KEY(crl_url) REFERENCES crl(url)
);
"""
CREATE_DB_REVOKE = """
CREATE TABLE revoke (
    id INTEGER PRIMARY KEY,
    rev_serial VARCHAR,
    rev_date DATETIME,
    crl_url INTEGER,
    FOREIGN KEY(crl_url) REFERENCES crl(url)
);
"""

def add_cert_dir_to_certmanager(certmanager, dirpath):
    assert isinstance(certmanager, CertificateManager)
    assert isinstance(dirpath, str)
    
    for root, _dirs, files in os.walk(dirpath):
        for name in files:
            path = os.path.join(root, name)
            print path
            with open(path) as f:
                data = f.read()
            cert_list = load_certificate(data)
            for cert in cert_list:
                certmanager.add_ca_certificate(cert) 

