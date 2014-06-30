import hashlib
import urllib2
import base64
import socket

import M2Crypto.X509 as X509
from pyasn1.type import univ
from pyasn1.error import PyAsn1Error
from pyasn1.codec.der import encoder, decoder
from pyasn1_modules import rfc2459

import rfc3161
from rfc3161.api import get_hash_from_oid, get_hash_class_from_oid, id_attribute_messageDigest
# from rfc3161.api import check_timestamp as rfc3161_check_timestamp
from rfc3161 import get_hash_oid, TimestampingError


def check_timestamp(tsr_buff, certificate, data=None, digest=None, hashname=None, nonce=None):
    '''
    adattatore usato per prendere parametri diversi come input
    '''
    tsr, substrate = decoder.decode(tsr_buff, asn1Spec=rfc3161.TimeStampResp())
    tst = tsr.time_stamp_token
    if substrate:
            return False, 'Extra data returned'
    # return rfc3161_check_timestamp(tst, certificate, data, digest, hashname, nonce)
    hashname = hashname or 'sha1'
    hashobj = hashlib.new(hashname)
    if digest is None:
        if not data:
            raise ValueError("check_timestamp requires data or digest argument")
        hashobj.update(data)
        digest = hashobj.digest()

    if not isinstance(tst, rfc3161.TimeStampToken):
        tst, substrate = decoder.decode(tst, asn1Spec=rfc3161.TimeStampToken())
        if substrate:
            return False, "extra data after tst"
    signed_data = tst.content
    if certificate != "":
        try:
            certificate = X509.load_cert_string(certificate, X509.FORMAT_PEM)
        except:
            certificate = X509.load_cert_string(certificate, X509.FORMAT_DER)
    else:
        return False, "missing certificate"
    if nonce is not None and int(tst.tst_info['nonce']) != int(nonce):
        return False, 'nonce is different or missing'
    # check message imprint with respect to locally computed digest
    message_imprint = tst.tst_info.message_imprint
    if message_imprint.hash_algorithm[0] != get_hash_oid(hashname) or \
        str(message_imprint.hashed_message) != digest:
            return False, 'Message imprint mismatch'
            
    if not len(signed_data['signerInfos']):
        return False, 'No signature'
    # We validate only one signature
    signer_info = signed_data['signerInfos'][0]
    # check content type
    if tst.content['contentInfo']['contentType'] != rfc3161.id_ct_TSTInfo:
        return False, "Signed content type is wrong: %s != %s" % (
            tst.content['contentInfo']['contentType'], rfc3161.id_ct_TSTInfo)

    # check signed data digest
    content = str(decoder.decode(str(tst.content['contentInfo']['content']),
        asn1Spec=univ.OctetString())[0])
    print content
    # if there is authenticated attributes, they must contain the message
    # digest and they are the signed data otherwise the content is the
    # signed data
    if len(signer_info['authenticatedAttributes']):
        authenticated_attributes = signer_info['authenticatedAttributes']
        signer_digest_algorithm = signer_info['digestAlgorithm']['algorithm']
        print signer_digest_algorithm
        signer_hash_class = get_hash_class_from_oid(signer_digest_algorithm)
        print signer_hash_class
        signer_hash_name = get_hash_from_oid(signer_digest_algorithm)
        print signer_hash_name
        content_digest = signer_hash_class(content).digest()
        print signer_hash_class(content).hexdigest()
        for authenticated_attribute in authenticated_attributes:
            if authenticated_attribute[0] == id_attribute_messageDigest:
                try:
                    signed_digest = str(decoder.decode(str(authenticated_attribute[1][0]),
                            asn1Spec=univ.OctetString())[0])
                    if signed_digest != content_digest:
                        return False, 'Content digest != signed digest'
                    else:
                        print 'ok'
                    s = univ.SetOf()
                    for i, x in enumerate(authenticated_attributes):
                        s.setComponentByPosition(i, x)
                    signed_data = encoder.encode(s)
                    break
                except PyAsn1Error:
                    raise
                    pass
        else:
            return False, 'No signed digest'
    else:
        signed_data = content

    # check signature
    signature = signer_info['encryptedDigest']
    pub_key = certificate.get_pubkey()
    pub_key.reset_context(signer_hash_name)
    pub_key.verify_init()
    pub_key.verify_update(signed_data)
    if pub_key.verify_final(str(signature)) != 1:
        return False, 'Bad signature'
    return True, ''
    
    
class MyRemoteTimestamper(rfc3161.RemoteTimestamper):
    
    def check(self, tsr_buff, data=None, digest=None, nonce=None):
        return check_timestamp(tsr_buff, digest=digest, data=data, nonce=nonce,
                certificate=self.certificate, hashname=self.hashname)
    
    def __call__(self, data=None, digest=None, include_tsa_certificate=None, nonce=None):
        '''
        classe sovrascritta per modificare alcune impostazioni della classe
        '''
        algorithm_identifier = rfc2459.AlgorithmIdentifier()
        algorithm_identifier.setComponentByPosition(0, get_hash_oid(self.hashname))
        message_imprint = rfc3161.MessageImprint()
        message_imprint.setComponentByPosition(0, algorithm_identifier)
        hashobj = hashlib.new(self.hashname)
        if data:
            hashobj.update(data)
            digest = hashobj.digest()
        elif digest:
            assert len(digest) == hashobj.digest_size, 'digest length is wrong'
        else:
            raise ValueError('You must pass some data to digest, or the digest')
        message_imprint.setComponentByPosition(1, digest)
        request = rfc3161.TimeStampReq()
        request.setComponentByPosition(0, 'v1')
        request.setComponentByPosition(1, message_imprint)
        if nonce is not None:
            request.setComponentByPosition(3, int(nonce))
        request.setComponentByPosition(4, include_tsa_certificate if include_tsa_certificate is not None else self.include_tsa_certificate)
        binary_request = encoder.encode(request)
        http_request = urllib2.Request(self.crl_url, binary_request,
                { 'Content-Type': 'application/timestamp-query' })
        if self.username != None:
            base64string = base64.standard_b64encode('%s:%s' % (self.username, self.password))
            http_request.add_header("Authorization", "Basic %s" % base64string)
        try:
            response = urllib2.urlopen(http_request).read()
        except (IOError, socket.error), e:
            raise TimestampingError('Unable to send the request to %s' % self.crl_url, e)
        
        tst_response, substrate = decoder.decode(response, asn1Spec=rfc3161.TimeStampResp())
        if substrate:
            return False, 'Extra data returned'
        
        return encoder.encode(tst_response), ''
        
        #result, message = self.check_response(tst_response, digest, nonce=nonce)
        #if result:
        #    return encoder.encode(tst_response.time_stamp_token), ''
        #else:
        #    return False, message