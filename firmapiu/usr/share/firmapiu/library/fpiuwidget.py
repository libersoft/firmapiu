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
        
        self.setDaemon(True)  # il thread al momento viene distrutto quando il main esce
        self.exec_cond = Condition()
        self.cond = Condition()
        self.main = main
        self.exec_function = None
        self.exec_args = None
        self._cancel = False
        self.logger = logger
        self.config = config
        self.logger.function = self.logger_callback
        self.config.function = self.config_callback
        self.buff = None
        
    def __del__(self):
        print "Executor Thread __del__"
        
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
        print 'executor cancel call'
        self._cancel = True
        
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
        while not self._cancel:
            self.exec_cond.acquire()
            print 'waiting for function to execute', current_thread().getName()
            self.exec_cond.wait()
            print 'reciving function to execute', current_thread().getName()
            try:
                print 'retval run:"', self.exec_function(*self.exec_args), '"'
                self.main.emit_on_main('thread_completed', 'OK')
            except Exception, e:
                print 'exception on thread occur', e
                self.main.emit_on_main('thread_completed_error', str(e))
                
            self.exec_cond.release()
        
        print '_cancel', current_thread().getName()


class FirmapiuConfigWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
    
class FirmapiuProgress(Gtk.ProgressBar):
    def __init__(self, text):
        Gtk.ProgressBar.__init__(self)
        self.set_show_text(True)
        self.set_text(text)
        self.show()
        self._active = False
        
    def _on_timeout(self, data):
        print 'on timeout', current_thread().getName()
        if not self._active:
            return False
        else:
            self.pulse()
            return True
        
    def active(self):
        self._active = True
        print 'gobject timeout add', current_thread().getName()
        GObject.timeout_add(100, self._on_timeout, None)
        
    def deactive(self):
        self._active = False


icon_dir = "/usr/share/firmapiu/icon/"


class FirmapiuWindow(Gtk.Window):
    __gsignals__ = {
        'thread_progress' : (
            GObject.SIGNAL_RUN_LAST, None, (str, str)
        ),
        'thread_request' : (
            GObject.SIGNAL_RUN_LAST, None, (str,)
                            
        ),
        'thread_completed' : (
            GObject.SIGNAL_RUN_LAST, None, (str,)
                            
        ),
        'thread_completed_error' : (
            GObject.SIGNAL_RUN_LAST, None, (str,)
                            
        ),
    }
    
    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect('destroy', Gtk.main_quit)
        self.logger = Logger()
        self.config = ConfigFileReader('/etc/firmapiu/firmapiu.conf', self.logger)

        self.executor = _ExecutorThread(self, self.logger, self.config)
        self.executor.start()
        
        self.vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.fgrid = FirmapiuGrid(3)  # griglia nella quale verranno disposte le icone
        self.flog = FirmapiuLogWindow()  # finestra di log del programma
        self.vbox.pack_start(self.fgrid, True, True, 0)
        self.vbox.pack_start(self.flog, True, True, 0)
        self.add(self.vbox)

    def __del__(self):
        print 'FirmapiuWindow __del__'

    def cleanup(self):
        print 'FirmapiuWindow.cleanp()'
        self.config.cleanup()
        self.logger.cleanup()


    def do_thread_completed(self, msg):
        self.flog.insert_message('OK %s' % msg)
    
    def do_thread_completed_error(self, err_msg):
        self.flog.insert_message('ERRORE: %s' % err_msg)

    def do_thread_progress(self, msg_type, msg_str):
        '''
        Funzione chiamata quando il thread comunica col main
        delle informazioni di log
        '''
        #print msg_type, msg_str, current_thread().getName()
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


class FirmapiuGrid(Gtk.Grid):    
    def __init__(self, column):
        Gtk.Grid.__init__(self)
        self.max_column = column
        self.row = 0
        self.column = 0

    def add_fbutton(self, fbutton):
        assert isinstance(fbutton, FirmapiuButton)
        self.attach(fbutton, self.column, self.row, 1, 1)
        if self.column == (self.max_column - 1):
            self.row += 1
            self.column = 0
        else:
            self.column += 1


class FirmapiuLogWindow(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.log_widget = Gtk.TextView()
        self.add(self.log_widget)
        self.log_buff = self.log_widget.get_buffer()
        self.log_buff.set_modified(False)
        self.insert_message("-- Finestra di Log --\n")
        self.show()
        
    def insert_message(self, message):
        assert isinstance(message, str)
        self.log_buff.insert(self.log_buff.get_end_iter(), message)


class FirmapiuButton(Gtk.Button):
    def __init__(self, label, image_path, clicked_function):
        Gtk.Button.__init__(self,label=label)
        if image_path is not None:
            self.set_image(Gtk.Image.new_from_file(image_path))
            self.set_image_position(Gtk.PositionType.TOP)
        self.connect('clicked', clicked_function)
#         if image_path is not None:
#             image = Gtk.Image()
#             image.set_from_file(image_path)
#             
#         image = Gtk.Image(stock=Gtk.STOCK_OPEN)

       



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


if __name__ == '__main__':
    GObject.threads_init()
    win = Gtk.Window()
    prog = FirmapiuProgress('pippo')
    win.show_all()
    prog.active() 
    win.add(prog)
    Gtk.main()    
