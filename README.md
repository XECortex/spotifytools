<h1 align="center"><img src="banner.svg" width="75%"></h1>
<p align="center">
    <img src="https://img.shields.io/badge/-Python%203-grey?logo=python">
    <img src="https://img.shields.io/badge/Version-1.10.5-brightgreen">
    <a href="https://github.com/XECortex/spotifytools/blob/main/LICENSE"><img src="https://img.shields.io/badge/Licence-MIT-green"></a>
    <img src="https://img.shields.io/github/repo-size/XECortex/spotifytools?label=Repo%20size">
    <a href="https://github.com/XECortex/spotifytools/stargazers"><img src="https://img.shields.io/github/stars/XECortex/spotifytools?style=social"></a>
</p>

“A GTK application written in Python that displays song lyrics and mutes Spotify advertisements“

## Installation
The installation of this tool is pretty easy, just follow the steps below:
1. `cd` to a nice place on your system, like `/tmp`
2. Clone this repository! `git clone https://github.com/XECortex/spotifytools.git && cd spotifytools`
3. Now you can run the install script. You need to be root, so use `sudo ./install.sh`
4. Finally, you need to install one more dependency, `gir1.2-appindicator3-0.1` on Ubuntu and Debian, or `libappindicator-gtk3` on Arch or RPM based distros

You can now delete the `spotifytools` directory if you want as it is no longer needed.
## Usage
You can start the application by using the application menu launcher or the `spotifytools` command in your terminal.

<p align="center"><img src="screenshot.png"></p>
<sup>(Colors may differ with other GTK themes)</sup>

## Issues
<img src="https://img.shields.io/badge/-Please%20read%20before%20reporting%20an%20issue!-red">

### The application doesn't start
If the application doesn't start via the application menu launcher, enter `spotifytools` in your terminal. Most likely, you are **not connected to the internet**, a **dependency is missing** or the app is **already running** somewhere else (note that the application doesn't quit when you close the main window, but minimized to the system tray.).

If any dependencies are missing, try to install them (via the package manager or pip, search the web if you don't know exactly what to do).

### Spotify is not detected
Note that this app doesn't is not compatible with the Spotify web player. The AUR, Debian and Snap versions should work fine.

### Advertsiements are not muted
At the moment, only PulseAudio / PipewirePulse is supported to mute Spotify. If you use another sound system, please open an issue and tell me which one.

### Something else doesn't work
If you have an issue that is not on listed here, please open a new issue and tell me what exactly doesn't work. I then look to fix it as quickly as possible.