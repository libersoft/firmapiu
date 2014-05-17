#!/usr/bin/python
import os
import hashlib
import rfc3161
from pyasn1_modules import rfc2459
from pyasn1.type import univ
from pyasn1.codec.der import encoder

class TSAClient(object):
    def __init__(self):
        pass


def create_timestamp_query(filename):
    if not os.path.exists(filename):
        return None, 'file non esistente'

    if not os.path.isfile(filename):
        return None, 'not a file'

    # calcolo l'hash 256 de file
    try:
        file_hash = open(filename, "rb")
        hash_obj = hashlib.sha256()
        hash_obj.update(file_hash.read())
        digest = hash_obj.digest()
    except:
        return None, 'failed to hash file'  # TODO da riverede la gestione delle eccezioni

    # costruisce l'oggetto richiesta
    algorithm_identifier = rfc2459.AlgorithmIdentifier()
    algorithm_identifier.setComponentByPosition(0, rfc3161.__dict__["id_sha256"])
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

    return binary_request, ""


