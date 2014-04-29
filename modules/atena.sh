#!/bin/bash

# $1 Architettura del pc (i386, x86_64)
incard_download_driver(){
	ARCH=$1

	# Si per la versione a 64 che 32 bit
	DOWNLOAD_URL_32="http://www.pec.it/Download/Software/FirmaDigitale/IDP6.23.01_LINUX32.run.tar"
	DOWNLOAD_URL_64=""
	OUT_FILE="atena.tar"

	if [ "$ARCH" == "i386" ]
	then
		if ! wget -q -O "$OUT_FILE" "$DOWNLOAD_URL_32"
		then
			return 1
		else
			echo "$OUT_FILE"
			return 0
		fi
	elif [ "$ARCH" == "x86_64" ]
	then
		if ! wget -q -O "$OUT_FILE" "$DOWNLOAD_URL_64"
		then
			return 1
		else
			echo "$OUT_FILE"
			return 0
		fi
	else
		return 1
	fi

}

# $1 path dell'archivio scaricato (uno per volta)
# $2 architettura del pc
incard_extract_driver(){
	ARCHIVE=$1
	ARCH=$2

	if [ ! "$ARCHIVE" == "atena.tar" ]
	then
		print_error "failed to find incard.zip"
		return 1
	fi

	if ! tar x "$ARCHIVE"
	then
		print_error "failed to untar"
		return 1
	fi

	case "$ARCH" in
		i386)
			echo "libbit4ipki.so"
			echo "libbit4ipki.so.conf"
			echo "libbit4ipki.so_pin.py"
			return 0
			;;
		x86_64)
			echo "x64/libbit4ipki.so"
			echo "x64/libbit4ipki.so.conf"
			echo "x64/libbit4ipki.so_pin.py"
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
incard_install_driver(){
	ARCH=$1
	FILE=$2
	LIB_PATH=$3

	case "$ARCH" in
		i386)
			case "$FILE" in
				"libbit4ipki.so")
					return 0
					;;
				"libbit4ipki.so.conf")
					return 0
					;;
				"libbit4ipki.so_pin.py")
					return 0
					;;
			esac
			;;
		x86_64)
			case "$FILE" in
				"x64/libbit4ipki.so")
					return 0
					;;
				"x64/libbit4ipki.so.conf")
					return 0
					;;
				"x64/libbit4ipki.so_pin.py")
					return 0
					;;
			esac
			;;
		*)
			;;
	esac

	return 0
}

