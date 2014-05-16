# Mettere sempre il build prima dell'install
# NON FARE COSI
# install:
#		install -d $(BIN_DIR)
#		install src/$(EXE) $(BIN_DIR)/$(EXE)
#
# build:
# 	@echo "Nothing to build this is a simple script"

BIN_DIR = $(DESTDIR)/usr/bin
CONFIG_DIR = $(DESTDIR)/etc/firmapiu
EXE = firmapiu-cli
CONFIG = firmapiurc

build:
	@echo "Nothing to build this is a simple script"

install:
	install -d $(BIN_DIR) $(CONFIG_DIR)
	install src/$(EXE) $(BIN_DIR)/$(EXE)
	install etc/$(CONFIG) $(CONFIG_DIR)/$(CONFIG)

uninstall:
	rm $(BIN_DIR)/$(EXE)
	rm -r $(CONFIG_DIR)

.PHONY: build install uninstall
