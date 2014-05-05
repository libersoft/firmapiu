#!/bin/bash

# $1 Architettura del pc (i386, x86_64)
incard_download_driver(){
	ARCH=$1

	# Si per la versione a 64 che 32 bit
	INCARD_DOWNLOAD_URL="https://www.pec.it/Download/Software/FirmaDigitale/MU_INCARD1290_LINUX.zip"
	OUT_FILE="incard.zip"

	if ! wget -q -O "$OUT_FILE" "$INCARD_DOWNLOAD_URL"
	then
		return 1
	else
		echo "$OUT_FILE"
		return 0
	fi
}

# $1 path dell'archivio scaricato (uno per volta)
# $2 architettura del pc
incard_extract_driver(){
	ARCHIVE=$1
	ARCH=$2

	if [ ! "$ARCHIVE" == "incard.zip" ]
	then
		print_error "failed to find incard.zip"
		return 1
	fi

	if ! unzip -q "$ARCHIVE"
	then
		print_error "failed to unzip $ARCHIVE"
		return 1
	fi

	case "$ARCH" in
		i386)
			echo "libbit4ipki.so;libbit4ipki.so.conf;libbit4ipki.so_pin.py"
			return 0
			;;
		x86_64)
			echo "x64/libbit4ipki.so;x64/libbit4ipki.so.conf;x64/libbit4ipki.so_pin.py"
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
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
				"libbit4ipki.so.conf")
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
				"libbit4ipki.so_pin.py")
					install "$FILE" "/usr/local/bin" || return 1
					return 0
					;;
			esac
			;;
		x86_64)
			case "$FILE" in
				"x64/libbit4ipki.so")
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
				"x64/libbit4ipki.so.conf")
					install "$FILE" "$LIB_PATH" || return 1
					return 0
					;;
				"x64/libbit4ipki.so_pin.py")
					install "$FILE" "/usr/local/bin" || return 1
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
