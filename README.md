# SpotifyTools - <i>v1.8</i>
A GTK application written in Python that displays song lyrics and mutes Spotify advertisements

## Installation
  1. Clone the repository: `git clone https://github.com/XECortex/spotifytools.git && cd spotifytools`

  2. Install dependencies: `pip install -r requirements.txt`. You also need Python 3, Spotify and PulseAudio or PipewirePulse installed on your System

  3. Run the install script: `sh install.sh`

If there are updates available, run `git pull` in the SpotifyTools directory

## Usage
Use the desktop launcher or run `main.py` with `python3`

```
usage: spotifytools [-h] [-l] [-t]

optional arguments:
  -h, --help            show this help message and exit
  -l, --launch-spotify  launch Spotify on program start
  -t, --tray-only       don't show the main window on startup, useful if you want to start spotifytools when you log in

flag names may change in the future
```

## Screenshots
![Screenshot](assets/screenshot.png)\
<sup>(Colors may differ with other GTK themes)</sup>
