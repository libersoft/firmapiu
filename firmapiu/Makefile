#Mettere sempre il build prima dell'install
# NON FARE COSI
# install:
#		install -d $(ABSOLUTE_BIN_DIR)
#		install src/$(EXE) $(ABSOLUTE_BIN_DIR)/$(EXE)
#
# build:
# 	@echo "Nothing to build this is a simple script"

RELATIVE_BIN_DIR = usr/bin
RELATIVE_ETC_DIR = etc/firmapiu
RELATIVE_SHARE_DIR = usr/share/firmapiu
RELATIVE_MENU_LAUNCHER = usr/share/applications

# path assoluto delle directory
ABSOLUTE_BIN_DIR = $(DESTDIR)/$(RELATIVE_BIN_DIR)
ABSOLUTE_ETC_DIR = $(DESTDIR)/$(RELATIVE_ETC_DIR)
ABSOLUTE_SHARE_DIR = $(DESTDIR)/$(RELATIVE_SHARE_DIR)
ABSOLUTE_MENU_LAUNCHER = $(DESTDIR)/$(RELATIVE_MENU_LAUNCHER)

CONFIG_FILE = firmapiu.conf
CONFIG = firmapiurc

build:
	# sostituisco il path dei moduli
	# sostituisco il path delle icone nella gui
	# sostituisco il path del lanciatore
	@echo 'Nothing to build'

install:
	# creo le directory in /etc /usr/share e /bin
	install -d $(ABSOLUTE_BIN_DIR) $(ABSOLUTE_ETC_DIR) $(ABSOLUTE_SHARE_DIR) $(ABSOLUTE_MENU_LAUNCHER)
	# creo la directory per i moduli, le librerie e le icone
	install -d $(ABSOLUTE_ETC_DIR)/certs
	install -d $(ABSOLUTE_SHARE_DIR)/module
	install -d $(ABSOLUTE_SHARE_DIR)/library
	install -d $(ABSOLUTE_SHARE_DIR)/icon
	# install icons
	install -d $(ABSOLUTE_SHARE_DIR)/icon
	install -m644 $(RELATIVE_SHARE_DIR)/icon/*.png $(ABSOLUTE_SHARE_DIR)/icon
	# install library and config file
	install $(RELATIVE_SHARE_DIR)/module/*.sh $(ABSOLUTE_SHARE_DIR)/module
	install $(RELATIVE_SHARE_DIR)/library/*.py $(ABSOLUTE_SHARE_DIR)/library
	install $(RELATIVE_SHARE_DIR)/gtk/*.py $(ABSOLUTE_SHARE_DIR)/gtk
	install $(RELATIVE_SHARE_DIR)/cli/*.py $(ABSOLUTE_SHARE_DIR)/cli
	# sposto i file di configurazione
	install -m644 $(RELATIVE_ETC_DIR)/$(CONFIG) $(ABSOLUTE_ETC_DIR)
	install -m644 $(RELATIVE_ETC_DIR)/$(CONFIG_FILE) $(ABSOLUTE_ETC_DIR)
	# install binary file
	@echo "creo launcher del programma"
	install -m644 $(RELATIVE_MENU_LAUNCHER)/firmapiu-gtk.desktop $(ABSOLUTE_MENU_LAUNCHER)
	

uninstall:
	# rimuovo la cartella /etc/firmapiu
	rm -r $(ABSOLUTE_ETC_DIR)
	# rimuovo la cartella /usr/share/firmapiu
	rm -r $(ABSOLUTE_SHARE_DIR)
	rm -r $(ABSOLUTE_MENU_LAUNCHER)/firmapiu-gtk.desktop

.PHONY: build install uninstall
