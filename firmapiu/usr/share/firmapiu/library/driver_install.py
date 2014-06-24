import sys
from gi.repository import Gtk
from driverlib import install_athena
from driverlib import install_cardos
from driverlib import install_incard
from driverlib import install_oberthur
from driverlib import is_root

driver = {
    'Athena': install_athena,
    'cardOS': install_cardos,
    'Incard': install_incard,
    'Oberthur': install_oberthur
}


def install_driver(install_function):
    if not install_function():
        print 'Installazione fallita'
    else:
        print 'Installazione riuscita'
        

if __name__ == '__main__':
    if not is_root():
        print 'use this program has root'
        sys.exit(1)
         
    
    win = Gtk.Window()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.show()
    
    for drv in driver.keys():
        butt = Gtk.Button(label=drv)
        butt.connect("clicked", lambda wid: install_driver(driver[drv]))
        box.pack_start(butt, True, True, 0)
        butt.show()
        
    win.add(box)
    
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()