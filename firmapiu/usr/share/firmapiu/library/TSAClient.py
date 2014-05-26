#!/usr/bin/python
import os
import hashlib
import rfc3161
from pyasn1_modules import rfc2459
from pyasn1.type import univ
from pyasn1.codec.der import encoder
import WebRequest
import ConfigProvider


def create_timestamp_query(filename, logger=None):
    if not os.access(filename, os.R_OK):
        logger.error('Non file %s found' % filename)
        return None

    try:
        file_hash = open(filename, 'rb')
        hash_obj = hashlib.sha256()
        hash_obj.update(file_hash.read())
        digest = hash_obj.digest()
    except:
        logger.error('not hash generate')
        return None

    # costruisce la richiesta
    algorithm_identifier = rfc2459.AlgorithmIdentifier()
    algorithm_identifier.setComponentByPosition(0, rfc3161.__dict__['id_sha256'])
    algorithm_identifier.setComponentByPosition(1, univ.Null())  # serve per Aruba
    message_imprint = rfc3161.MessageImprint()
    message_imprint.setComponentByPosition(0, algorithm_identifier)
    message_imprint.setComponentByPosition(1, digest)
    request = rfc3161.TimeStampReq()
    request.setComponentByPosition(0, 'v1')
    request.setComponentByPosition(1, message_imprint)
    request.setComponentByPosition(4, univ.Boolean(True))  # server per Aruba
    # codifico tutto in DER
    binary_request = encoder.encode(request)

    return binary_request


def send_timestamp_query(logger=None):
    web = WebRequest("https://servizi.arubapec.it/tsa/ngrequest.php", logger)
    web.request()

