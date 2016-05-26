# Diversity Mod
##### A racing mod for The Binding of Isaac: Afterbirth

<br /><br />

## Download

[Download the latest version here.](https://github.com/Zamiell/isaac-racing-mods/releases/)

<br />

## What Is It?

Diversity Mod is a mod that gives the D6 and 3 random passive items to all characters. It allows for more diversity when racing.

<br />

## How Do I Use It?

Just run the `diversitymod` program. You do not have to move any files or uninstall other mods.

<br />

## Exact Changes

* All characters start with the D6 (except for Eve, Eden, and Keeper, as it isn't possible).
* All characters start with the same 3 additional random passive items, keeping their original passive items and resources.
* Mom's Knife, Epic Fetus, and Tech X are removed from all item pools. It is still possible to start with them as one of the 3 passive items.
* D4 and D100 are removed from all item pools.
* All special items are no longer special.
* Room modifications, animations, and bug fixes are taken from [the Jud6s mod](https://github.com/Zamiell/jud6s).

<br />

## What Exactly Does the Program Do?

* When the program is run, your "resources" directory is backed up to "resources_tmp##########" (a random directory name).
* When you click "Start Diversity Mod", it moves files into your "resources" directory and automatically starts Isaac.
* Characters are assigned random items based on the seed. If no seed is provided, a random seed will be generated.
* The program must remain open for the mod to work, because it restores previously installed mods when it is closed.
* If Isaac is not in the default Steam location, the Diversity Mod program will prompt the user for the path to the game files.
* The Diversity Mod program will not work if it is inside the Rebirth resources folder.

<br />

## Known Issues

* The program is not currently compatible with Linux/Mac. (Chronometrics is working to fix this.)
* The Avast antivirus application will prevent the program from running. This is presumably because it is moving and deleting files in your "Program Files" directory. You will need to make an exception for the Diversity Mod program or disable your Avast completely.
* When the program closes unexpectedly, it leaves mod files installed. This can happen if your computer crashes or if you kill the program with Task Manager. To fix this, just clean out all of the files and folders from the Isaac "resources" directory except for the "packed" directory. Make sure you do this while the Diversity Mod program is NOT running. By default, the "resources" directory is at `C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\resources`.
* The program also creates a temporary resources folder as mentioned in the previous section. If you had other mods installed when starting the Diversity Mod program, you can recover those files from the temporary folder. If you had nothing else stored in the resources folder before starting the Diversity Mod program, you can just delete the temporary folder.

<br />

## Excluded Starting Items

Besides not being able to start with two of the same item, it is not possible to start with the following items:

* 15 - <3
* 16 - Raw Liver
* 22 - Lunch
* 23 - Dinner
* 24 - Dessert
* 25 - Breakfast
* 26 - Rotten Meat
* 29 - Moms Underwear
* 30 - Moms Heels
* 31 - Moms Lipstick
* 92 - Super Bandage
* 119 - Blood Bag
* 176 - Stem Cells
* 194 - Magic 8 Ball
* 226 - Black Lotus
* 238 - Key Piece #1
* 239 - Key Piece #2
* 253 - Magic Scab
* 258 - Missing No.
* 334 - The Body
* 339 - Safety Pin
* 344 - Match Book
* 346 - A Snack
* 355 - Mom's Pearls
* 428 - PJs

<br />

## Item Pool Bans

* If starting Soy Milk or Libra, Soy Milk and Libra are removed from all pools.
* If starting Isaac's Heart, Blood Rights are removed from all pools.
* If starting Brimstone, Tammy's Head is removed from all pools.
* If starting Monstro's Lung or Chocolate Milk, Monstro's Lung and Chocolate Milk are removed from all pools.
* If starting Ipecac or Dr. Fetus, Ipecac and Dr. Fetus are removed from all pools.
* If starting Technology 2, Ipecac is removed from all pools.
* If starting Monstro's Lung, Ipecac is removed from all pools.

<br />

## To Build From Source

* Diversity Mod uses Python 3, so make sure you are using that instead of Python 2.
* Install pyinstaller with `pip install pyinstaller`.
* Run `python build.py`.

<br />

## Version History

* *2.3.3* - April 19th, 2016
  * Fixed the bug where the link to Diversity Mod was wrong in the new version notification.
  * Fixed the bug where the version was not displayed correctly on the title screen.
* *2.3.2* - April 18th, 2016
  * Added the game files from Jud6s v1.22.
* *2.3.1* - April 15th, 2016
  * Fixed a bug with the custom resources path support where Diversity Mod was not reading from the INI file correctly.
* *2.3* - April 13th, 2016
  * Added the game files from Jud6s v1.21.
  * When populating your resources folder with files, Diversity Mod will now automatically install a config.ini if there isn't already one there. If there is, it will leave it in place.
  * Diversity Mod will now check to see if it is the latest version on launch.
* *2.2* - February 12th, 2016
  * Removed Tech X, D4, and D100 from all pools.
  * Updated the rooms from the Jud6s mod v1.17.
* *2.1* - January 17th, 2016
  * Fixed the bug where certain characters were not starting with their normal passive items.
* *2.0* - January 17th, 2016
  * Made it work with Afterbirth.
  * Added stuff from Jud6s v1.12.
  * Added more item bans.
  * Cleaned up the code a lot.
* *0.11* - August 19th, 2015
  * NOT compatible with previous versions.
  * Fixed Cain bug, so now he really can't start with two lucky feet.
* *0.9* - August 18th, 2015
  * Diversity Mod version 0.9 is NOT compatible with previous versions.
  * Brimstone is now returned to the Devil Room pool.
  * Ipecac is now returned to the Treasure Room pool.
  * If any character has Soymilk (ID330) as a starting item, Libra (ID304) is removed from the game.
  * If any character has Isaac's Heart (ID276) as a starting item, Blood Rights (ID186) is removed from the game.
  * Some characters have specific exclusions from the starting possibilities because they are redundant or irrelevant.
  * The currently installed Diversity Mod seed is actively written to diversity_seed.txt.
  * Character select screen shows "(Random)" when playing a seed that was randomly generated.
  * Randomly generated seeds are now 6 alphanumeric characters.
  * Seed uses CRC32 hashing for the seed compatibility between operating systems.
  * Unicode characters in the seed entry field become "?" upon Start.
  * Small title graphic improvement.
* *0.8* - August 18th, 2015
  * The randomly selected starting items will be different with version 0.8, so it is NOT compatible with previous versions.
  * Ipecac is now returned to the Treasure Room pool.
  * If any character has Soymilk (ID330) as a starting item, Libra (ID304) is removed from the game.
  * If any character has Isaac's Heart (ID276) as a starting item, Blood Rights (ID186) is removed from the game.
  * Some characters have specific exclusions from the starting possibilities because they are redundant or irrelevant.
  * The currently installed Diversity Mod seed is actively written to diversity_seed.txt.
  * Character select screen shows "(Random)" when playing a seed that was randomly generated.
  * Randomly generated seeds are now 6 alphanumeric characters.
  * Seed uses CRC32 hashing for the seed compatibility between operating systems.
  * Unicode characters in the seed entry field become "?" upon Start.
  * Small title graphic improvement.
* *0.7* - August 9th, 2015
  * version 0.7 is compatible with 0.6 (generates the same starting items)
  * added ability to press Enter to start without clicking the Start button
  * removed "Close Diversity Mod" button, just use the X
  * removes leading/trailing spaces from seed on Start
  * added random seed generator button
  * condensed install and restart buttons into a single button
  * added colored background to seed field, blue when entry matches installed
  * moved temporary folder to be next to the resources folder, instead of within
  * changed temporary folder name to include a random number
  * fixed title graphic to not be blurry
* *0.6* - August 3rd, 2015
  * updated title graphics and character select graphics
  * implemented file browser for user to define Rebirth resources folder when it is not automatically found
  * check if Diversity Mod is inside the resources folder, then warn and kill if it is
  * spaced code for readability
  * stopped creating version.txt
  * excluded w9xpopen.exe from final build
* *0.5* - July 31st, 2015
  * added GUI
  * added options.ini to hold custom path
  * user is prompted to provide a valid path when the program can't find their steam path
  * Diversity Mod files are removed and previous mods are restored when the program is closed
  * gave Eden 3 random passive items, but they still get a random spacebar item
* *0.41* - July 24th, 2015
  * packaged with WipeRebirthResourcesFolder for easy uninstall
* *0.4* - July 23rd, 2015
  * automatically starts (or restarts) isaac-ng.exe
  * generates a random seed when no seed is entered
  * fixed so A Quarter (ID74) is a possible starting item
  * changed to have an INCLUDE list instead of an EXCLUDE list
  * changed random starting items method to random.sample()
* *0.3* - July 21st, 2015
  * added Super Bandage (ID92), Blood Bag (ID119), Magic 8 Ball (ID194), Black Lotus (226), & The Body (ID334) to list of excluded passives
  * renamed diversitymod.txt to README.md
* *0.2* - July 21st, 2015
  * changed possible starting items to all passive items from all pools (excluding 17 boring items)
  * added version number to character select screen graphic
  * made minor changes to the prompts and text output

<br />

## Credits

* Diversity Mod was originally made by DuneAught, with help from Awerush, Hyphen-ated, Inschato, and Sillypears.
* InvaderTim updated the code for Afterbirth.
* Zamiel cleaned up the codebase.
* Chronometrics added cross-platform support.
