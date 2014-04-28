#!/bin/bash

# $1 Architettura del pc (i386, x86_64)
# $2 Directory dove salvare i driver
incard_download_driver(){
	ARCH=$1
	DOWNLOAD_DIR=$2
	INCARD_DOWNLOAD_URL="https://www.pec.it/Download/Software/FirmaDigitale/MU_INCARD1290_LINUX.zip"
	DRIVER_ZIP="incard.zip"

	echo "download2"
	echo "download1"
	return 0
}

# $1 path dell'archivio scaricato (uno per volta)
incard_extract_driver(){
	ARCHIVE=$1

	case "$ARCHIVE" in
		"download1")
			echo "file1"
			echo "file2"
			;;
		"download2")
			echo "file3"
			echo "file4"
			;;
	esac

	return 0
}

# $1 Architettura del pc (i386, x86_64)
# $2 path del file scompattato (uno per volta)
incard_install_driver(){
	ARCH=$1
	FILE=$2

	case "$FILE" in
		*)
	esac

	return 0
}
