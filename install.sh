#!/usr/bin/env sh

echo "Installing..."

# Make main.py executable
sudo chmod +x main.py

# Create the desktop launcher
echo "Generating launcher..."
touch spotifytools.desktop
truncate -s 0 spotifytools.desktop
echo -e "[Desktop Entry]\nType=Application\nName=SpotifyTools\nIcon="$(pwd)"/assets/icons/spotifytools.svg\nCategories=Audio;Music;Player;AudioVideo;\nComment=Display song lyrics and mute Spotify advertisements\nExec="$(pwd)"/main.py" >> spotifytools.desktop

# Make the launcher executable
sudo chmod +x spotifytools.desktop

# Copy the launcher to the desktop and applications directory
sudo cp spotifytools.desktop /usr/share/applications
cp spotifytools.desktop ~/Desktop

echo "Done!"
