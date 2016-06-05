# Isaac Racing Mods v3.1.0
##### A collection of racing mods for The Binding of Isaac: Afterbirth

<br /><br />

## Download

[Download the latest version here.](https://github.com/Zamiell/isaac-racing-mods/releases/)

<br />

## What Is It?

This is a program that contains the 3 racing mods:
* [The Jud6s Mod](https://github.com/Zamiell/jud6s)
* [Instant Start Mod](https://github.com/Zamiell/isaac-racing-mods/README-instant-start-mod.md)
* [Diversity Mod](https://github.com/Zamiell/isaac-racing-mods/README-diversity-mod.md)

It will also automatically keep everything up to date so that you don't have to be bothered downloading the latest versions over and over.

<br />

## How Do I Use It?

Run the `isaac-racing-mods` program. You do not have to move any files or uninstall other mods.

<br />

## What Exactly Does the Program Do Behind the Scenes?

* When the program is started, any important files in your "resources" directory are backed up to "resources_tmp##########" (a directory name corresponding to the current time).
* Once you select the mod you want to play, it moves files into your "resources" directory and automatically starts Isaac.
* When closed, the program will put everything in your "resources" directory back to the way it was.

<br />

## Jud6s Custom Rulesets

You can find the documentation for the "Normal / Unseeded" ruleset on [the GitHub page for the Jud6s Mod](https://github.com/Zamiell/jud6s). Occasionally, other modified rulesets are used for racing:

#### Extra Changes in the "Seeded" ruleset
* All characters start with The Compass in addition to their other items.
* Angel statues are replaced with either Uriel or Gabriel. Key Piece 1 has been placed in each Angel Room.
* Pandora's Box, Teleport!, Undefined, and Book of Sin are removed from all item pools.
* The Cain's Eye trinket is removed from the game.

#### Extra Changes in the "Dark Room" ruleset
* 4 golden chests will now spawn at the beginning of the Dark Room (instead of red chests).
* We Need To Go Deeper! is removed from all item pools.
* There are special graphics for The Polaroid, The Negative, and the beam of light that takes you to the Cathedral.

#### Extra Changes in "The Lost Child Open Loser's Bracket" ruleset
* The changes from the "Dark Room" ruleset are included in this ruleset.
* Judas starts with Judas' Shadow in addition to his other items.
* Judas starts with 0 health.

### Extra Changes in the "Mega Satan" ruleset
* Pedestals for Key Piece 1 and Key Piece 2 are placed next to the Mega Satan door.

### Extra Changes in the "Beginner" ruleset
* Judas starts with 1 red heart and 1 full soul heart instead of of 1 red heart and 1 half soul heart.

### Extra Changes in the "Don't Stop" ruleset
* A soul heart appears at the beginning of every floor.

<br />

## Known Issues

* If the program closes unexpectedly, it can leave mod files installed. To fix this and go back to a "vanilla" game, delete all of the files and folders in the Isaac "resources" directory except for the "packed" directory. (By default, the "resources" directory is located at `C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\resources`.)
* There are no release versions for OS X or Linux. However, the program is written in Python 3.4 and is cross-platform. If you have the technical know how, you can just download the source code and run the Python script directly (see below).

## Running from Source

* `python --version` (to confirm that you are using Python 3.x)
* `pip install psutil`
* `pip install pillow`
* `python program/program.py` (`program.py` is the actual program and `isaac-racing-mods.py` is the automatic updater)

## Building from Source (only tested on Windows)

* `python build.py` (will make a subdirectory called `release`)

<br />

## Version History

* *3.1.0* - June 2nd
  * Added the files for the Jud6s Mod v1.26.
  * Added a 7th option to the Jud6s launcher for "Beginners", which is the ruleset used in the Basement series of tournaments.
  * Added an 8th option to the Jud6s launcher for "Don't Stop", which is the ruleset used in one of the legs of the Real Platinum Rod relay event.
  * The mod will now permanently remember the location that you put the window. It will also work properly with multiple monitors.
  * When automatically updating, the window will no longer lock up and there is a new amazing animation.
  * When cleaning up after itself, the mod will now delete the config.ini file out of the resources folder if it wasn't there initially.
  * Diversity Mod will no longer remove any items that you happen to start with.
  * Eden now starts with 3 random items in Diversity Mod.
  * Removed the "go back" keyboard shortcut from Diversity Mod.
  * Fixed a crash with loading Diversity Mod fonts on OS X.
  * Fixed a crash when launching Isaac on OS X.
* *3.0.1* - May 28th, 2016
  * Fixed the bug with setting a custom Isaac resources folder location.
* *3.0.0* - May 28th, 2016
  * This is the first version of the combined mod package. It starts at version 3.0.0 to signify that it is a subsequent version of v2.3.3, the final standalone release of Diversity Mod.
  * The standalone versions of Instant Start Mod and Diversity Mod will no longer be maintained. For now, the standalone version of Jud6s will continue to be maintained alongside this one.
  * The Isaac Racing Mods will now automatically update if there is a new version (provided that you click the "Automatically update and launch the new version" button).
  * A new spiffy Jud6s launcher is added to the mod package.
  * A new Mega Satan mode is added to the Instant Start Mod.
  * Diversity Mod now shows the starting items and item bans on the starting room graphic, similar to what Instant Start mod does.
  * Lots of changes were done behind the scenes to clean up the code.
