#!/bin/bash

# $1 Architettura del pc (i386, x86_64)
oberthur_download_driver(){
	ARCH=$1

	# Si per la versione a 64 che 32 bit
	DOWNLOAD_URL="http://www.pec.it/Download/Software/FirmaDigitale/MU_OBERTHUR1283_LINUX.zip"
	OUT_FILE="oberthur.zip"

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
oberthur_extract_driver(){
	ARCHIVE=$1
	ARCH=$2

	if [ ! "$ARCHIVE" == "oberthur.zip" ]
	then
		print_error "failed to find oberthur.zip"
		return 1
	fi

	if ! unzip -q "$ARCHIVE"
	then
		print_error "failed to unzip $ARCHIVE"
		return 1
	fi

	case "$ARCH" in
		i386)
			echo "32/libbit4opki.so;32/libbit4opki.so.conf"
			return 0
			;;
		x86_64)
			echo "64/libbit4opki.so;64/libbit4opki.so.conf"
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
oberthur_install_driver(){
	ARCH=$1
	FILE=$2
	LIB_PATH=$3

	case "$ARCH" in
		i386)
			case "$FILE" in
				"32/libbit4opki.so")
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
				"32/libbit4opki.so.conf")
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
			esac
			;;
		x86_64)
			case "$FILE" in
				"64/libbit4opki.so")
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
				"64/libbit4opki.so.conf")
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
			esac
			;;
		*)
			return 1
			;;
	esac

	return 0
}

