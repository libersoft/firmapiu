#!/usr/bin/python
import os
from gi.repository import Gtk
from gi.repository import GObject

from loglib import ERROR, DEBUG, Logger
from fpiumanager import FirmapiuManager

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


class FirmapiuMainWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self)

        self.icon_dir = "/usr/share/firmapiu/icon/"
        
        self.connect("delete-event", Gtk.main_quit)
        self.populate_with_icon()  # aggiungo le icone
        
        self.logger = Logger()
        self.logger.function  = self.write_log
        self.signmanager = FirmapiuManager(self.config_handler, self.logger)

    def populate_with_icon(self):
        self.button_grid = Gtk.Grid()
        self.add(self.button_grid)

        self.bottone_firma = Gtk.Button(label='firma')
        self.bottone_firma.connect("clicked", self.firma)

        self.bottone_verifica = Gtk.Button(label='verifica')
        self.bottone_verifica.connect("clicked", self.verifica)

        self.installa_driver = Gtk.Button(label='installa driver')
        self.installa_driver.connect("clicked", self.install_driver)

        self.carica_cert = Gtk.Button(label='carica certificati')
        self.carica_cert.connect("clicked", self.carica_certificati)

        self.bottone_esci = Gtk.Button(label='esci')
        self.bottone_esci.connect("clicked", self.esci)

        self.log_view = Gtk.TextView()
        self.log_buffer = self.log_view.get_buffer()
        self.log_buffer.set_modified(False)
        self.log_view.show()

        self.button_grid.attach(self.bottone_firma, 1, 0, 1, 1)
        self.button_grid.attach(self.bottone_verifica, 2, 0, 1, 1)
        #self.button_grid.attach(self.bottone_timestamp, 3, 0, 1, 1)
        #self.button_grid.attach(self.bottone_impostazioni, 1, 1, 1, 1)
        #self.button_grid.attach(self.bottone_impostazioni_avanzate, 2, 1, 1, 1)
        self.button_grid.attach(self.bottone_esci, 3, 1, 1, 1)
        self.button_grid.attach(self.installa_driver, 1, 2, 1, 1)
        self.button_grid.attach(self.carica_cert, 2, 2, 1, 1)
        #self.button_grid.attach(self.label_drag_drop, 1, 2, 3, 1)
        self.button_grid.attach(self.log_view, 1, 3, 3, 1)

    # Funzione che verra chiamata dall'handler ogni volta che ci saranno dei da inserire dei messaggi
    def write_log(self, msg_type, msg_str):
        if msg_type == ERROR:
            self.log_buffer.insert(self.log_buffer.get_end_iter(), "[error] %s\n" % msg_str)
        elif msg_type == DEBUG:
            self.log_buffer.insert(self.log_buffer.get_end_iter(), "[debug] %s\n" % msg_str)
        else:
            self.log_buffer.insert(self.log_buffer.get_end_iter(), "%s\n" % msg_str)

    def launch_choose_window(self, extension=None):
        dialog = Gtk.FileChooserDialog(
            "Scegli il file da firmare",
            self, Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK
            )
        )
        if extension is not None:  # aggiungo il filtro all'estensione
            filter_ext = Gtk.FileFilter()
            filter_ext.set_name("file with extension .%s" % extension)
            filter_ext.add_pattern("*.%s" % extension)
            dialog.add_filter(filter_ext)
        
        response = dialog.run()
        choise = None
        if response == Gtk.ResponseType.OK:
            choise = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            choise = None
        dialog.destroy()

        return choise

    def config_handler(self, name):  # handler usato per le richieste del file di configurazione
        # viene creato un dialog per ogni valore non scritto nel file di configurazione
        entryDialog = FirmapiuEntryDialog('%s:' % name, 'inserisci qui %s' % name)
        # attendo che l'utente inserisca un valore
        response = entryDialog.run()
        if response == Gtk.ResponseType.OK:
            result = entryDialog.get_response()  # estraggo il valore
        elif response == Gtk.ResponseType.CANCEL:
            result = None

        # distruggo la finestra creata
        entryDialog.destroy()
        return result

    def dispatcher(self, widget):
        self.verifica(widget)
        #thread.start_new_thread(firma, ())

    def carica_certificati(self, widget):
        self.signmanager.load_cert_dir()

    def firma(self, widget):
        file_choose = self.launch_choose_window()
        if file_choose is not None:  # se ho scelto il file
            self.signmanager.sign(file_choose)            
            

    def verifica(self, widget):
        file_choose = self.launch_choose_window(extension='p7m')  # scelgo il file da verificare
        if file_choose is not None:
            self.signmanager.verify(file_choose)

    def timestamp(self, widget):
        file_choose = self.launch_choose_window()
        if file_choose is not None:
            self._signer.timestamp_file(
                filename=file_choose
            )
            
    def verifica_timestamp(self, widget):
        file_choose = self.launch_choose_window(extension='tsr')  # scelgo il file da verificare
        if file_choose is not None:
            self._signer.verify_timestamp_file(file_choose, file_choose)

    def install_driver(self, widget):
        os.popen('gksudo python /usr/share/firmapiu/library/drivergui.py')

    def impostazioni(self, widget):
        self._logger.status('impostazioni pressed')

    def impostazioni_avanzate(self, widget):
        self._logger.status('avanzate pressed')

    def esci(self, widget):
        Gtk.main_quit()


def main():
    GObject.threads_init()
    win = FirmapiuMainWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
