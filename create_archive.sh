#!/bin/bash

FIRMAPIU_DIR="/home/samuel/Dropbox/progettoFirmaPiu/firmapiu/"

appname="firmapiu"
version="$1"
firmapiu_directory="firmapiu"

sync_firmapiu() {
	rsync -avzh --exclude 'Makefile' "$FIRMAPIU_DIR" "/"
}

sanitize_directory() {
	directory=$1
	find "${directory}" -type f -name "*.pyc" -exec rm {} \;
	find "${directory}" -type f -name "*.pyo" -exec rm {} \;
	find "${directory}" -type f -name "*~" -exec rm {} \;
}

sanitize_directory "$firmapiu_directory"
tar czvf "${appname}-${version}.tar.gz" "$firmapiu_directory" 

