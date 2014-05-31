import os
import hashlib
import rfc3161
from pyasn1_modules import rfc2459
from pyasn1.type import univ
from pyasn1.codec.der import encoder

class TimestampRequestPacker(object):
    def __init__(self, logger):
        if logger is None:
            raise AttributeError
        self.logger = logger

    def pack_der(self, filename):
        if not os.access(filename, os.R_OK):
            self.logger.error('no file %s found' % filename)
            return None
        try:
            file_hash = open(filename, 'rb')
            hash_obj = hashlib.sha256()
            hash_obj.update(file_hash.read())
            digest = hash_obj.digest()
        except:
            self.logger.error('not hash generate')
            return None

        # costruisce la rischiesta
        algorithm_identifier = rfc2459.AlgorithmIdentifier()
        algorithm_identifier.setComponentByPosition(0, rfc3161.__dict__['id_sha256'])
        algorithm_identifier.setComponentByPosition(1, univ.Null())  # serve per Aruba

        message_imprint = rfc3161.MessageImprint()
        # setto l'identificatore della hash nella richiesta
        message_imprint.setComponentByPosition(0, algorithm_identifier)
        # inserisco la hash nella richiesta
        message_imprint.setComponentByPosition(1, digest)

        request = rfc3161.TimeStampReq()
        request.setComponentByPosition(0, 'v1')
        request.setComponentByPosition(1, message_imprint)
        request.setComponentByPosition(4, univ.Boolean(True))  # server per Aruba

        # codifico tutto in DER
        binary_request = encoder.encode(request)
        return binary_request

