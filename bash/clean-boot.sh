#!/usr/bin/env bash

# Removes unused kernel versions from /boot directory

echo Removing old kernels.

echo Space on /boot: $(df --block-size=1M /boot | tail -1 | awk '{print $4}') MiB
KERNEL=$(uname -r)
echo You are running on kernel $KERNEL

KERNEL_LIST=$(dpkg --list | grep linux-image | awk '{ print $2 }' | sort -V | sed -n '/'$KERNEL'/q;p')

if [ -z "$KERNEL_LIST" ];
then
    echo No kernels to remove.
else
    echo The following will be removed: $KERNEL_LIST

    read -p "Continue? (y/j or n)" -n 1 -r
    echo
    if [[ $REPLY =~ ^[YyJj]$ ]]
    then
        echo Removing kernels.
        $(dpkg --list | grep linux-image | awk '{ print $2 }' | sort -V | sed -n '/'$KERNEL'/q;p'| xargs sudo apt-get -y purge)
        echo Free space on /boot: $(df --block-size=1M /boot | tail -1 | awk '{print $4}') MiB
    else
        echo Not removing kernels.
    fi
fi
