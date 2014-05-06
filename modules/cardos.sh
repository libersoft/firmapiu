#!/bin/bash

# $1 Architettura del pc (i386, x86_64)
cardos_download_driver(){
	ARCH=$1

	# Si per la versione a 64 che 32 bit
	CARDOS_32_DOWNLOAD_URL="http://www.provincia.bz.it/cartaservizi/downloads/linux/cardos.tar.gz"
	CARDOS_64_DOWNLOAD_URL="http://www.provincia.bz.it/cartaservizi/downloads/linux/cardos64.tar.gz"

	OUT_FILE="cardos.tar.gz"

	if [ "$ARCH" == "i386" ]
	then
		DOWNLOAD_URL="$CARDOS_32_DOWNLOAD_URL"
	elif [ "$ARCH" == "x86_64" ]
	then
		DOWNLOAD_URL="$CARDOS_64_DOWNLOAD_URL"
	fi

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
cardos_extract_driver(){
	ARCHIVE=$1
	ARCH=$2

	if [ ! "$ARCHIVE" == "cardos.tar.gz" ]
	then
		print_error "failed to find cardos.tar.gz"
		return 1
	fi

	if ! tar xf "$ARCHIVE"
	then
		print_error "failed to unzip $ARCHIVE"
		return 1
	fi

	# i file sono i solito per tutte le archietture
	echo "usr/local/bin/siecapin;usr/local/lib/libgmp.so.3.4.2;usr/local/lib/libgmp.so.3;usr/local/lib/libgmp.so;usr/local/lib/libces.so.1.1.5;usr/local/lib/libces.so.1;usr/local/lib/libces.so;usr/local/lib/libsiecacrd.so;usr/local/lib/libsiecadlg.so;usr/local/lib/libsiecap11.so;usr/local/lib/libsiecap15.so;usr/local/lib/libsiecacns.so;etc/sieca.conf"
	return 0

}

# $1 Architettura del pc (i386, x86_64)
# $2 path del file scompattato (uno per volta)
# $3 path della libreria dove installare i file .so (si possono usare anche altre dir)
cardos_install_driver(){
	ARCH=$1
	FILE=$2
	LIB_PATH=$3

	case "$FILE" in
		"usr/local/bin/siecapin")
				install "$FILE" "/usr/local/bin" || return 1
				return 0
				;;
		"usr/local/lib/libgmp.so.3.4.2")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libgmp.so.3")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libgmp.so")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libces.so.1.1.5")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libces.so.1")
				cp "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libces.so")
				cp "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libsiecacrd.so")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libsiecadlg.so")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libsiecap11.so")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libsiecap15.so")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"usr/local/lib/libsiecacns.so")
				install "$FILE" "$LIB_PATH" || return 1
				return 0
				;;
		"etc/sieca.conf")
				install "$FILE" "/etc" || return 1
				return 0
				;;
	esac

	return 0
}
