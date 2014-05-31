#!/usr/bin/python

import sys
import commands
from threading import Thread
from gi.repository import Gtk
from TSA import TimestampClient

sys.path.append('../library')
import SignProvider
from Logger import Logger
from ConfigFileLoader import ConfigFileLoader


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


class FirmapiuWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        self.logger = Logger(self.write_log)
        self.icon_dir = "../icon/"
        self.config = ConfigFileLoader(
            '../../../../etc/firmapiu/firmapiu.conf',
            self.config_handler,
            self.logger)
        self.connect("delete-event", Gtk.main_quit)
        self.populate_with_icon()  # aggiungo le icone

    def populate_with_icon(self):
        self.button_grid = Gtk.Grid()
        self.add(self.button_grid)

        self.bottone_firma = Gtk.Button()
        image_bottone_firma = Gtk.Image()
        image_bottone_firma.set_from_file(self.icon_dir + 'firma96x96.png')
        image_bottone_firma.show()
        self.bottone_firma.add(image_bottone_firma)
        self.bottone_firma.connect("clicked", self.firma)

        self.bottone_verifica = Gtk.Button()
        image_bottone_verifica = Gtk.Image()
        image_bottone_verifica.set_from_file(self.icon_dir + "verifica96x96.png")
        image_bottone_verifica.show()
        self.bottone_verifica.add(image_bottone_verifica)
        self.bottone_verifica.connect("clicked", self.verifica)

        self.bottone_verifica = Gtk.Button()
        image_bottone_verifica = Gtk.Image()
        image_bottone_verifica.set_from_file(self.icon_dir + "verifica96x96.png")
        image_bottone_verifica.show()
        self.bottone_verifica.add(image_bottone_verifica)
        self.bottone_verifica.connect("clicked", self.verifica)

        self.bottone_timestamp = Gtk.Button()
        image_bottone_timestamp = Gtk.Image()
        image_bottone_timestamp.set_from_file(self.icon_dir + "datacarta96x96.png")
        image_bottone_timestamp.show()
        self.bottone_timestamp.add(image_bottone_timestamp)
        self.bottone_timestamp.connect("clicked", self.timestamp)

        self.bottone_impostazioni = Gtk.Button()
        image_bottone_impostazioni = Gtk.Image()
        image_bottone_impostazioni.set_from_file(self.icon_dir + "impostazioni96x96.png")
        image_bottone_impostazioni.show()
        self.bottone_impostazioni.add(image_bottone_impostazioni)
        self.bottone_impostazioni.connect("clicked", self.impostazioni)

        self.bottone_impostazioni_avanzate = Gtk.Button()
        image_bottone_impostazioni_avanzate = Gtk.Image()
        image_bottone_impostazioni_avanzate.set_from_file(self.icon_dir + "avanzate96x96.png")
        image_bottone_impostazioni_avanzate.show()
        self.bottone_impostazioni_avanzate.add(image_bottone_impostazioni_avanzate)
        self.bottone_impostazioni_avanzate.connect("clicked", self.impostazioni_avanzate)

        self.bottone_esci = Gtk.Button()
        image_bottone_esci = Gtk.Image()
        image_bottone_esci.set_from_file(self.icon_dir + "system-log-out.png")
        image_bottone_esci.show()
        self.bottone_esci.add(image_bottone_esci)
        self.bottone_esci.connect("clicked", self.esci)

        self.log_view = Gtk.TextView()
        self.log_buffer = self.log_view.get_buffer()
        self.log_buffer.set_modified(False)
        self.log_view.show()
        self.logger.write(None, "finestra di log del programma")

        self.button_grid.attach(self.bottone_firma, 1, 0, 1, 1)
        self.button_grid.attach(self.bottone_verifica, 2, 0, 1, 1)
        self.button_grid.attach(self.bottone_timestamp, 3, 0, 1, 1)
        self.button_grid.attach(self.bottone_impostazioni, 1, 1, 1, 1)
        self.button_grid.attach(self.bottone_impostazioni_avanzate, 2, 1, 1, 1)
        self.button_grid.attach(self.bottone_esci, 3, 1, 1, 1)
        #self.button_grid.attach(self.label_drag_drop, 1, 2, 3, 1)
        self.button_grid.attach(self.log_view, 1, 3, 3, 1)

    # Funzione che verra chiamata dall'handler ogni volta che ci saranno dei da inserire dei messaggi
    def write_log(self, msg_type, msg_str):
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

    def firma(self, widget):
        file_choose = self.launch_choose_window()
        if file_choose is not None:  # se ho scelto il file
            signer = SignProvider.SignProvider(self.config, self.logger, True)
            signer.sign_file_with_ds_certificate(file_choose)

    def verifica(self, widget):
        file_choose = self.launch_choose_window(extension='p7m')  # scelgo il file da verificare
        if file_choose is not None:
            signer = SignProvider.SignProvider(self.config, self.logger)
            signer.verify_file_with_ds_certificate(file_choose, file_choose)

    def timestamp(self, widget):
        file_choose = self.launch_choose_window()
        if file_choose is not None:
            timest = TimestampClient(self.config, self.logger)
            timest.send_timestamp_query(file_choose)  # eseguo la richiesta di timestamp
            # TODO va salvato il file

    def verifica_timestamp(self, widget):
        file_choose = self.launch_choose_window(extension='tsr')  # scelgo il file da verificare
        if file_choose is not None:
            self.logger.status('verifica timestamp pressed')

    def impostazioni(self, widget):
        self.logger.status('impostazioni pressed')

    def impostazioni_avanzate(self, widget):
        self.logger.status('avanzate pressed')

    def esci(self, widget):
        Gtk.main_quit()


def main():
    win = FirmapiuWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
