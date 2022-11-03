#! /usr/bin/env bash

work_dir=`mktemp -d`

absolute_path=$(realpath $1)

directory_name=$(dirname "${absolute_path}")
file_name=$(basename -- "${absolute_path}")

echo "Using temp directory $WORK_DIR"

echo "Creating $file_name"
cd $work_dir
/sbin/mkfs.msdos -C  "${work_dir}/${file_name}" 1440

mv "${work_dir}/${file_name}" "${absolute_path}"

rm -rf "$WORK_DIR"

