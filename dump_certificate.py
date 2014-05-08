#!/usr/bin/python

import PyKCS11
import sys


# def dump(src, length=8):
#     FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
#     N = 0
#     result = ''
#     while src:
#         s, src = src[:length], src[length:]
#         hexa = ' '.join(["%02X" % ord(x) for x in s])
#         s = s.translate(FILTER)
#         result += "%04X   %-*s   %s\n" % (N, length * 3, hexa, s)
#         N += length
#     return result


class GetInfo(object):

    def __init__(self, library_path):
        self.pkcs11_obj = PyKCS11.PyKCS11Lib()
        self.pkcs11_obj.load(library_path)

    def get_slot_list(self):
        return self.pkcs11_obj.getSlotList()

    def get_slot_info(self, slot):
        assert isinstance(slot, int)
        return self.pkcs11_obj.getSlotInfo(slot)

    def get_token_info(self, slot):
        assert isinstance(slot, int)
        return self.pkcs11_obj.getTokenInfo(slot)

    def dump_ds_certificate(self, slot, outfile="certificate.der"):
        assert isinstance(slot, int)
        session = self.pkcs11_obj.openSession(slot)

        # tutti gli attrivuti possibili per i token
        all_attributes = PyKCS11.CKA.keys()
        all_attributes = [e for e in all_attributes if isinstance(e, int)]

        # ottengo i token della smartcard
        objects = session.findObjects()

        # se non sono presenti token
        if not len(objects):
            sys.stderr.write("nessun token trovato")
            return False

        for obj in objects:
            attributes = session.getAttributeValue(obj, all_attributes)
            attr_dict = dict(zip(all_attributes, attributes))

            # cerco nei certificati CKO_CERTIFICATE quelli che contengono DS
            if attr_dict[PyKCS11.CKA_CLASS] == PyKCS11.CKO_CERTIFICATE and \
                    attr_dict[PyKCS11.CKA_TRUSTED] and \
                    attr_dict[PyKCS11.CKA_TOKEN] and \
                    attr_dict[PyKCS11.CKA_CERTIFICATE_TYPE] == PyKCS11.CKC_X_509 and \
                    "DS" in str(attr_dict[PyKCS11.CKA_LABEL]):
                # print attr_dict[PyKCS11.CKA_ID]
                # faccio un dump della sessione
                value = attr_dict[PyKCS11.CKA_VALUE]
                cert_file = open(outfile, "wb")
                for unicode_val in value:
                    cert_file.write(chr(unicode_val))
                cert_file.close()

        return True

# se non sono stati passati argomenti
if len(sys.argv) == 1:
    library = "/usr/local/lib/libbit4ipki.so"
else:  # il primo ergomento passato e' la libreria
    library = sys.argv[1]

info = GetInfo(library)
# ottengo la lista degli slot per la smartcard
slot_list = info.get_slot_list()

# se non ci sono slot inserite
if not len(slot_list):
    sys.exit(1)
else:  # di default uso la prima
    slot_use = slot_list[0]

if info.dump_ds_certificate(slot_use):
    sys.exit(0)
else:
    sys.exit(1)
