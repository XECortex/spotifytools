#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[1;91mERROR\033[0m: Please run as root"
    exit
fi

echo -e "\033[1mUninstalling...\033[0m"
rm -rf /opt/spotifytools/
unlink /usr/bin/spotifytools
unlink /usr/share/applications/spotifytools.desktop
unlink /usr/share/icons/hicolor/scalable/apps/spotifytools.svg

echo -e "\033[32;1mDone!\033[0m"