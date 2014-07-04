import os
from gi.repository import GObject, Gtk
from threading import Thread, current_thread, Condition
from loglib import Logger
from conflib import ConfigFileReader
from fpiumanager import FirmapiuManager

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
        Funzione chiamata quando ricevo una risposta dal main
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
        Funzione chiamata quando ho bisogno di informazioni di
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
        Funzione chiamata quando devono essere scritte delle 
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


class FirmapiuChooseDialog(Gtk.FileChooserDialog):
    def __init__(self):
        Gtk.FileChooserDialog.__init__(self,
            "Scegli il file da firmare",
            None,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK
            )
        )

    def set_extension(self, ext_name):
        assert isinstance(ext_name, str)
        # aggiungo il filtro per l'estensione
        filter_ext = Gtk.FileFilter()
        filter_ext.set_name("file with extension .%s" % ext_name)
        filter_ext.add_pattern("*.%s" % ext_name)
        self.add_filter(filter_ext)


class FirmapiuEntryDialog(Gtk.MessageDialog):
    def __init__(self, insert_title, insert_msg):
        Gtk.Dialog.__init__(self, insert_title, None, 0,
            (
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
        )

        self.insert_msg = insert_msg

        self.label = Gtk.Label(label=insert_title)
        self.label.show()
        self.vbox.pack_start(self.label, True, True, 0)

        self.entry = Gtk.Entry()
        self.entry.set_text(self.insert_msg)
        self.entry.show()
        self.vbox.pack_start(self.entry, True, True, 0)

    def get_response(self):
        if self.entry.get_text() == self.insert_msg:
            return None
        return self.entry.get_text()


class FirmapiuLogView(Gtk.TextView):
    def __init__(self):
        Gtk.TextView.__init__(self)
        self.log_buff = self.get_buffer()
        self.log_buff.set_modified(False)
        self.show()
        
    def insert_message(self, message):
        assert isinstance(message, str)
        print 'log_buff.insert', current_thread().getName()
        self.log_buff.insert(self.log_buff.get_end_iter(), message)


class FirmapiuButton(Gtk.Button):
    def __init__(self, label, image_path, clicked_function):
        Gtk.Button.__init__(self, label=label)
        self.connect('clicked', clicked_function)
        

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
        self.executor = _ExecutorThread(self, self.logger, self.config)
        self.executor.start()
        
        self.fmanager = FirmapiuManager()
        
        self.grid = Gtk.Grid()
        self.add(self.grid)
        
        fbutton_firma = FirmapiuButton('firma', None, self.firma)
        fbutton_verifica = FirmapiuButton('verifica', None, self.verifica)
        fbutton_timestamp = FirmapiuButton('timestamp', None, self.timestamp)
        fbutton_carica_certificati = FirmapiuButton('carica certificati', None, self.carica_certificati)
        fbutton_installa_driver = FirmapiuButton('installa driver', None, self.installa_driver)
        
        self.flog = FirmapiuLogView()
        
        self.grid.attach(fbutton_firma, 0, 0, 1, 1)
        self.grid.attach(fbutton_verifica, 0, 1, 1, 1)
        self.grid.attach(fbutton_timestamp, 0, 2, 1, 1)
        self.grid.attach(fbutton_carica_certificati, 0, 3, 1, 1)
        self.grid.attach(fbutton_installa_driver, 0, 4, 1, 1)
        self.grid.attach(self.flog, 0, 5, 1, 1)

    def choose_filename(self, extension=None):
        dialog = FirmapiuChooseDialog()
        if extension is not None:
            dialog.set_extension(extension)
        response = dialog.run()
        choise = None
        if response == Gtk.ResponseType.OK:
            choise = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            choise = None
        dialog.destroy()
        return choise

    def request_input(self, name):
        dialog = FirmapiuEntryDialog(name, 'inserisci qui')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = dialog.get_response()  # estraggo il valore
        elif response == Gtk.ResponseType.CANCEL:
            result = None
        # distruggo la finestra creata
        dialog.destroy()
        return result
    
    def firma(self, widget):
        filename = self.choose_filename()
        self.executor.set_function(self.fmanager.sign, filename, self.config, self.logger)
        self.executor.execute_function()
        
    def verifica(self, widget):
        filename = self.choose_filename('p7m')
        self.executor.set_function(self.fmanager.verify, filename, self.config, self.logger)
        self.executor.execute_function()
        
    def timestamp(self, widget):
        filename = self.choose_filename()
        self.executor.set_function(self.fmanager.timestamp, filename, self.config, self.logger)
        self.executor.execute_function()
        
    def verifica_timestamp(self, widget):
        filename = self.choose_filename('tsr')
        self.executor.set_function(self.fmanager.timestamp_verify, filename, self.config, self.logger)
        self.executor.execute_function()
        
    def carica_certificati(self, widget):
        self.executor.set_function(self.fmanager.load_cert_dir, self.config, self.logger)
        self.executor.execute_function()
        
    def installa_driver(self, widget):
        os.popen('gksudo python /usr/share/firmapiu/library/drivergui.py')
        
    def do_thread_progress(self, msg_type, msg_str):
        '''
        Funzione chiamata quando il thread comunica col main
        delle informazioni di log
        '''
        print msg_type, msg_str, current_thread().getName()
        self.flog.insert_message('[%s] %s\n' % (msg_type, msg_str))
        
    def do_thread_request(self, name):
        '''
        Funzione chiamata quando il thread vuole delle informazioni
        di configurazione dal main.
        Il main mostra all'utente dei dialog e da essi recupera
        le informazioni e con un segnale le invia al thread
        '''
        print 'request', name, current_thread().getName()
        value = self.request_input(name)
        self.executor.emit('main_response', value)
        
    def emit_on_main(self, *args):
        GObject.idle_add(GObject.GObject.emit,self,*args)


GObject.threads_init()
win = TestWindow()
win.show_all()
Gtk.main()