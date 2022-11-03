#!/usr/bin/env bash

echo Extracting all files into subdirectories

function unzip-all {
	dir='.';
	[[ ! -z "${1// }" ]] && dir=$1;
	for z in *.zip; do
		q=$(echo "$z" | cut -f 1 -d '.');
		echo "Extracting $z -> $dir/$q";
		unzip "$z" -d "$dir/$q";
	done;
}

function unrar-all {
	dir='.';
	[[ ! -z "${1// }" ]] && dir=$1;
	for z in *.rar; do
		q=$(echo "$z" | cut -f 1 -d '.');
		echo "Extracting $z -> $dir/$q";
		mkdir -p "$dir/$q"	
		unrar x "$z" "$dir/$q"; 
	done;
}

case $1 in
	rar)
		echo rar only
		unrar-all $2
		;;
	zip)
		echo zip only
		unzip-all $2
		;;
	*)
		echo default case
		unzip-all $1
		unrar-all $1
		;;
esac

