from sys import exit
from fpiumanager import FirmapiuManager
from loglib import Logger
from conflib import ConfigFileReader
from argparse import ArgumentParser


def parse_argument():
    parser = ArgumentParser()
    parser.add_argument('-s', '--sign', action='append', help='Sign given filename')
    parser.add_argument('-v', '--verify', action='append', help='Verify given filename')
    parser.add_argument('-a', '--add-cert', action='append', help='Add certificate to store')
    parser.add_argument('-c', '--show-certs', action='store_true', help='Show all certificate in the store')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive mode')
    result = parser.parse_args()
    print result
    return result


def on_config_message(name):
    value = raw_input('insert %s: ' % name)
    return value


def on_logger_message(msg_type, msg_str):
    print '[%s] %s' % (msg_type, msg_str)


def interactive_mode():
    print 'Cosa vuoi fare:'
    print '1) Firma'
    print '2) Verifica'
    print '3) Carica Certificato'
    print '4) Esci'
    choise = raw_input('>>> ')
    if choise == '4':
        print 'Hai deciso di uscire'
        exit(0)
    elif choise == '3':
        exit(carica_certificato(config, logger))
    elif choise == '2':
        exit(verifica(config, logger))
    elif choise == '1':
        exit(firma(config, logger))
    else:
        print 'Comando sconosciuto'
        exit(1)


def firma(config, logger):
    filepath = choise_file()
    fmanager.sign(filepath, config, logger)


def verifica(config, logger):
    filepath = choise_file()
    fmanager.verify(filepath, config, logger)


def carica_certificato(config, logger):
    filepath = choise_file()
    fmanager.load_cert(filepath, config, logger)


def mostra_certificati(config, logger):
    pass


def choise_file():
    filepath = raw_input('Path del file: ')
    return filepath


if __name__ == '__main__':
    par = parse_argument()
    logger = Logger()
    logger.function = on_logger_message
    config = ConfigFileReader('/etc/firmapiu/firmapiu.conf', logger)
    config.function = on_config_message
    fmanager = FirmapiuManager()
    fmanager.load_cert_dir(config, logger)
    
    if par.interactive:
        interactive_mode()

    if par.show_certs:
        mostra_certificati(config, logger)
        
    if par.add_cert:
        carica_certificato(config, logger)
        
    if par.sign:
        firma(config, logger)
    
    if par.verify:
        verifica(config, logger)
