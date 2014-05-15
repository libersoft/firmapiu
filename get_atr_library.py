import os
import sys
import libxml2
import logging
from smartcard import System, Exceptions  # sudo apt-get install python-pyscard
from smartcard.pcsc import PCSCExceptions
from smartcard.util import toHexString


def check_pcscd_running():
    """
    return the status of pcscd daemon
    :rtype : bool
    """
    logging.debug("check for pcscd daemon running")
    pcscd_pid_file = "/var/run/pcscd/pcscd.pid"
    if os.path.exists(pcscd_pid_file):
        return True
    else:
        return False


def get_smartcard_atr():
    """
    return the atr of the current device
    :rtype : (string or None, str or None)
    """

    try:
        # ottengo la lista dei lettori
        readers_list = System.readers()
    except PCSCExceptions.EstablishContextException:
        # il lettore di smartcard potrebbe non essere inserito
        return None, "demone pcscd not attivo\n"

    # non sono riuscito a trovare nessun lettore
    if len(readers_list) == 0:
        return None, "nessun lettore riconosciuto\n"

    # di default prendo il primo lettore
    reader = readers_list[0]

    connection = reader.createConnection()
    try:
        # Mi connetto e ottengo l'ATR dalla carta
        connection.connect()
        atr_str = toHexString(connection.getATR()).replace(" ", ":").lower()
        connection.disconnect()
    except Exceptions.CardConnectionException, e:
        return None, "smartcard non inserita\n"

    return atr_str, ""


def get_smartcard_library(atr_str):
    """
    in base all'atr restituisco quale libreria e' utile usare
    :rtype : (string or None , string or None)
    :param atr_str:string stringa che contiene l'atr della smartcard
    """

    # carico il file xml con le librerie e cerco la libreria relativa all'ATR
    doc = libxml2.parseFile("libraries.xml")
    # in base all'atr cerco nel file usando XPATH
    library_result = doc.xpathEval("//key[text()='%s']/../@path" % atr_str)
    # se non trovo nessun risultato
    if len(library_result) == 0:
        return None, "non ho trovato nessuna libreria\n"

    # ottengo il path della libreria
    library_used = library_result[0].get_content()
    return library_used, ""


def main():
    if not check_pcscd_running():
        sys.stderr.write("demone pcscd not work")
        return 1

    str_atr, err_str = get_smartcard_atr()
    if not str_atr:
        sys.stderr.write(err_str)
        return 1

    str_lib, err_str = get_smartcard_library(str_atr)
    if not str_lib:
        logging.error(err_str)
        return 1

    print(str_lib)
    return 0


if __name__ == "__main__":
    sys.exit(main())

