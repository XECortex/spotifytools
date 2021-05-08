#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo -e "\033[91mPlease run as root\033[0m"
    exit
fi

echo -e "\033[1;91mUninstalling...\033[0m"
rm -rf /opt/spotifytools/
unlink /usr/bin/spotifytools
unlink /usr/share/applications/spotifytools.desktop

echo -e "\033[1mDone!\033[0m"