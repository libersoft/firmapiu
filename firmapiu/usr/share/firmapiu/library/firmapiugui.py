#!/usr/bin/python
import subprocess
from gi.repository import GObject, Gtk
from fpiumanager import FirmapiuManager
from fpiuwidget import FirmapiuButton
from fpiuwidget import FirmapiuWindow


icon_dir = "/usr/share/firmapiu/icon/"


class TestWindow(FirmapiuWindow):
    
    def __init__(self):
        FirmapiuWindow.__init__(self)
        self.fmanager = FirmapiuManager()
                
        fbutton_firma = FirmapiuButton('firma', icon_dir + 'firma.png', self.firma)
        fbutton_verifica = FirmapiuButton('verifica', icon_dir + 'verifica.png', self.verifica)
        fbutton_timestamp = FirmapiuButton('timestamp', icon_dir + 'timestamp.png', self.timestamp)
        fbutton_carica_certificati = FirmapiuButton('carica certificati', icon_dir + 'certificati.png', self.carica_certificati)
        fbutton_installa_driver = FirmapiuButton('installa driver', icon_dir + 'driver.png', self.installa_driver)
        #fbutton_dati_timestamp = FirmapiuButton('dati timestamp', icon_dir + 'impostazioni.png', self.installa_driver)
        fbutton_esci = FirmapiuButton('esci', icon_dir + 'esci.png', self.esci)
        
        self.fgrid.add_fbutton(fbutton_firma)
        self.fgrid.add_fbutton(fbutton_verifica)
        self.fgrid.add_fbutton(fbutton_timestamp)
        self.fgrid.add_fbutton(fbutton_carica_certificati)
        self.fgrid.add_fbutton(fbutton_installa_driver)
        #self.fgrid.add_fbutton(fbutton_dati_timestamp)
        self.fgrid.add_fbutton(fbutton_esci)


    def __del__(self):
        print 'TestWindow __del__'

    def cleanup(self):
        FirmapiuWindow.cleanup(self)
        self.fmanager.cleanup()

    def esci(self, widget):
        print 'esci pressed'
        self.cleanup()
        Gtk.main_quit()

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
        self.executor.set_function(subprocess.call, ['gksudo' ,'python', '/usr/share/firmapiu/library/drivergui.py'])
        self.executor.execute_function()


GObject.threads_init()
win = TestWindow()
win.show_all()
Gtk.main()