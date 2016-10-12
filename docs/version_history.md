# Version History

* *3.5.3* - October 11th
  * Fixed the bug where the program would crash if you cancel out of the "isaac-ng.exe" selection box.
  * The starting room graphic was slightly changed to make it look better. Thanks to Birdie0 for this.
  * The "Lost Child Open" text on the Instant Start Mod is no longer translated to avoid confusion.
  * Isaac Racing Mods has been partially translated to Russian; just select "Pусский" from the main menu.
  * Thanks to SedNegi for the French translations, CrafterLynx for the Spanish translations, and Birdie0 and Dea1h for the Russian translations.
* *3.5.2* - October 4th
  * Isaac Racing Mods has been partially translated to Spanish; just select "Español" from the main menu.
  * Fixed a bug with the automatic updater. You might have to download the new version manually if you recieve errors about a "d6_image". 
* *3.5.1* - September 30th
  * Added icons for the "Go Back" buttons.
  * Added various "About" buttons that link to documentation for the various mods.
  * Added a "Visit the website" button to the "Miscellaneous Stuff" section.
* *3.5.0* - September 19th
  * Isaac Racing Mods has been partially translated to French; just select "Français" from the main menu.
  * The keyboard hotkey for "Exit" on the main menu has been changed to Esc.
  * All of the keyboard hotkeys for "Go Back" have been changed to Esc.
* *3.4.2* - August 28th
  * Changed "EnableColorCorrection" in the default "config.ini" back to 1, since it makes the game look too dark without actually increasing performance. Thanks to Krakenos for this. (This was the only change in the Jud6s Mod v1.32.)
* *3.4.1* - August 28th
  * Fixed a bug with the "Miscellaneous Stuff" checkboxes not properly activating.
* *3.4.0* - August 28th
  * The documentation for the mod was moved from the README file (and [the GitHub repository page](https://github.com/Zamiell/jud6s)) to [a new website](https://zamiell.github.io/jud6s/).
  * A new optional checkbox has been added to the "Miscellaneous Stuff" section to prevent the program from automatically closing Isaac.
  * If something goes wrong when attempting to close Isaac, the error message will be more helpful.
  * A new optional checkbox has been added to the "Miscellaneous Stuff" section to prevent the program from removing the boss cutscenes for those who mostly speedrun instead of race.
* *3.3.1* - August 26th
  * Changed the "EnableColorCorrection" and "EnableFilter" values in the default "config.ini" to 0, as they were mistakenly set to 1. (This was the only change in the Jud6s Mod v1.31.)
  * Fixed a typo in the Pageant Boy tournament ruleset menu screen.
* *3.3.0* - August 25th
  * Added an "Exit" button to the main menu.
  * Added a "Miscellaneous Stuff" button to the main menu that contains 3 new features:
    * A button to open the Isaac game directory.
    * A button to open the Isaac directory in "Documents".
    * A button to remove all currently installed mods.
* *3.2.6* - August 21st
  * Fixed the Diversity Mod display bug with A Dollar, A Quarter, and Money = Power in the starting room.
* *3.2.5* - August 20th
  * Added the files from the Jud6s Mod v1.30.
* *3.2.4* - August 19th
  * Added the files from the Jud6s Mod v1.29.
  * Fixed the Instant Start Mod to also give the instant start item to Eve, Eden, and Keeper.
* *3.2.3* - August 1st
  * The "Pageant Boy" ruleset has been added to the choices in the Jud6s Mod menu to accommodate the upcoming tournament.
* *3.2.2* - July 26th
  * Added the files from the Jud6s Mod v1.28.
  * The Diversity Mod items are now also given to Keeper.
  * "isaac-racing-mods-without-updater.zip" is renamed to "isaac-racing-mods-patch-package.zip" to prevent confusion with new users.
* *3.2.1* - July 21st
  * Diversity Mod will now automatically capitalize the seed you enter.
  * Diversity Mod has some item synergy bans removed:
    * Tammy's Head is unbanned on Brimstone starts.
    * Monstro's Lung and Chocolate Milk are unbanned on Monstro's Lung and Chocolate Milk starts.
    * Ipecac is unbanned on Technology 2 starts.
* *3.2.0* - June 27th
  * The automatic updater now has the ability to update itself, instead of just the main program.
  * Automatic updates should be twice as fast now, since the new updater is more efficient with what it downloads.
  * Before launching the game, the program will sleep for 0.5 seconds to try and prevent the bug where the mod only gets partially installed.
  * Added the files from the Jud6s Mod v1.27.
  * The Broken Remote has been removed from the seeded ruleset.
  * A new "[Seeded+](https://github.com/Zamiell/isaac-racing-mods/blob/master/README-seeded+.md)" ruleset has been added to the Instant Start mod. This contains a modified shop pool in addition to all of the other changes in the normal seeded ruleset.
  * On the Instant Start Mod, the custom starts section is now split up between custom starts with a D6 and custom starts without a D6.
* *3.1.1* - June 5th
  * The "Don't Stop" Jud6s ruleset should work properly now.
* *3.1.0* - June 4th
  * Added the files from the Jud6s Mod v1.26.
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
