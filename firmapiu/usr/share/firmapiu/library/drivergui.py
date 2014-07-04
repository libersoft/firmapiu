import sys
from threading import Thread
from gi.repository import Gtk, GObject
from driverlib import install_athena
from driverlib import install_cardos
from driverlib import install_incard
from driverlib import install_oberthur
from driverlib import is_root
from loglib import Logger

driver = {
    'Athena': install_athena,
    'cardOS': install_cardos,
    'Incard': install_incard,
    'Oberthur': install_oberthur
}


class InstallThread(Thread, GObject.GObject):
    def __init__(self, main, logger):
        self.main = main
        self.logger = logger
        self.exec_function = None
        self.exec_args = None
        self.logger.function = self.logger_callback

    def logger_callback(self, msg_type, msg_str):
        '''
        Funzione chiamata quando devono essere scritte delle 
        informazioni di log.
        Viene inviato un segnale con le informazioni
        '''
        self.main.emit_on_main('log', msg_type, msg_str)

    def set_function(self, function, *args):
        self.exec_function = function
        self.exec_args = args
        
    def run(self):
        self.exec_function(*self.exec_args)


class FirmapiuLogView(Gtk.TextView):
    def __init__(self):
        Gtk.TextView.__init__(self)
        self.log_buff = self.get_buffer()
        self.log_buff.set_modified(False)
        self.show()
        
    def insert_message(self, message):
        assert isinstance(message, str)
        self.log_buff.insert(self.log_buff.get_end_iter(), message)


class DriverWindow(Gtk.Window):
    __gsignals__ = {
        'log' : (
            GObject.SIGNAL_RUN_LAST, None, (str, str)
        )
    }

    def __init__(self):
        Gtk.Window.__init__(self)
        self.logger = Logger()
        self.log = FirmapiuLogView()

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.show()
        self.add(self.box)

        for drv in driver.keys():
            butt = Gtk.Button(label=drv)
            butt.connect("clicked", self.install_driver)
            self.box.pack_start(butt, True, True, 0)
            butt.show()
            
        self.box.pack_start(self.log, True, True, 0)

    def do_log(self, msg_type, msg_str):
        self.log.insert_message('[%s] %s\n' % (msg_type, msg_str))
    
    def emit_on_main(self, *args):
        GObject.idle_add(GObject.GObject.emit,self,*args)
    
    def install_driver(self, widget):
        install_thread = InstallThread(self, self.logger)
        install_thread.set_function(install_athena, self.logger)
        install_thread.run()


if __name__ == '__main__':
    if not is_root():
        print 'use this program has root'
        sys.exit(1)
         
    win = DriverWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()