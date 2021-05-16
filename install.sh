#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[1;91mERROR\033[0m: Please run as root"
    exit
fi

echo -e "\033[1mChecking dependencies...\033[0m"
command -v python3 > /dev/null || { echo -e "\033[1;91mERROR\033[0m: Python 3 is not installed on your system (install package python3)"; exit 1; }
command -v pip3 > /dev/null || { echo -e "\033[1;91mERROR\033[0m: pip3 (package installer for Python) is not installed on your system (install package python3-pip)"; exit 1; }
command -v spotify > /dev/null || echo -e "\033[1;33mWARN\033[0m: Spotify is not installed on your system. This tool is pretty useless without it, isn't it?"
command -v pactl > /dev/null || echo -e "\033[1;33mWARN\033[0m: pactl (PulseAudio control) was not found, some features might not work"

echo -e "\033[1mInstalling python packages...\033[0m"
pip3 install pygobject psutil watchdog requests configupdater lxml beautifulsoup4

echo -e "\033[1mCopying files...\033[0m"
chmod +x spotifytools
chmod +x spotifytools.desktop
chmod +x src/main.py
chmod +x uninstall.sh

rm -rf /opt/spotifytools/
mkdir -p /opt/spotifytools/

cp -a spotifytools /usr/bin/
cp -a spotifytools.desktop /usr/share/applications/
cp -a src/. uninstall.sh version /opt/spotifytools/

if [ ! -d /usr/share/icons/hicolor/scalable/apps/ ]; then
    mkdir -p /usr/share/icons/hicolor/scalable/apps/
fi

cp -a src/assets/spotifytools.svg /usr/share/icons/hicolor/scalable/apps/

echo -e "\033[1mUpdating icon cache...\033[0m"
gtk-update-icon-cache

echo -e "\033[32;1mDone!\033[0m"