#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo -e "\033[1;91mERROR\033[0m: Please run as root"
    exit
fi

echo -e "\033[1mChecking dependencies...\033[0m"
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;91mERROR\033[0m: Python 3 is not installed on your system"
    exit
fi

if ! command -v spotify &> /dev/null; then
    echo -e "\033[1;33mWARN\033[0m: Spotify is not installed on your system. This tool is pretty useless without it, isn't it?"
fi

if ! command -v pactl &> /dev/null; then
    echo -e "\033[1;33mWARN\033[0m: pactl (PulseAudio control) was not found, some features might not work"
fi

echo -e "\033[1mInstalling python packages...\033[0m"
python3 -m pip install pygobject watchdog requests configupdater lxml beautifulsoup4

echo -e "\033[1mCopying files...\033[0m"
chmod +x spotifytools
chmod +x spotifytools.desktop
chmod +x src/main.py
chmod +x uninstall.sh

rm -rf /opt/spotifytools/
mkdir /opt/spotifytools/

cp -a spotifytools /usr/bin/
cp -a spotifytools.desktop /usr/share/applications/
cp -a src/. uninstall.sh version /opt/spotifytools/

echo -e "\033[32;1mDone!\033[0m"