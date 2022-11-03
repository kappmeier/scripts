#! /usr/bin/env bash

#if [ $EUID != 0 ]; then
#    sudo "$0" "$@"
#    exit $?
#fi

absolute_path=$(realpath $1)
echo "Unmounting ${absolute_path}"
sudo umount /media/floppy2/

# Copy back from temp directory
tmpdir=$(dirname $(mktemp -u))
file_name=$(basename -- "${absolute_path}")
mv "${tmpdir}/${file_name}" "${absolute_path}"

