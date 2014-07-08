import sys
from gi.repository import Gtk, GObject
from fpiuwidget import FirmapiuWindow
from fpiuwidget import FirmapiuButton
from driverlib import install_athena
from driverlib import install_cardos
from driverlib import install_incard
from driverlib import install_oberthur
from driverlib import is_root


icon_dir = "/usr/share/firmapiu/icon/"


class DriverWindow(FirmapiuWindow):
    
    def __init__(self):
        FirmapiuWindow.__init__(self)
                
        fbutton_athena = FirmapiuButton('Athena', icon_dir + 'driver.png', self.athena)
        fbutton_cardos = FirmapiuButton('Cardos', icon_dir + 'driver.png', self.cardos)
        fbutton_incard = FirmapiuButton('Incard', icon_dir + 'driver.png', self.incard)
        fbutton_obertur = FirmapiuButton('Oberthur', icon_dir + 'driver.png', self.oberthur)
        fbutton_esci = FirmapiuButton('esci', icon_dir + 'esci.png', self.esci)

                
        self.fgrid.add_fbutton(fbutton_athena)
        self.fgrid.add_fbutton(fbutton_cardos)
        self.fgrid.add_fbutton(fbutton_incard)
        self.fgrid.add_fbutton(fbutton_obertur)
        self.fgrid.add_fbutton(fbutton_esci)

    def esci(self, widget):
        print 'esci pressed'
        Gtk.main_quit()

    def athena(self, widget):
        self.executor.set_function(install_athena, self.logger)
        self.executor.execute_function()

    def cardos(self, widget):
        self.executor.set_function(install_cardos, self.logger)
        self.executor.execute_function()

    def incard(self, widget):
        self.executor.set_function(install_incard, self.logger)
        self.executor.execute_function()

    def oberthur(self, widget):
        self.executor.set_function(install_oberthur, self.logger)
        self.executor.execute_function()


if __name__ == '__main__':
    if not is_root():
        print 'use this program has root'
        sys.exit(1)
         
    GObject.threads_init()
    win = DriverWindow()
    win.show_all()
    Gtk.main()