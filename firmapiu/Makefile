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
	install -d $(ABSOLUTE_SHARE_DIR)/library/rfc3161
	install -d $(ABSOLUTE_SHARE_DIR)/icon
	# install icons
	install -d $(ABSOLUTE_SHARE_DIR)/icon
	install -m644 $(RELATIVE_SHARE_DIR)/icon/*.png $(ABSOLUTE_SHARE_DIR)/icon
	# install library and config file
	install $(RELATIVE_SHARE_DIR)/module/*.sh $(ABSOLUTE_SHARE_DIR)/module
	install -m644 $(RELATIVE_SHARE_DIR)/library/*.py $(ABSOLUTE_SHARE_DIR)/library
	install -m644 $(RELATIVE_SHARE_DIR)/library/rfc3161/*.py $(ABSOLUTE_SHARE_DIR)/library/rfc3161
	# sposto i file di configurazione
	install -m644 $(RELATIVE_ETC_DIR)/firmapiurc $(ABSOLUTE_ETC_DIR)
	install -m644 $(RELATIVE_ETC_DIR)/firmapiu.conf $(ABSOLUTE_ETC_DIR)
	install -m644 $(RELATIVE_ETC_DIR)/libraries.xml $(ABSOLUTE_ETC_DIR)
	# install binary file
	@echo "creo launcher del programma"
	install -m644 $(RELATIVE_MENU_LAUNCHER)/firmapiu-gtk.desktop $(ABSOLUTE_MENU_LAUNCHER)
	install -m644 $(RELATIVE_BIN_DIR)/firmapiugui $(ABSOLUTE_BIN_DIR)
	

uninstall:
	# rimuovo la cartella /etc/firmapiu
	rm -r $(ABSOLUTE_ETC_DIR)
	# rimuovo la cartella /usr/share/firmapiu
	rm -r $(ABSOLUTE_SHARE_DIR)
	rm -r $(ABSOLUTE_MENU_LAUNCHER)/firmapiu-gtk.desktop

.PHONY: build install uninstall