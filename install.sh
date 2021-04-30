#!/usr/bin/env sh

echo -e "\n\033[1mInstalling...\033[0m"

# Make main.py executable
sudo chmod +x main.py

# Create the desktop launcher
echo -e "\n\033[1mCreating launcher...\033[0m"
touch spotifytools.desktop
truncate -s 0 spotifytools.desktop
echo -e "[Desktop Entry]\nType=Application\nName=SpotifyTools\nIcon=$(pwd)/assets/icons/spotifytools.svg\nCategories=Audio;Music;Player;AudioVideo;\nComment=Display song lyrics and mute Spotify advertisements\nExec=$(pwd)/main.py" >> spotifytools.desktop

# Make the launcher executable
sudo chmod +x spotifytools.desktop

# Copy the launcher to the desktop and applications directory
sudo cp spotifytools.desktop /usr/share/applications
cp spotifytools.desktop ~/Desktop

echo -e "\033[1;32mDone!\033[0m\n\n\033[33mPlease make sure all Python dependencies are also installed.\033[0m"
