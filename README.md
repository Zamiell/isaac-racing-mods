# Isaac Racing Mods
##### A collection of racing mods for The Binding of Isaac: Afterbirth

<br /><br />

**Isaac Racing Mods is now renamed to the Racing+ mod. You can find more information about it at [the official website](https://isaacracing.net).**

## Download & Additional Information

Please visit [the website for the Isaac Racing Mods](https://zamiell.github.io/isaac-racing-mods/).

<br />

## Running from Source (for developers)

* `python --version` (to confirm that you are using Python 3.x)
* `pip install psutil`
* `pip install pillow`
* `cd isaac-racing-mods/program`
* `nano ../options.ini` (set `isaac_resources_directory` equal to your resources directory)
* `python program.py` (`program.py` is the actual program and `isaac-racing-mods.py` is the automatic updater)

<br />

## Building from Source (for developers)

Building from source has only been tested on Windows.

* `python --version` (to confirm that you are using Python 3.x)
* `pip install pyinstaller`
* `cd isaac-racing-mods`
* `python build.py` (will make a subdirectory called `release`)
