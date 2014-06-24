import os
import platform
import shutil
import requests
from tempfile import NamedTemporaryFile
from tempfile import mkdtemp
from zipfile import ZipFile
import tarfile
import json
import conflib

LIBRARY_PATH = '/usr/local/lib'

to_extract = {
            '32': {
                'download': [
                    {
                        'url' : 'http://www.regione.toscana.it/documents/10180/595930/smart_card.zip',
                        'compression' : 'zip',
                        'rule': [
                              {'file': 'usr/local/lib/libgmp.so.3.4.2', 'symbolic_link': ['usr/local/lib/libgmp.so.3', 'usr/local/lib/libgmp.so'] },
                              {'file': 'usr/local/bin/siecapin', 'destination': '/usr/local/bin' },
                              {'file': 'usr/local/lib/libsiecacns.so' }
                        ]
                    },
                    {
                        'url' : 'http://www.regione.toscana.it/documents/10180/595930/smart_card.zip',
                        'compression' : 'zip',
                        'rule': [
                              {'file': 'usr/local/lib/libgmp.so.3.4.2', 'symbolic_link': ['usr/local/lib/libgmp.so.3', 'usr/local/lib/libgmp.so'] },
                              {'file': 'usr/local/bin/siecapin', 'destination': '/usr/local/bin' },
                              {'file': 'usr/local/lib/libsiecacns.so' }
                        ]
                    }
                
              ]
            },
            '64': {
                'download': [
                    {
                        'url' : 'http://www.regione.toscana.it/documents/10180/595930/smart_card.zip',
                        'compression' : 'zip',
                        'rule': [
                              {'file': 'usr/local/lib/libgmp.so.3.4.2', 'symbolic_link': ['usr/local/lib/libgmp.so.3', 'usr/local/lib/libgmp.so'] },
                              {'file': 'usr/local/bin/siecapin', 'destination': '/usr/local/bin' },
                              {'file': 'usr/local/lib/libsiecacns.so' }
                        ]
                    },
                    {
                        'url' : 'http://www.regione.toscana.it/documents/10180/595930/smart_card.zip',
                        'compression' : 'zip',
                        'rule': [
                              {'file': 'usr/local/lib/libgmp.so.3.4.2', 'symbolic_link': ['usr/local/lib/libgmp.so.3', 'usr/local/lib/libgmp.so'] },
                              {'file': 'usr/local/bin/siecapin', 'destination': '/usr/local/bin' },
                              {'file': 'usr/local/lib/libsiecacns.so' }
                        ]
                    }
                ]
            }
    }


def smart_extraction(to_extract):
    
    for ext in to_extract:
        if 'file' in ext:
            print ext['file']
        if 'destination' in ext:
            print ext['destination']
        if 'symbolic_link' in ext:
            print ext['symbolic_link']

class DriverManager:
    def __init__(self):
        self.tempdir = None
    
    def install(self):
        pass
    
    def remove(self):
        pass
    
    def __exit__(self):
        if self.tempdir is not None:
            os.unlink(self.tempdir)
    
def is_root():
    return os.getuid() == 0

def get_architecture():
    return platform.architecture()[0]

def download_to_temp_dir(url):
    tempdir = mkdtemp(prefix='firmapiu-')
    with NamedTemporaryFile(dir=tempdir, delete=False) as temp:
        filename = temp.name
        res = requests.get(url)
        temp.write(res.content)
        
    return filename

def clean_tempdir(filename):
    os.unlink(filename)
    
def extract_zip(filename, to_extract):
    if not os.access(filename, os.R_OK):
        print 'file %s not exists' % filename
        return False
    
    with ZipFile(filename) as zipfile:        
        for ext in to_extract:
            print "extracting %s" % ext
            try:
                source = zipfile.open(ext)
            except KeyError:  # ext non e' stato trovato nell'archivio
                print 'il file zip non contiene %s' % ext
                return False
            taget_path = os.path.join(LIBRARY_PATH, os.path.basename(ext))
            target = file(taget_path, 'w')
            try:
                shutil.copyfileobj(source, target)
                print 'change file permission'
                os.chmod(taget_path, 0755)
            except IOError:
                return False

    return True

def extract_all_zip(filename, destdir):
    with ZipFile(filename) as zipfile:
        zipfile.extractall(destdir)
        
    return True

def extract_tar(filename, to_extract):
    if not os.access(filename, os.R_OK):
        print 'file %s not exists' % filename
        return False
    
    with tarfile.open(filename) as tar:
        for ext in to_extract:
            print "extracting %s" % ext
            try:
                tar_info = tar.getmember(ext)
            except KeyError:  # il membro non e' stato trovato
                print 'il file tar non contiene %s' % ext
                return False
            
            taget_path = os.path.join(LIBRARY_PATH, os.path.basename(ext))
            target = file(taget_path, 'w')
            
            extfile = tar.extractfile(tar_info)
            shutil.copyfileobj(extfile, target)
            extfile.close()
    
    return True

def install_athena():
    if not is_root():
        return False
    
    url='http://www.regione.toscana.it/documents/10180/595930/smart_card.zip'
    arch = get_architecture()
    if arch == '32bit':
        to_extract = ('x86/libaseCnsP11.so',)
    elif arch == '64bit':
        to_extract = ('x64/libaseCnsP11.so',)
    else:
        return False 
    
    filename = download_to_temp_dir(url)
    if extract_zip(filename, to_extract):
        return True
    else:
        return False
        
def install_cardos():
    if not is_root():
        return False
    
    arch = get_architecture()

    if arch == '32bit':
        url = 'http://www.provincia.bz.it/cartaservizi/downloads/linux/cardos.tar.gz'
    elif arch == '64bit':
        url = 'http://www.provincia.bz.it/cartaservizi/downloads/linux/cardos64.tar.gz'
    else:
        return False
    
    to_extract = (
        #'usr/local/bin/siecapin',
        'usr/local/lib/libgmp.so.3.4.2',
        'usr/local/lib/libgmp.so.3',
        'usr/local/lib/libgmp.so',
        'usr/local/lib/libces.so.1.1.5',
        'usr/local/lib/libces.so.1',
        'usr/local/lib/libces.so',
        'usr/local/lib/libsiecacrd.so',
        'usr/local/lib/libsiecadlg.so',
        'usr/local/lib/libsiecap11.so',
        'usr/local/lib/libsiecap15.so'
        'usr/local/lib/libsiecacns.so'
        #'etc/sieca.conf'
    )
    
    filename = download_to_temp_dir(url)
    extract_tar(filename, to_extract)
    return True
    
def install_incard():
    if not is_root():
        return False
    
    url = 'https://www.pec.it/Download/Software/FirmaDigitale/MU_INCARD1290_LINUX.zip'
    
    arch = get_architecture()
    
    if arch == '32bit':
        to_extract = (
            'libbit4ipki.so',
            'libbit4ipki.so.conf',
#            'libbit4ipki.so_pin.py'
        )
    elif arch == '64bit':
        to_extract = (
            'x64/libbit4ipki.so',
            'x64/libbit4ipki.so.conf',
#            'x64/libbit4ipki.so_pin.py'
        )
    else:
        return False
    
    filename = download_to_temp_dir(url)
    extract_zip(filename, to_extract)
    
    return True

def install_oberthur():
    if not is_root():
        return False
    
    url = 'http://www.pec.it/Download/Software/FirmaDigitale/MU_OBERTHUR1283_LINUX.zip'
    
    arch = get_architecture()
    
    if arch == '32bit':
        to_extract = (
            '32/libbit4opki.so',
            '32/libbit4opki.so.conf'
        )
    elif arch == '64bit':
        to_extract = (
            '64/libbit4opki.so',
            '64/libbit4opki.so.conf'
        )
    else:
        return False
    
    filename = download_to_temp_dir(url)
    extract_zip(filename, to_extract)
    
    return True
    

def download_certificate():
    # se la directory non esiste scarico i certificati
    if not os.path.exists('/etc/firmapiu/certs/'):
        filename = download_to_temp_dir('http://www.cnipa.gov.it/site/_files/LISTACER_20140415.zip.p7m')
        extract_all_zip(filename, '/etc/firmapiu/certs')
    else:
        pass
    
def download_crl():
    if not os.path.exists('/etc/firmapiu/crl/'):
        filename = download_to_temp_dir('http://www.cnipa.gov.it/site/_files/LISTACER_20140415.zip.p7m')
        extract_all_zip(filename, '/etc/firmapiu/certs')
    else:
        pass
    
def init_certificate(config,  on_ca_path_not_exist, on_crl_path_not_exist):
    assert isinstance(config, conflib.ConfigReader)
    ca_cert_path = config.get_ca_certificate_path()
    if ca_cert_path is None:
        return
    crl_path = config.get_crl_path()
    if crl_path is None:
        return
    
    if not os.path.exists(ca_cert_path):
        on_ca_path_not_exist(ca_cert_path)
    
    if not os.path.exists(crl_path):
        on_crl_path_not_exist(crl_path)
        
    


if __name__ == '__main__':
    download_certificate()

    

        
