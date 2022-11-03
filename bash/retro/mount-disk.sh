#! /usr/bin/env bash

#if [ $EUID != 0 ]; then
#    sudo "$0" "$@"
#    exit $?
#fi

absolute_path=$(realpath $1)
echo "Mounting ${absolute_path}"

# Copy to temp directory
tmpdir=$(dirname $(mktemp -u))
file_name=$(basename -- "${absolute_path}")
#directory_name=$(dirname "${absolute_path}")
cp "${absolute_path}" "${tmpdir}/${file_name}"


sudo mount -o loop "${tmpdir}/${file_name}" /media/floppy2/
