import sys
from gi.repository import Gtk, GObject
from fpiuwidget import FirmapiuWindow
from fpiuwidget import FirmapiuButton
from driverlib import install_athena
from driverlib import install_cardos
from driverlib import install_incard
from driverlib import install_oberthur
from driverlib import is_root

class DriverWindows(FirmapiuWindow):
    
    def __init__(self):
        FirmapiuWindow.__init__(self)
                
        fbutton_athena = FirmapiuButton('Athena', None, self.athena)
        fbutton_cardos = FirmapiuButton('Cardos', None, self.cardos)
        fbutton_incard = FirmapiuButton('Incard', None, self.incard)
        fbutton_obertur = FirmapiuButton('Oberthur', None, self.oberthur)
                
        self.fgrid.add_fbutton(fbutton_athena)
        self.fgrid.add_fbutton(fbutton_cardos)
        self.fgrid.add_fbutton(fbutton_incard)
        self.fgrid.add_fbutton(fbutton_obertur)

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
    win = DriverWindows()
    win.show_all()
    Gtk.main()