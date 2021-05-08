#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo -e "\033[1;91mPlease run as root\033[0m"
    exit
fi

echo -e "\033[1mInstalling dependencies...\033[0m"
python3 -m pip install pygobject watchdog requests configupdater lxml beautifulsoup4

echo -e "\033[1mSeting execute permissions...\033[0m"
chmod +x spotifytools
chmod +x spotifytools.desktop
chmod +x src/main.py
chmod +x uninstall.sh

echo -e "\033[1mCopying files...\033[0m"
if [ ! -d /opt/spotifytools/ ]; then
    mkdir /opt/spotifytools/
fi

cp -a spotifytools /usr/bin/
cp -a spotifytools.desktop /usr/share/applications/
cp -a src/. /opt/spotifytools/
cp -a version /opt/spotifytools/
cp -a uninstall.sh /opt/spotifytools/

echo -e "\033[1mDone!\033[0m"