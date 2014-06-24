from M2Crypto import X509, BIO, m2, SMIME
import re
def prova():        
    x509 = X509.load_cert('/home/samuel/Scrivania/elencopubblico/ArubaPEC/TSA_AP_NG_TSA_1.der', X509.FORMAT_DER)
    
    assert isinstance(x509, X509.X509)
    
    print x509.get_issuer()
    print x509.get_subject()
    i = x509.get_ext_count() - 1
     
    while i >= 0:
        print "%s*****%s" % (x509.get_ext_at(i).get_name(), x509.get_ext_at(i).get_value())
        print "***************************************************************"
        i-=1
    
    print x509.get_serial_number()
    print x509.check_ca()
    return False
    

def prova2():
    with open('/home/samuel/Dropbox/progettoFirmaPiu/test/rfc3161.pdf.p7m') as f:
        data = f.read()
         
    p7_bio = BIO.MemoryBuffer(data)
         
    # carico il file p7m
    p7 = SMIME.PKCS7( 
        m2.pkcs7_read_bio_der(p7_bio._ptr()),
        1
    )
         
    # ottengo i firmatari del file
    cert = p7.get0_signers(X509.X509_Stack())
    # se non ci sono firmatari  
    if not len(cert):
        print 'no signer found'
     
    x509 = cert.pop()
    print x509.get_issuer()
    print x509.get_subject()
    i = x509.get_ext_count() - 1
      
    while i >= 0:
        print "%s*****%s" % (x509.get_ext_at(i).get_name(), x509.get_ext_at(i).get_value())
        print "***************************************************************"
        i-=1

    

if __name__ == '__main__':
    prova2()
