#Mettere sempre il build prima dell'install
# NON FARE COSI
# install:
#		install -d $(BIN_DIR)
#		install src/$(EXE) $(BIN_DIR)/$(EXE)
#
# build:
# 	@echo "Nothing to build this is a simple script"

BIN_DIR = $(DESTDIR)/usr/bin
ETC_DIR=$(DESTDIR)/etc/firmapiu
SHARE_DIR = $(DESTDIR)/usr/share/firmapiu

MODULES_DIR = $(SHARE_DIR)/modules
LIBRARY_DIR = $(SHARE_DIR)/library

EXE_CLI = firmapiu-cli
EXE_PY = firmapiu-py
EXE_GUI = firmapiu-gui
CONFIG = firmapiurc

build:
	sed -i "/^FIRMAPIU_PATH/d" bin/$(EXE_CLI) # sostituisco il path dei moduli
	sed -i "s#../usr/share/firmapiu/icons/#/usr/share/firmapiu/icons/#" bin/$(EXE_GUI)

install:
	# create directory
	install -d $(BIN_DIR) $(ETC_DIR) $(SHARE_DIR)
	install -d $(MODULES_DIR) $(LIBRARY_DIR)
	# install binary file
	install bin/$(EXE_CLI) $(BIN_DIR)
	install bin/$(EXE_GUI) $(BIN_DIR)
	install bin/$(EXE_PY) $(BIN_DIR)
	# install library and config file
	install usr/share/firmapiu/modules/*.sh $(MODULES_DIR)
	install usr/share/firmapiu/library/*.py $(LIBRARY_DIR)
	install -m644 etc/firmapiu/$(CONFIG) $(ETC_DIR)

uninstall:
	# rimuovo i file binary
	rm $(BIN_DIR)/$(EXE_CLI)
	rm $(BIN_DIR)/$(EXE_PY)
	rm $(BIN_DIR)/$(EXE_GUI)
	# rimuovo la cartella /etc/firmapiu
	rm -r $(ETC_DIR)
	# rimuovo la cartella /usr/share/firmapiu
	rm -r $(SHARE_DIR)

.PHONY: build install uninstall
