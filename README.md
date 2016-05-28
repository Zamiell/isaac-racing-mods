# Isaac Racing Mods v3.0.0
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

## Known Issues

* Some users with the Avast antivirus application installed have reported that it will prevent the program from running. This is presumably because it is moving and deleting files in your "Program Files" directory. You will need to make an exception for the Diversity Mod program or disable your Avast completely.
* When the program closes unexpectedly, it can leave mod files installed. To fix this and go back to a "vanilla" game, delete all of the files and folders in the Isaac "resources" directory except for the "packed" directory. (By default, the "resources" directory is located at `C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\resources`.)
* There are no release versions for OS X or Linux. However, the program is written in Python 3 and is cross-platform. If you have the technical know how, you can just download the source code and run the Python script directly.

<br />

## Version History

* *3.0.0* - May 28th, 2016
  * This is the first version of the combined mod package. It starts at version 3.0.0 to signify that it is a subsequent version of v2.3.3, the final standalone release of Diversity Mod.
  * The standalone versions of Instant Start Mod and Diversity Mod will no longer be maintained. For now, the standalone version of Jud6s will continue to be maintained alongside this one.
  * The Isaac Racing Mods will now automatically update if there is a new version (provided that you click the "Automatically update and launch the new version" button).
  * A new spiffy Jud6s launcher is added to the mod package.
  * A new Mega Satan mode is added to the Instant Start Mod.
  * Diversity Mod now shows the starting items and item bans on the starting room graphic, similar to what Instant Start mod does.
  * Lots of changes were done behind the scenes to clean up the code.
