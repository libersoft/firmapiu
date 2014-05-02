#!/bin/bash

# $1 Architettura del pc (i386, x86_64)
atena_download_driver(){
	ARCH=$1

	# Si per la versione a 64 che 32 bit
	DOWNLOAD_URL="http://www.regione.toscana.it/documents/10180/595930/smart_card.zip"
	OUT_FILE="atena.zip"

	if ! wget -q -O "$OUT_FILE" "$DOWNLOAD_URL"
	then
		return 1
	else
		echo "$OUT_FILE"
		return 0
	fi

}

# $1 path dell'archivio scaricato (uno per volta)
# $2 architettura del pc
atena_extract_driver(){
	ARCHIVE=$1
	ARCH=$2

	if [ ! "$ARCHIVE" == "atena.zip" ]
	then
		print_error "failed to find atena.zip"
		return 1
	fi

	if ! unzip -q "$ARCHIVE"
	then
		print_error "failed to unzip $ARCHIVE"
		return 1
	fi

	case "$ARCH" in
		i386)
			echo "x86/libaseCnsP11.so"
			return 0
			;;
		x86_64)
			echo "x64/libaseCnsP11.so"
			 return 0
			;;
		*)
			print_error "architecture '$ARCH' not present"
			return 1
			;;
	esac

}

# $1 Architettura del pc (i386, x86_64)
# $2 path del file scompattato (uno per volta)
# $3 path della libreria dove installare i file .so (si possono usare anche altre dir)
atena_install_driver(){
	ARCH=$1
	FILE=$2
	LIB_PATH=$3

	case "$ARCH" in
		i386)
			case "$FILE" in
				"x86/libaseCnsP11.so")
					return 0
					;;
			esac
			;;
		x86_64)
			case "$FILE" in
				"x64/libaseCnsP11.so")
					return 0
					;;
			esac
			;;
		*)
			;;
	esac

	return 0
}

