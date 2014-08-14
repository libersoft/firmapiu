from gi.repository import GObject, Gtk
from fpiuwidget import FirmapiuButton
from fpiuwidget import FirmapiuWindow
from certmanager import CertificateManager
import localconfig

icon_dir = "/usr/share/firmapiu/icon/"

class CertificateGui(FirmapiuWindow):
    def __init__(self):
        FirmapiuWindow.__init__(self)
        
        self._certmanager = CertificateManager(localconfig.DATABASE_FILE)
        
        fbutton_load_cert = FirmapiuButton('Carica file di certificato', icon_dir + 'firma.png', self.carica_certificato)
        fbutton_show_cert = FirmapiuButton('Mostra Certificati', icon_dir + 'verifica.png', self.mostra_certificati)
        fbutton_esci = FirmapiuButton('esci', icon_dir + 'esci.png', self.esci)

        self.fgrid.add_fbutton(fbutton_load_cert)
        self.fgrid.add_fbutton(fbutton_show_cert)
        self.fgrid.add_fbutton(fbutton_esci)

    def cleanup(self):
        FirmapiuWindow.cleanup(self)

    def esci(self, widget):
        print 'esci pressed'
        self.cleanup()
        Gtk.main_quit()

    def carica_certificato(self, widget):
        pass
    
    def mostra_certificati(self, widget):
        pass
    
GObject.threads_init()
win = CertificateGui()
win.show_all()
Gtk.main()