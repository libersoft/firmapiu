from gi.repository import GObject, Gtk
from threading import Thread, current_thread, Condition
from loglib import Logger
from conflib import ConfigFileReader

class _ExecutorThread(Thread, GObject.GObject):
    __gsignals__ = {
        'main_response': (
            GObject.SIGNAL_RUN_LAST, None, (str,)
        )
                    
    }
    
    def __init__(self, main, logger, config):
        assert isinstance(logger, Logger)
        assert isinstance(config, ConfigFileReader)
        
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.exec_cond = Condition()
        self.cond = Condition()
        self.main = main
        self.exec_function = None
        self.exec_args = None
        self.cancel = False
        self.logger = logger
        self.config = config
        self.logger.function = self.logger_callback
        self.config.function = self.config_callback
        self.buff = None
        
    def do_main_response(self, value):
        '''
        funzione chiamata quando ricevo una risposta dal main
        tramite un segnale
        '''
        self.cond.acquire()
        self.buff = value
        self.cond.notify()
        self.cond.release()

    def set_function(self, function, *args):
        self.exec_function = function
        self.exec_args = args
        
    def cancel(self):
        self.cancel = True
        
    def config_callback(self, name):
        '''
        funzione chiamata quando ho bisogno di informazioni di
        configurazione, viene mandato un segnale al main
        e viene poi aspettato con una wait di essere svegliati.
        La variabile self.buff serve per il passaggio di
        parametri.
        '''
        self.cond.acquire()
        self.main.emit_on_main('thread_request', name)
        self.cond.wait()
        value = self.buff
        self.cond.release()
        return value
        
    def logger_callback(self, msg_type, msg_str):
        '''
        funzione chiamata quando devono essere scritte delle 
        informazioni di log.
        Viene inviato un segnale con le informazioni
        '''
        self.main.emit_on_main('thread_progress', msg_type, msg_str)

    def execute_function(self):
        self.exec_cond.acquire()
        print 'send notify to function', current_thread().getName()
        self.exec_cond.notify()
        self.exec_cond.release()

    def run(self):
        while not self.cancel:
            self.exec_cond.acquire()
            print 'waiting for function to execute', current_thread().getName()
            self.exec_cond.wait()
            print 'reciving function to execute', current_thread().getName()
            self.exec_function(*self.exec_args)
            self.exec_cond.release()
        print 'cancel', current_thread().getName()

class TestWindow(Gtk.Window):
    
    __gsignals__ = {
        'thread_progress' : (
            GObject.SIGNAL_RUN_LAST, None, (str, str)
        ),
        'thread_request' : (
            GObject.SIGNAL_RUN_LAST, None, (str,)
                            
        )
    }
    
    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.logger = Logger()
        self.config = ConfigFileReader('/etc/firmapiu/firmapiu.conf', self.logger)
        
        button = Gtk.Button('bottone')
        button.connect('clicked', self.firma)
        self.add(button)
        self.executor = _ExecutorThread(self, self.logger, self.config)
        self.executor.start()

    def firma(self, widget):
        self.executor.set_function(prova_funzione, self.config, self.logger)
        self.executor.execute_function()
        
    def do_thread_progress(self, msg_type, msg_str):
        '''
        Funzione chiamata quando il thread comunica col main
        delle informazioni di log
        '''
        print msg_type, msg_str, current_thread().getName()
        
    def do_thread_request(self, name):
        '''
        Funzione chiamata quando il thread vuole delle informazioni
        di configurazione dal main.
        Il main mostra all'utente dei dialog e da essi recupera
        le informazioni e con un segnale le invia al thread
        '''
        print 'request', name, current_thread().getName()
        self.executor.emit('main_response', 'pippo')
        
    def emit_on_main(self, *args):
        GObject.idle_add(GObject.GObject.emit,self,*args)


def prova_funzione(config, logger):
    assert isinstance(config, ConfigFileReader)
    assert isinstance(logger, Logger)
    print 'prova funzione', current_thread().getName()
    logger.status('messaggio di status')
    logger.error('messaggio di errore')
    logger.debug('messaggio di debug')
    pin = config.get_smartcard_pin()
    print 'pin', pin, current_thread().getName()

GObject.threads_init()
win = TestWindow()
win.show_all()
Gtk.main()