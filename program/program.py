#! C:\Python35\python.exe

# TODO
# - mega satan on instant start
# - instant start logo
# - implement crash log like item tracker does

# Notes:
# - D: && cd D:\Repositories\isaac-racing-mods\program
# - pep8 --first --ignore=E501 program.py

# Imports
import sys                    # To handle generic error catching
import tkinter                # We use TKinter to draw the GUI
import tkinter.messagebox     # This is not automatically imported above
import tkinter.filedialog     # This is not automatically imported above
import os                     # For various file operations (1/2)
import shutil                 # For various file operations (2/2)
import configparser           # For parsing options.ini
import psutil                 # For finding and killing the running Isaac process
import webbrowser             # For automatically launching Isaac
import subprocess             # For restarting the program
import time                   # For finding the Epoch timestamp
import xml.etree.ElementTree  # For parsing the game's XML files (and builds.xml)
import random                 # For getting a random start
from PIL import Image, ImageFont, ImageDraw, ImageTk  # For drawing things on the title and character screen

# Configuration
mod_pretty_name = 'Isaac Racing Mods'
mod_name = 'isaac-racing-mods'
jud6s_version = '1.24'

# Global variables
items_icons_path = 'images/collectibles/'
trinket_icons_path = 'images/trinkets/'
icon_zoom = 1.3
icon_filter = Image.BILINEAR
raw_image_library = {}  # Item images library

# Parse builds.xml and items.xml
builds = xml.etree.ElementTree.parse('xml/builds.xml').getroot()  # This file contains all of the predetermined starts for the mod
items_xml = xml.etree.ElementTree.parse('xml/items.vanilla.xml')  # This needs to be parsed now so that we can display the practice window; it will be parsed again before installation
items_info = items_xml.getroot()


############################
# General purpose functions
############################

def error(error_description, exception):
    error_message = error_description
    if exception is not None:
        error_message += '\n\n'
        for i in exception:
            error_message += str(i) + '\n'
    tkinter.messagebox.showerror('Error', error_message)
    exit()


def warning(warning_description, exception):
    warning_message = warning_description
    if exception is not None:
        warning_message += '\n\n'
        for i in exception:
            warning_message += str(i) + '\n'
    tkinter.messagebox.showwarning('Warning', warning_message)


# weighted_choice - http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python
def weighted_choice(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i


##############################
# File manipulation functions
##############################

def delete_file_if_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            try:
                os.remove(path)
            except:
                error('Failed to delete the "' + path + '" file.', sys.exc_info())
        elif os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except:
                error('Failed to delete the "' + path + '" directory.', sys.exc_info())
        else:
            error('Failed to delete "' + path + '", as it is not a file or a directory.', None)


def copy_file(path1, path2):
    if not os.path.exists(path1):
        error('Copying "' + path1 + '" failed because it does not exist.', None)

    if os.path.isfile(path1):
        try:
            shutil.copyfile(path1, path2)
        except:
            error('Failed to copy the "' + path1 + '" file:', sys.exc_info())
    elif os.path.isdir(os.path.join(isaac_resources_directory, file_name)):
        try:
            shutil.copytree(path1, path2)
        except:
            error('Failed to copy the "' + path1 + '" directory:', sys.exc_info())
    else:
        error('Failed to copy "' + path1 + '", as it is not a file or a directory.', None)


def make_directory(path):
    if os.path.exists(path):
        error('Failed to create the "' + path + '" directory, as a file or directory already exists by that name.', None)

    try:
        os.makedirs(path)
    except:
        error('Failed to create the "' + path + '" directory:', sys.exc_info())


###########################
# Initialization functions
###########################

def set_custom_path():
    # Open file dialog
    user_entered_isaac_location = tkinter.filedialog.askopenfilename()

    # Check that the file is isaac-ng.exe
    if user_entered_isaac_location[-12:] != 'isaac-ng.exe':
        error('The file you selected is not called "isaac-ng.exe".', None)

    # Check that the file exists
    if not os.path.isfile(user_entered_isaac_location):
        error('The file you selected does not exist or is not a valid file.', None)

    # Derive the resources location from the location of isaac-ng.exe ("isaac-ng.exe" is 12 characters long)
    user_entered_resources_directory = os.path.join(user_entered_isaac_location[0:-12], 'resources')

    # Check that the resources directory exists
    if not os.path.isdir(user_entered_resources_directory):
        error(mod_pretty_name + ' was not able to find the "resources" directory that is supposed to live next to "isaac-ng.exe".', None)

    # Write the new path to the INI file
    mod_options.set('options', 'isaacresourcesdirectory', user_entered_resources_directory)
    try:
        with open(os.path.join('..', 'options.ini'), 'w') as config_file:
            mod_options.write(config_file)
    except:
        error('Failed to write the new directory path to the "options.ini" file:', sys.exc_info())

    # Alert the user
    tkinter.messagebox.showinfo('Success', 'You have successfully set your Isaac resources directory.\nClick OK to restart ' + mod_pretty_name + '.')

    # Restart the program
    try:
        subprocess.Popen(['program.exe'])
    except:
        error(mod_pretty_name + ' was not able to automatically restart itself. Please re-run it manually.', sys.exc_info())
    exit()


#######################
# The main menu window
#######################

class ModSelectionWindow():
    def __init__(self, parent):
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/d6.ico')  # Set the GUI icon

        # Start counting rows
        row = -1

        # Select a mod
        row += 1
        select_message = tkinter.Message(self.window, justify=tkinter.CENTER, text='Select a mod:', font='font 20', width=400)
        select_message.grid(row=row, column=0, pady=5)

        # "Jud6s" button
        row += 1
        jud6s_button = tkinter.Button(self.window, text=' Jud6s (1) ', compound='left', font='font 20', width=275)
        jud6s_button.configure(command=self.show_jud6s_window)
        jud6s_button.icon = ImageTk.PhotoImage(get_item_icon('The D6'))
        jud6s_button.configure(image=jud6s_button.icon)
        jud6s_button.grid(row=row, column=0, pady=5, padx=50)
        self.window.bind('1', lambda event: jud6s_button.invoke())

        # "Instant Start" button
        row += 1
        instant_start_button = tkinter.Button(self.window, text=' Instant Start (2) ', compound='left', font='font 20', width=275)
        instant_start_button.configure(command=self.show_instant_start_window)
        instant_start_button.icon = ImageTk.PhotoImage(get_item_icon('More Options'))
        instant_start_button.configure(image=instant_start_button.icon)

        instant_start_button.grid(row=row, column=0, pady=5)
        self.window.bind('2', lambda event: instant_start_button.invoke())

        # "Diversity" button
        row += 1
        diversity_button = tkinter.Button(self.window, text=' Diversity (3) ', compound='left', font='font 20', width=275)
        diversity_button.configure(command=self.show_diversity_window)
        diversity_button.image = Image.open('images/diversity/poop.ico')
        diversity_button.icon = ImageTk.PhotoImage(diversity_button.image)
        diversity_button.configure(image=diversity_button.icon)
        diversity_button.grid(row=row, column=0, pady=5)
        self.window.bind('3', lambda event: diversity_button.invoke())

        # Spacing
        row += 1
        spacing = tkinter.Message(self.window, text='', font='font 6')
        spacing.grid(row=row, columnspan=2)

        # Uninstall mod files when the window is closed
        self.window.protocol('WM_DELETE_WINDOW', uninstall_mod)

        # Place the window in the center of the screen
        self.window.deiconify()  # Show the GUI
        self.window.update_idletasks()  # Update the GUI
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.window.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

    def show_jud6s_window(self):
        self.window.destroy()
        Jud6sWindow(self.parent)

    def show_instant_start_window(self):
        self.window.destroy()
        InstantStartWindow(self.parent)

    def show_diversity_window(self):
        self.window.destroy()
        DiversityWindow(self.parent)


#######################
# The Jud6s Mod window
#######################

class Jud6sWindow():
    def __init__(self, parent):
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title('Jud6s Mod v' + jud6s_version)  # Set the GUI title
        self.window.iconbitmap('images/d6.ico')  # Set the GUI icon

        # Start counting rows
        row = -1

        # Select a mod
        row += 1
        select_message = tkinter.Message(self.window, justify=tkinter.CENTER, text='Select a ruleset:', font='font 20', width=400)
        select_message.grid(row=row, column=0, pady=5)

        # 1 - "Normal (Unseeded)" button
        row += 1
        ruleset1_button = tkinter.Button(self.window, text=' Normal / Unseeded (1) ', compound='left', font='font 13', width=350)
        ruleset1_button.configure(command=lambda: self.install_jud6s_mod(1))
        ruleset1_button.icon = ImageTk.PhotoImage(get_item_icon('The D6'))
        ruleset1_button.configure(image=ruleset1_button.icon)
        ruleset1_button.grid(row=row, column=0, pady=5, padx=50)
        self.window.bind('1', lambda event: ruleset1_button.invoke())

        # 2 - "Seeded" button
        row += 1
        ruleset2_button = tkinter.Button(self.window, text=' Seeded (2) ', compound='left', font='font 13', width=350)
        ruleset2_button.configure(command=lambda: self.install_jud6s_mod(2))
        ruleset2_button.icon = ImageTk.PhotoImage(get_item_icon('The Compass'))
        ruleset2_button.configure(image=ruleset2_button.icon)
        ruleset2_button.grid(row=row, column=0, pady=5)
        self.window.bind('2', lambda event: ruleset2_button.invoke())

        # 3 - "Dark Room" button
        row += 1
        ruleset3_button = tkinter.Button(self.window, text=' Dark Room (3) ', compound='left', font='font 13', width=350)
        ruleset3_button.configure(command=lambda: self.install_jud6s_mod(3))
        ruleset3_button.icon = ImageTk.PhotoImage(get_item_icon('The Negative'))
        ruleset3_button.configure(image=ruleset3_button.icon)
        ruleset3_button.grid(row=row, column=0, pady=5)
        self.window.bind('3', lambda event: ruleset3_button.invoke())

        # 4 - "The Lost Child Open Loser's Bracket" button
        row += 1
        ruleset4_button = tkinter.Button(self.window, text=' The Lost Child Open Loser\'s Bracket (4) ', compound='left', font='font 13', width=350)
        ruleset4_button.configure(command=lambda: self.install_jud6s_mod(4))
        ruleset4_button.icon = ImageTk.PhotoImage(get_item_icon('Judas\' Shadow'))
        ruleset4_button.configure(image=ruleset4_button.icon)
        ruleset4_button.grid(row=row, column=0, pady=5)
        self.window.bind('4', lambda event: ruleset4_button.invoke())

        # 5 - "Mega Satan" button
        row += 1
        ruleset5_button = tkinter.Button(self.window, text=' Mega Satan (5) ', compound='left', font='font 13', width=350)
        ruleset5_button.configure(command=lambda: self.install_jud6s_mod(5))
        ruleset5_button.icon = ImageTk.PhotoImage(get_item_icon('Key Piece 1'))
        ruleset5_button.configure(image=ruleset5_button.icon)
        ruleset5_button.grid(row=row, column=0, pady=5)
        self.window.bind('5', lambda event: ruleset5_button.invoke())

        # Spacing
        row += 1
        spacing = tkinter.Message(self.window, text='', font='font 10')
        spacing.grid(row=row)

        # "Go Back" button
        row += 1
        go_back_button = tkinter.Button(self.window, text=' Go Back (6) ', compound='left', command=self.show_mod_selection_window, font='font 13')
        go_back_button.grid(row=row, column=0, pady=5)
        self.window.bind('6', lambda event: go_back_button.invoke())

        # Spacing
        row += 1
        spacing = tkinter.Message(self.window, text='', font='font 6')
        spacing.grid(row=row)

        # Uninstall mod files when the window is closed
        self.window.protocol('WM_DELETE_WINDOW', uninstall_mod)

        # Place the window in the center of the screen
        self.window.deiconify()  # Show the GUI
        self.window.update_idletasks()  # Update the GUI
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_x = (screen_width / 2) - (window_width / 2)
        window_y = (screen_height / 2) - (window_height / 2)
        self.window.geometry('%dx%d+%d+%d' % (window_width, window_height, window_x, window_y))

    def show_mod_selection_window(self):
        self.window.destroy()
        ModSelectionWindow(self.parent)

    def install_jud6s_mod(self, ruleset):
        # Remove everything from the resources directory EXCEPT the "packed" directory and config.ini
        for file_name in os.listdir(isaac_resources_directory):
            if file_name != 'packed' and file_name != 'config.ini':
                delete_file_if_exists(os.path.join(isaac_resources_directory, file_name))

        # If there isn't a config.ini in the resources directory already, copy over the default Jud6s one
        if not os.path.isfile(os.path.join(isaac_resources_directory, 'config.ini')):
            copy_file('other-files/config.ini', os.path.join(isaac_resources_directory, 'config.ini'))

        # Copy over the "jud6s" directory, which represents the base files for the mod
        for file_name in os.listdir('jud6s'):
            copy_file(os.path.join('jud6s', file_name), os.path.join(isaac_resources_directory, file_name))

        # Prepare the font for writing to the title screens later
        if ruleset != 1:
            large_font = ImageFont.truetype('IsaacSans.ttf', 19)
            small_font = ImageFont.truetype('IsaacSans.ttf', 15)
            title_img = Image.open('jud6s-extra/titlemenu-base.png')
            title_draw = ImageDraw.Draw(title_img)
            title_screen_text = 'Jud6s Mod ' + jud6s_version

        # 1 - Normal / Unseeded
        if ruleset == 1:
            pass  # This requires no additional files

        # 2 - Seeded
        elif ruleset == 2:
            # Define the ruleset name
            ruleset_name = 'Ruleset 2 - Seeded'

            # The custom angel
            copy_file('jud6s-extra/' + ruleset_name + '/entities2.xml', os.path.join(isaac_resources_directory, 'entities2.xml'))

            # The removed unseeded items
            copy_file('jud6s-extra/' + ruleset_name + '/itempools.xml', os.path.join(isaac_resources_directory, 'itempools.xml'))

            # The removed trinket
            copy_file('jud6s-extra/' + ruleset_name + '/items.xml', os.path.join(isaac_resources_directory, 'items.xml'))

            # The added starting items
            copy_file('jud6s-extra/' + ruleset_name + '/players.xml', os.path.join(isaac_resources_directory, 'players.xml'))

            # The custom angel rooms
            copy_file('jud6s-extra/' + ruleset_name + '/rooms/00.special rooms.stb', os.path.join(isaac_resources_directory, 'rooms/00.special rooms.stb'))

            # Draw a title screen and save it overtop the old title screen
            title_draw.text((345, 239), title_screen_text, (134, 86, 86), font=large_font)
            title_draw.text((342, 256), ruleset_name, (134, 86, 86), font=small_font)
            title_img.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/titlemenu.png'))

        # 3 - Dark Room
        elif ruleset == 3:
            # Define the ruleset name
            ruleset_name = 'Ruleset 3 - Dark Room'

            # The removed shovel
            copy_file('jud6s-extra/' + ruleset_name + '/itempools.xml', os.path.join(isaac_resources_directory, 'itempools.xml'))

            # The custom beam of light
            copy_file('jud6s-extra/' + ruleset_name + '/gfx/effects', os.path.join(isaac_resources_directory, 'gfx/effects'))

            # The custom Polaroid and Negative
            copy_file('jud6s-extra/' + ruleset_name + '/gfx/items', os.path.join(isaac_resources_directory, 'gfx/items'))

            # Draw a title screen and save it overtop the old title screen
            title_draw.text((345, 239), title_screen_text, (134, 86, 86), font=large_font)
            title_draw.text((333, 256), ruleset_name, (134, 86, 86), font=small_font)
            title_img.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/titlemenu.png'))

        # 4 - The Lost Child Open Loser's Bracket
        elif ruleset == 4:
            # Define the ruleset name
            ruleset_name = 'Ruleset 4 - LCO Loser\'s Bracket'

            # The removed shovel
            copy_file('jud6s-extra/' + ruleset_name + '/itempools.xml', os.path.join(isaac_resources_directory, 'itempools.xml'))

            # The custom beam of light
            copy_file('jud6s-extra/' + ruleset_name + '/gfx/effects', os.path.join(isaac_resources_directory, 'gfx/effects'))

            # The custom Polaroid and Negative
            copy_file('jud6s-extra/' + ruleset_name + '/gfx/items', os.path.join(isaac_resources_directory, 'gfx/items'))

            # The changed starting items and health
            copy_file('jud6s-extra/' + ruleset_name + '/players.xml', os.path.join(isaac_resources_directory, 'players.xml'))

            # Draw a title screen and save it overtop the old title screen
            title_draw.text((345, 239), title_screen_text, (134, 86, 86), font=large_font)
            title_draw.text((342, 256), 'LCO Loser\'s Bracket', (134, 86, 86), font=small_font)  # We don't use ruleset_name here because it is too long
            title_img.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/titlemenu.png'))

        # 5 - Mega Satan
        elif ruleset == 5:
            # Define the ruleset name
            ruleset_name = 'Ruleset 5 - Mega Satan'

            # The changed Dark Room
            copy_file('jud6s-extra/' + ruleset_name + '/rooms/16.dark room.stb', os.path.join(isaac_resources_directory, 'rooms/16.dark room.stb'))

            # The changed Chest
            copy_file('jud6s-extra/' + ruleset_name + '/rooms/17.chest.stb', os.path.join(isaac_resources_directory, 'rooms/17.chest.stb'))

            # Draw a title screen and save it overtop the old title screen
            title_draw.text((345, 239), title_screen_text, (134, 86, 86), font=large_font)
            title_draw.text((322, 256), ruleset_name, (134, 86, 86), font=small_font)
            title_img.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/titlemenu.png'))

        # If Isaac is running, kill it
        try:
            for process in psutil.process_iter():
                if process.name() == 'isaac-ng.exe':
                    process.kill()
        except:
            error(mod_pretty_name + ' could not automatically close Isaac:', sys.exc_info())

        # Start Isaac
        try:
            webbrowser.open('steam://rungameid/250900')
        except:
            warning(mod_pretty_name + ' was not able to automatically start Isaac:', sys.exc_info())


###############################
# The Instant Start Mod window
###############################

class InstantStartWindow():
    def __init__(self, parent):
        # Class variables
        self.starting_build = 1  # Default to build #1

        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title('Jud6s Mod v' + jud6s_version)  # Set the GUI title
        self.window.iconbitmap('images/d6.ico')  # Set the GUI icon

        # Start counting rows
        row = -1

        # "Choose a Start" button
        row += 1
        choose_start_button = tkinter.Button(self.window, text=' Choose a Start (1) ', compound='left', font='font 16')
        choose_start_button.configure(command=lambda: choose_start_window(self.window))
        choose_start_button.icon = ImageTk.PhotoImage(get_item_icon('More Options'))
        choose_start_button.configure(image=choose_start_button.icon)
        choose_start_button.grid(row=row, column=0, pady=5)
        self.window.bind('1', lambda event: choose_start_button.invoke())

        # "Random Start" button
        row += 1
        random_start_button = tkinter.Button(self.window, text=' Random Start (2) ', compound='left', font='font 16')
        random_start_button.configure(command=self.install_mod)
        random_start_button.icon = ImageTk.PhotoImage(get_item_icon('???'))
        random_start_button.configure(image=random_start_button.icon)
        random_start_button.grid(row=row, column=0, pady=5)
        self.window.bind('2', lambda event: random_start_button.invoke())

        # Seeded checkbox
        row += 1
        seeded_mode = tkinter.IntVar()
        seeded_checkbox = tkinter.Checkbutton(self.window, justify=tkinter.CENTER, text='Seeded (3)', font='font 14', variable=seeded_mode)
        seeded_checkbox.grid(row=row, column=0, columnspan=2, pady=5)
        self.window.bind('3', lambda event: seeded_checkbox.invoke())

        # LCO checkbox
        row += 1
        LCO_mode = tkinter.IntVar()
        LCO_checkbox = tkinter.Checkbutton(self.window, justify=tkinter.CENTER, text='Lost Child Open (4)', font='font 14', variable=LCO_mode)
        LCO_checkbox.grid(row=row, column=0, columnspan=2, pady=5)
        self.window.bind('4', lambda event: LCO_checkbox.invoke())

        # Mega Satan checkbox
        row += 1
        mega_satan_mode = tkinter.IntVar()
        mega_satan_checkbox = tkinter.Checkbutton(self.window, justify=tkinter.CENTER, text='Mega Satan (5)', font='font 14', variable=mega_satan_mode)
        mega_satan_checkbox.grid(row=row, column=0, columnspan=2, pady=5)
        self.window.bind('5', lambda event: mega_satan_checkbox.invoke())

        # Spacing
        row += 1
        m = tkinter.Message(self.window, text='', font='font 7')
        m.grid(row=row, column=0)

        # Instructions
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will open when you start the mod.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Keep this program open while playing.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will return to normal when this program is closed.\n\n', font='font 13', width=400)
        m.grid(row=row, column=0)

        # Uninstall mod files when the window is closed
        self.window.protocol('WM_DELETE_WINDOW', uninstall_mod)

        # Place the window in the center of the screen
        self.window.deiconify()  # Show the GUI
        self.window.update_idletasks()  # Update the GUI
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_x = (screen_width / 2) - (window_width / 2)
        window_y = (screen_height / 2) - (window_height / 2)
        self.window.geometry('%dx%d+%d+%d' % (window_width, window_height, window_x, window_y))

    def show_mod_selection_window(self):
        self.window.destroy()
        ModSelectionWindow(self.parent)

    # Install instant start mod
    def install_mod():
        pass


###########################
# The Diversity Mod window
###########################

class DiversityWindow():
    def __init__(self, parent):
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title('Jud6s Mod v' + jud6s_version)  # Set the GUI title
        self.window.iconbitmap('images/d6.ico')  # Set the GUI icon

        # Start counting rows
        row = -1

    def show_mod_selection_window(self):
        self.window.destroy()
        ModSelectionWindow(self.parent)


################################
# "Start Selector" window stuff
################################

# get_image - Load the image from the provided path in a format suitable for Tk
def get_image(path):
    from os import sep

    image = raw_image_library.get(path)
    if image is None:
        canonicalized_path = path.replace('/', sep).replace('\\', sep)
        image = Image.open(canonicalized_path)
        raw_image_library[path] = image
    return image


# get_item_dict - Return an item dictionary based on the provided item id or name
def get_item_dict(id):
    id = str(id)
    if id.isdigit():
        for child in items_info:
            if child.attrib['id'] == id and child.tag != 'trinket':
                return child.attrib
    else:
        for child in items_info:
            if child.attrib['name'].lower() == id.lower() and child.tag != 'trinket':
                return child.attrib


# get_item_id - Given an item name or id, return its id
def get_item_id(id):
    id = str(id)
    if id.isdigit():
        for child in items_info:
            if child.attrib['id'] == id and child.tag != 'trinket':
                return child.attrib['id']
    else:
        for child in items_info:
            if child.attrib['name'].lower() == id.lower() and child.tag != 'trinket':
                return child.attrib['id']


# get_trinket_id - Given an item name or id, return its id
def get_trinket_id(id):
    id = str(id)
    if id.isdigit():
        for child in items_info:
            if child.attrib['id'] == id and child.tag == 'trinket':
                return child.attrib['id']
    else:
        for child in items_info:
            if child.attrib['name'].lower() == id.lower() and child.tag == 'trinket':
                return child.attrib['id']


# get_item_icon - Given the name or id of an item, return its icon image
def get_item_icon(id):
    dict = get_item_dict(id)
    if dict:
        icon_file = dict['gfx']
        return get_image(items_icons_path + icon_file)
    else:
        return get_image(items_icons_path + 'questionmark.png')


# get_trinket_icon - Given the name or id of a trinket, return its icon image
def get_trinket_icon(id):
    id = str(id)
    if id.isdigit():
        for child in items_info:
            if child.attrib['id'] == id and child.tag == 'trinket':
                return get_image(trinket_icons_path + child.attrib['gfx'])
    else:
        for child in items_info:
            if child.attrib['name'].lower() == id.lower() and child.tag == 'trinket':
                return get_image(trinket_icons_path + child.attrib['gfx'])
    return get_image(trinket_icons_path + 'questionmark.png')


# get_heart_icons - Process the hearts image into the individual heart icons and return them
def get_heart_icons():
    '''
    hearts_list[0] = # Full red
    hearts_list[1] = # Half red
    hearts_list[2] = # Empty heart
    hearts_list[3] = # Left half eternal
    hearts_list[4] = # Right half eternal overlap
    hearts_list[5] = # Full soul
    hearts_list[6] = # Half soul
    hearts_list[7] = # Full black
    hearts_list[8] = # Half black
    '''
    hearts_list = [None] * 9
    hearts = Image.open('images/ui_hearts.png')

    # 16x16 left upper right lower
    for index in range(0, 9):
        left = (16 * index) % 80
        top = 0 if index < 5 else 16
        bottom = top + 16
        right = left + 16
        hearts_list[index] = hearts.crop((left, top, right, bottom))
        hearts_list[index] = hearts_list[index].resize((int(hearts_list[index].width * icon_zoom), int(hearts_list[index].height * icon_zoom)), icon_filter)
        hearts_list[index] = ImageTk.PhotoImage(hearts_list[index])
    return hearts_list


# get_hud_icons - Parse the hudpickups.png file that contains all of the pickup grahpics
def get_hud_icons():
    '''
    hud_icons[0] = # coins
    hud_icons[1] = # keys
    hud_icons[2] = # hardmode
    hud_icons[3] = # bombs
    hud_icons[4] = # golden key
    hud_icons[5] = # no achievements
    '''
    hud_icons = [None] * 6
    hud_image = Image.open('images/hudpickups.png')

    for index in range(0, 6):
        left = (16 * index) % 48
        top = 0 if index < 3 else 16
        bottom = top + 16
        right = left + 16
        hud_icons[index] = hud_image.crop((left, top, right, bottom))
        hud_icons[index] = hud_icons[index].resize((int(hud_icons[index].width * icon_zoom), int(hud_icons[index].height * icon_zoom)), icon_filter)
        hud_icons[index] = ImageTk.PhotoImage(hud_icons[index])
    return hud_icons


# choose_start_window - Display the "Start Selector" window
def choose_start_window(root):
    global p_win
    if not p_win:
        def close_window():
            global p_win
            root.bind_all('<MouseWheel>', lambda event: None)
            p_win.destroy()
            p_win = None

        def select_build(event=None, build_widget=None):
            global chosen_start
            widget = event.widget if event else build_widget
            while not hasattr(widget, 'build'):
                if widget == root:
                    return
                widget = widget._nametowidget(widget.winfo_parent())
            build = widget.build
            chosen_start = build.attrib['id']
            close_window()
            install_mod()

        # Callback for the search entry changing; will hide any builds that don't match the search.
        def search_builds(sv):
            search_term = sv.get().lower()
            for widget in build_frames:
                item_name = widget.build.attrib['id']
                try:
                    if not re.search('^' + search_term, item_name):
                        widget.grid_remove()
                    else:
                        widget.grid()
                except:
                    widget.grid()
            canvas.yview_moveto(0)

        # Callback for pressing enter in the search box: launch the topmost visible build.
        def select_search_builds():
            for child in build_frames:
                if child.winfo_manager() != '':
                    select_build(build_widget=child)
                    break

        def make_hearts_and_consumables_canvas(parent, build):
            current_canvas = Canvas(parent, bg=current_bgcolor)
            current = 0
            redhearts = build.attrib.get('redhearts')
            soulhearts = build.attrib.get('soulhearts')
            blackhearts = build.attrib.get('blackhearts')
            heartcontainers = build.attrib.get('heartcontainers')

            def add_hearts(amount, type):
                curr = current
                for i in range(0, amount):
                    widget = Label(current_canvas, bg=current_bgcolor)
                    widget.image = hearts_list[type]
                    widget.configure(image=widget.image)
                    widget.bind('<Button-1>', select_build)
                    widget.grid(column=curr % 6, row=0 if curr < 6 else 1)
                    curr += 1
                return curr

            if redhearts:
                fullreds = int(int(redhearts) / 2)
                current = add_hearts(fullreds, 0)
                if int(redhearts) % 2 == 1:
                    current = add_hearts(1, 1)
            if heartcontainers:
                current = add_hearts(int(heartcontainers) / 2, 2)
            if soulhearts:
                fullsouls = int(int(soulhearts) / 2)
                current = add_hearts(fullsouls, 5)
                if int(soulhearts) % 2 == 1:
                    current = add_hearts(1, 6)
            if blackhearts:
                fullblacks = int(int(blackhearts) / 2)
                current = add_hearts(fullblacks, 7)
                if int(blackhearts) % 2 == 1:
                    add_hearts(1, 8)
            if build.attrib.get('coins') or build.attrib.get('bombs') or build.attrib.get('keys'):
                widget = Label(current_canvas, text='     Consumables:', bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1
            if build.attrib.get('coins'):
                widget = Label(current_canvas, bg=current_bgcolor)
                widget.image = hud_list[0]
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2)
                current += 1
                widget = Label(current_canvas, text=build.attrib['coins'], bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1
            if build.attrib.get('bombs'):
                widget = Label(current_canvas, bg=current_bgcolor)
                widget.image = hud_list[3]
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2)
                current += 1
                widget = Label(current_canvas, text=build.attrib['bombs'], bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1
            if build.attrib.get('keys'):
                widget = Label(current_canvas, bg=current_bgcolor)
                widget.image = hud_list[1]
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2)
                current += 1
                widget = Label(current_canvas, text=build.attrib['keys'], bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1
            if build.attrib.get('card'):
                card_info = xml.etree.ElementTree.parse('game-files/pocketitems.xml').getroot()
                card_name = None
                for card in card_info:
                    if card.tag in ['card', 'rune'] and card.attrib['id'] == build.attrib['card']:
                        card_name = card.attrib['name']
                        break
                widget = Label(current_canvas, text='     Card: ' + card_name, bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1

            return current_canvas

        p_win = Toplevel(root)
        p_win.iconify()  # Hide the window for now so that the user doesn't see the GUI building itself
        p_win.title('Start Selector')
        p_win.resizable(False, True)
        p_win.protocol('WM_DELETE_WINDOW', close_window)
        p_win.tk.call('wm', 'iconphoto', p_win._w, ImageTk.PhotoImage(get_item_icon('More Options')))

        # Initialize the scrolling canvas
        canvas = Canvas(p_win, borderwidth=0)
        scrollbar = Scrollbar(canvas, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.configure(scrollregion=canvas.bbox('all'), width=200, height=200)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)

        # Scrolling code taken from: http://stackoverflow.com/questions/16188420/python-tkinter-scrollbar-for-frame
        imageBox = LabelFrame(canvas, borderwidth=0)
        interior_id = canvas.create_window(0, 0, window=imageBox, anchor=NW)

        # _configure_interior - Track changes to the canvas and frame width and sync them (while also updating the scrollbar)
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame
            size = (imageBox.winfo_reqwidth(), imageBox.winfo_reqheight())
            canvas.config(scrollregion='0 0 %s %s' % size)
            if imageBox.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame
                canvas.config(width=imageBox.winfo_reqwidth())
        imageBox.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if imageBox.winfo_reqwidth() != imageBox.winfo_width():
                # Update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        # _on_mousewheel - Code taken from: http://stackoverflow.com/questions/17355902/python-tkinter-binding-mousewheel-to-scrollbar
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        # Define keyboard bindings
        p_win.bind('<MouseWheel>', _on_mousewheel)
        p_win.bind('<Home>', lambda event: canvas.yview_moveto(0))
        p_win.bind('<End>', lambda event: canvas.yview_moveto(1))
        p_win.bind('<Prior>', lambda event: canvas.yview_scroll(-1, 'pages'))
        p_win.bind('<Next>', lambda event: canvas.yview_scroll(1, 'pages'))

        # Start to build the GUI window
        current_row = 0
        hearts_list = get_heart_icons()
        hud_list = get_hud_icons()
        Label(imageBox, text='Click a build to play it', font='font 32 bold').grid(row=current_row, pady=5)
        current_row += 1

        # Search label and entry box
        search_widget_space = Label(imageBox)
        Label(search_widget_space, text='Search: ').grid(row=0, column=0)
        build_search_string = tkinter.StringVar()
        build_search_string.trace('w', lambda name, index, mode, sv=build_search_string: search_builds(sv))
        build_search_entry = Entry(search_widget_space, width=12, textvariable=build_search_string)
        build_search_entry.bind('<Escape>', lambda event: event.widget.delete(0, END))
        build_search_entry.bind('<Return>', lambda event: select_search_builds())
        build_search_entry.grid(row=0, column=1)
        search_widget_space.grid(row=current_row)
        p_win.entry = build_search_entry  # Keep track of this for later
        current_row += 1

        # Build the frames
        current_bgcolor = '#949494'
        build_frames = [None] * len(builds)
        for index, child in enumerate(builds):
            # Draw dividers in between the different kinds of starts
            if index == 0:
                Message(imageBox, text='', font='font 12').grid(row=current_row)  # Spacing
                current_row += 1
                Label(imageBox, text='Treasure Room Starts', font='font 20 bold').grid(row=current_row, pady=5)
                current_row += 1
            elif index == 19:
                Message(imageBox, text='', font='font 12').grid(row=current_row)  # Spacing
                current_row += 1
                Label(imageBox, text='Devil Room Starts', font='font 20 bold').grid(row=current_row, pady=5)
                current_row += 1
            elif index == 22:
                Message(imageBox, text='', font='font 12').grid(row=current_row)  # Spacing
                current_row += 1
                Label(imageBox, text='Angel Room Starts', font='font 20 bold').grid(row=current_row, pady=5)
                current_row += 1
            elif index == 25:
                Message(imageBox, text='', font='font 12').grid(row=current_row)  # Spacing
                current_row += 1
                Label(imageBox, text='Custom Starts', font='font 20 bold').grid(row=current_row, pady=5)
                current_row += 1

            # Background color
            current_bgcolor = '#E0E0E0' if current_bgcolor == '#949494' else '#949494'

            # Draw the build frame here
            build_frame = LabelFrame(imageBox, bg=current_bgcolor)
            build_frame.bind('<Button-1>', select_build)
            build_frame.build = child
            build_frames[index] = build_frame

            # ID
            widget = Label(build_frame, text=child.attrib['id'], font='font 32 bold', bg=current_bgcolor, width=2)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=0, rowspan=3)

            # Items
            widget = Label(build_frame, text='Item: ', bg=current_bgcolor)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=0, column=1, sticky=tkinter.E)
            items_frame = Canvas(build_frame)
            items = child.attrib.get('items')
            if items:
                items = items.split(' + ')
                luck_up = 0
                for i, item in enumerate(items):
                    if item == 'Lucky Foot':
                        luck_up += 1
                        continue
                    widget = Label(items_frame, bg=current_bgcolor)
                    widget.image = get_item_icon(item)
                    widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                    widget.configure(image=widget.image)
                    widget.bind('<Button-1>', select_build)
                    widget.grid(row=0, column=i)
                if luck_up > 0:
                    widget = Label(items_frame, bg=current_bgcolor)
                    widget.image = get_item_icon('Lucky Foot')
                    widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                    widget.configure(image=widget.image)
                    widget.bind('<Button-1>', select_build)
                    widget.grid(row=0, column=i + 1)
                    widget = Label(build_frame, text='x' + str(luck_up), bg=current_bgcolor)
                    widget.grid(row=0, column=i + 2)

            # Trinket (appended to the end of the items)
            trinket = child.attrib.get('trinket')
            if trinket:
                widget = Label(items_frame, bg=current_bgcolor)
                widget.image = get_trinket_icon(trinket)
                widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(row=0, column=len(items) + 1)
            items_frame.grid(row=0, column=2, sticky=tkinter.W)

            # Health (currently commented out since all builds will start with default health)
            '''
            widget = Label(build_frame, text='Health: ', bg=current_bgcolor)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=1, column=1, sticky=tkinter.E)

            hearts_and_consumables_frame = make_hearts_and_consumables_canvas(build_frame, child)
            hearts_and_consumables_frame.bind('<Button-1>', select_build)
            hearts_and_consumables_frame.grid(row=1, column=2, sticky=tkinter.W)
            '''

            # Removed Items (currently commented out since all builds will not have any removed items)
            '''
            widget = Label(build_frame, text='Removed Items: ', bg=current_bgcolor)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=2, column=1, sticky=tkinter.E)
            '''
            removed_items = child.attrib.get('removed')
            if removed_items:
                removed_items = removed_items.split(' + ')
                removed_items_frame = Canvas(build_frame, bg=current_bgcolor)
                for i, item in enumerate(removed_items):
                    widget = Label(removed_items_frame, bg=current_bgcolor)
                    widget.image = get_item_icon(item)
                    widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                    widget.configure(image=widget.image)
                    widget.bind('<Button-1>', select_build)
                    widget.grid(row=2, column=i)
                removed_items_frame.grid(row=2, column=2, sticky=tkinter.W)
            else:
                # Keep the spacing consistent by adding an empty invisible frame of the same height as an item
                Frame(build_frame, width=0, height=32, bg=current_bgcolor, borderwidth=0).grid(row=2, column=2, sticky=tkinter.W)
            build_frame.grid(row=current_row, pady=5, padx=3, sticky=tkinter.W + tkinter.E)
            current_row += 1

        # Update the window so the widgets give their actual dimensions
        p_win.update()

        # Show the window now that we are finished building the GUI
        p_win.deiconify()

        # Set the new window to appear relative to the main window (so that it doesn't appear on another monitor and so forth)
        width = imageBox.winfo_width() + scrollbar.winfo_width() + 2
        height = max(min(int(p_win.winfo_vrootheight() * 2 / 3), imageBox.winfo_height() + 4), p_win.winfo_height())
        p_win.geometry('%dx%d+%d+%d' % (width, height, root.winfo_rootx() + 50, root.winfo_rooty() + 50))
        p_win.update()  # Then update with the newly calculated height
        imageBox.grid_columnconfigure(0, minsize=imageBox.winfo_width())  # Maintain the maximum width

    # Put the focus on the entry box whenever this window is opened
    p_win.entry.focus()


########################
# Main window functions
########################

# Given two images, return one image with the two connected vertically, centered if necessary
def join_images_vertical(top, bottom):
    # Create a new image big enough to fit both of the old ones
    result = Image.new(top.mode, (max(top.width, bottom.width), top.height + bottom.height))
    middle_paste = int(result.width / 2 - top.width / 2)
    result.paste(top, (middle_paste, 0))
    middle_paste = int(result.width / 2 - bottom.width / 2)
    result.paste(bottom, (middle_paste, top.height))
    return result


# Given two images, return one image with the two connected horizontally, centered if necessary
def join_images_horizontal(left, right):
    result = Image.new(left.mode, (left.width + right.width, max(left.height, right.height)))
    middle_paste = int(result.height / 2 - left.height / 2)
    result.paste(left, (0, middle_paste))
    middle_paste = int(result.height / 2 - right.height / 2)
    result.paste(right, (left.width, middle_paste))
    return result


# Create an image containing the specified text
def create_text_image(text, font):
    img = Image.new('RGBA', (1000, 100))  # Dummy image
    w, h = ImageDraw.Draw(img).textsize(text, font=font)
    result = Image.new('RGBA', (w, h))  # Actual image, just large enough to fit the text
    ImageDraw.Draw(result).text((0, 0), text, (0, 0, 0), font=font)
    return result.resize((int(result.width / 2), int(result.height / 2)), Image.ANTIALIAS)


# Draw and return the background image listing starting and removed items for the starting room and attach it to the controls image
def draw_startroom_background(items, removed_items=None, trinket=None, id='Undefined'):
    result = None
    font = ImageFont.truetype('fonts/olden.ttf', 32)
    if removed_items:
        if len(removed_items) > 1:
            text = 'Removed Items'
        else:
            text = 'Removed Item'
        result = create_text_image(text, font)
        removed_image = None
        for item in removed_items[:10]:
            item_image = get_item_icon(item)
            removed_image = join_images_horizontal(removed_image, item_image) if removed_image else item_image
        result = join_images_vertical(result, removed_image)
        removed_image = None
        for item in removed_items[10:19]:
            item_image = get_item_icon(item)
            removed_image = join_images_horizontal(removed_image, item_image) if removed_image else item_image
        if removed_image:
            if len(removed_items) > 19:
                removed_image = join_images_horizontal(removed_image, create_text_image('+' + str(len(removed_items) - 19), font))
            result = join_images_vertical(result, removed_image)
    if items or trinket:
        items_image = None
        if items:
            luck_up = 0
            for item in items:
                if item == '46':  # Lucky Foot
                    luck_up += 1
                    continue
                item_image = get_item_icon(item)
                items_image = join_images_horizontal(items_image, item_image) if items_image else item_image
            if luck_up > 0:
                item_image = get_item_icon(46)
                items_image = join_images_horizontal(items_image, item_image) if items_image else item_image
                items_image = join_images_horizontal(items_image, create_text_image('x' + str(luck_up), font))
        if trinket:
            items_image = join_images_horizontal(items_image, get_trinket_icon(trinket)) if items_image else item_image
        result = join_images_vertical(items_image, result) if result else items_image  # Add the starting items
        if len(items) > 1:
            text = 'Starting Items'
        else:
            text = 'Starting Item'
        result = join_images_vertical(create_text_image(text, font), result)  # Add start label
        result = join_images_vertical(Image.new('RGBA', (5, 15)), result)  # Add some space

    return result


def draw_character_menu(current_build):
    # Open the character menu graphic and write the item/build on it
    color = (54, 47, 45)
    character_menu = Image.open('images/charactermenu.png')
    character_menu_draw = ImageDraw.Draw(character_menu)
    smallfont = ImageFont.truetype('fonts/comicbd.ttf', 10)
    largefont = ImageFont.truetype('fonts/comicbd.ttf', 14)
    if chosen_start == '':
        seedtext = 'Random Item'
    elif int(chosen_start) >= 26:  # Build 26 should be the first custom build
        seedtext = 'Build #' + chosen_start
    else:
        seedtext = current_build.get('items')
    w, h = character_menu_draw.textsize(mod_name + ' v' + version, font=smallfont)
    w2, h2 = character_menu_draw.textsize(seedtext, font=largefont)
    character_menu_draw.text((240 - w / 2, 31), mod_name + ' v' + version, color, font=smallfont)
    character_menu_draw.text((240 - w2 / 2, 41), seedtext, color, font=largefont)
    character_menu.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/charactermenu.png'))


def install_mod_no_start():
    global chosen_start
    chosen_start = '0'
    install_mod()


#########################
# Installation functions
#########################




def install_instant_start_mod():
    global chosen_start, seeded_mode, LCO_mode, mega_satan_mode

    # Make a custom title menu graphic that represents which options were selected
    instant_start_logo = Image.open('images/title-menu/reset-logo.png')
    r, g, b, a = instant_start_logo.split()
    instant_start_logo = Image.merge('RGB', (r, g, b))
    mask = Image.merge('L', (a,))
    title_img = Image.open('images/title-menu/titlemenu-noruleset.png')
    title_img.paste(instant_start_logo, (45, 178), mask)

    # Draw the text on it
    title_draw = ImageDraw.Draw(title_img)
    large_font = ImageFont.truetype('fonts/IsaacSans.ttf', 19)
    title_draw.text((10, 235), 'Instant Start', (134, 86, 86), font=large_font)
    title_draw.text((40, 250), 'Mod v' + version, (134, 86, 86), font=large_font)
    mode_text = '(Seeded LCO)'
    w, h = title_draw.textsize(mode_text, font=large_font)
    title_draw.text((235 - w / 2, 255), mode_text, (134, 86, 86), font=large_font)
    title_img.save('images/title-menu/titlemenu.png')

    # Remove everything from the resources directory EXCEPT the "packed" directory and config.ini
    for file_name in os.listdir(isaac_resources_directory):
        if file_name != 'packed' and file_name != 'config.ini':
            delete_file_if_exists(os.path.join(isaac_resources_directory, file_name))

    # If there isn't a config.ini in the resources directory already, copy over the default Jud6s one
    if not os.path.isfile(os.path.join(isaac_resources_directory, 'config.ini')):
        copy_file('other-files/config.ini', os.path.join(isaac_resources_directory, 'config.ini'))

    # Copy over the "jud6s" directory, which represents the base files for the mod
    for file_name in os.listdir('jud6s'):
        copy_file(os.path.join('jud6s', file_name), os.path.join(isaac_resources_directory, file_name))

    # Copy over the title menu graphic for this mod (different than the Jud6s one)
    if chosen_start != '0':
        copy_file('images/title-menu/titlemenu.png', os.path.join(isaac_resources_directory, 'gfx/ui/main menu/titlemenu.png'))

    # If this is seeded mode, copy over the special angel rooms
    if seeded_mode.get() == 1:
        # This is the custom angel rooms
        copy_file('custom-rulesets/seeded/00.special rooms.stb', os.path.join(isaac_resources_directory, 'rooms/00.special rooms.stb'))

        # This is the custom angel entity
        copy_file('custom-rulesets/seeded/entities2.xml', os.path.join(isaac_resources_directory, 'entities2.xml'))

    # If this is LCO mode, copy over the special graphics
    if LCO_mode.get() == 1:
        # Make the directories if they don't already exist
        if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/items')):
            make_directory(os.path.join(isaac_resources_directory, 'gfx/items'))
        if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/items/collectibles')):
            make_directory(os.path.join(isaac_resources_directory, 'gfx/items/collectibles'))
        if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/effects')):
            make_directory(os.path.join(isaac_resources_directory, 'gfx/effects'))

        # Copy the 3 files
        copy_file('images/dark-room/collectibles_327_thepolaroid.png', os.path.join(isaac_resources_directory, 'gfx/items/collectibles/collectibles_327_thepolaroid.png'))
        copy_file('images/dark-room/collectibles_328_thenegative.png', os.path.join(isaac_resources_directory, 'gfx/items/collectibles/collectibles_328_thenegative.png'))
        copy_file('images/dark-room/effect_007_light.png', os.path.join(isaac_resources_directory, 'gfx/effects/effect_007_light.png'))

    # The user wants no start
    if chosen_start == '0':
        current_build = xml.etree.ElementTree.Element('build')  # Set current_build to an empty XML element, i.e. <build />

    # The user wants a specific build
    elif chosen_start != '':
        current_build = None
        for build in builds:
            if build.attrib['id'] == chosen_start:
                current_build = build
                break

    # The user wants a random start
    else:
        random.seed()
        build_weights = [float(build.attrib['weight']) for build in builds]
        current_build = builds[weighted_choice(build_weights)]

    # Do a fresh parse of a Jud6s players.xml, items.xml, and itempools.xml, so that it isn't influenced from a previous start
    players_xml = xml.etree.ElementTree.parse('jud6s/players.xml')
    players_info = players_xml.getroot()
    items_xml = xml.etree.ElementTree.parse('xml/items.vanilla.xml')
    items_info = items_xml.getroot()
    itempools_xml = xml.etree.ElementTree.parse('xml/itempools.vanilla.xml')
    itempools_info = itempools_xml.getroot()

    # Parse the build info
    items = current_build.get('items')
    trinket = current_build.get('trinket')
    removed_items = current_build.get('removed')
    redhearts = current_build.get('redhearts')
    soulhearts = current_build.get('soulhearts')
    blackhearts = current_build.get('blackhearts')
    heartcontainers = current_build.get('heartcontainers')
    keys = current_build.get('keys')
    coins = current_build.get('coins')
    bombs = current_build.get('bombs')
    card = current_build.get('card')
    blindfolded = current_build.get('blindfolded')

    # Remove Karma from the game (done in the Jud6s mod)
    for item in items_info:
        if item.tag == 'trinket' and item.attrib['name'] == 'Karma':
            item.attrib['achievement'] = '0'

    # Remove Cain's Eye from the game (done in the seeded Jud6s mod)
    if seeded_mode.get() == 1:
        for item in items_info:
            if item.tag == 'trinket' and item.attrib['name'] == 'Cain\'s Eye':
                item.attrib['achievement'] = '0'

    # Add starting items
    if seeded_mode.get() == 1:
        if items:
            items += ' + The Compass'
        else:
            items = 'The Compass'
    if LCO_mode.get() == 1:
        if items:
            items += ' + Judas\' Shadow'
        else:
            items = 'Judas\' Shadow'
    if items or trinket:
        if items:
            items = items.split(' + ')
        for child in players_info:
            # These are the 10 characters that can receive the D6
            characterList = ['Isaac', 'Magdalene', 'Cain', 'Judas', '???', 'Samson', 'Azazel', 'Lazarus', 'The Lost', 'Lilith']

            # Go through the 10 characters
            if child.attrib['name'] in characterList:
                # Set starting health (currently only done in LCO mode)
                if LCO_mode.get() == 1:
                    child.set('hp', '0')
                    child.set('armor', '0')

                # Set a trinket
                if trinket:
                    child.set('trinket', get_trinket_id(trinket))

                # Set the item(s)
                if items:
                    for i in range(0, len(items)):
                        items[i] = get_item_id(items[i])

                    # Add the items to the player.xml
                    for item in items:
                        id = get_item_id(item)
                        if child.attrib['items'] != '':
                            child.attrib['items'] += ','
                        child.attrib['items'] += id

                    # Remove soul hearts and black hearts from items in items.xml (normal health ups are okay)
                    for item in items_info:
                        if item.attrib['id'] in items:
                            for key in ['soulhearts', 'blackhearts']:
                                if key in item.attrib:
                                    del item.attrib[key]

                # Set pickups
                if coins:
                    child.set('coins', coins)
                if bombs:
                    child.set('bombs', bombs)
                if keys:
                    child.set('keys', keys)
                if card:
                    child.set('card', card)

                # Set blindfolded
                if blindfolded:
                    child.set('canShoot', 'false')

    # Remove items from the pools
    if seeded_mode.get() == 1:
        if removed_items:
            removed_items += ' + Pandora\'s Box + Teleport! + Undefined + The Book of Sin'
        else:
            removed_items = 'Pandora\'s Box + Teleport! + Undefined + The Book of Sin'
    if LCO_mode.get() == 1:
        if removed_items:
            removed_items += ' + We Need To Go Deeper!'
        else:
            removed_items = 'We Need To Go Deeper!'
    if removed_items:
        removed_items = removed_items.split(' + ')
        for i in range(0, len(removed_items)):
            removed_items[i] = get_item_id(removed_items[i])
        for pool in itempools_info:
            for item in pool.findall('Item'):
                if item.attrib['Id'] in removed_items:
                    pool.remove(item)

    # Set the player's health (commented out since we always want the default health)
    '''
    for child in items_info:
        if child.attrib['name'] == 'The D6':
            child.set('hearts', redhearts)
            child.set('maxhearts', str(int(redhearts) + (int(redhearts) % 2) + (int(heartcontainers) if heartcontainers else 0)))
            if soulhearts:
                child.set('soulhearts', soulhearts)
            if blackhearts:
                child.set('blackhearts', blackhearts)
    '''

    # Write the changes to the copied over XML files
    players_xml.write(os.path.join(isaac_resources_directory, 'players.xml'))
    itempools_xml.write(os.path.join(isaac_resources_directory, 'itempools.xml'))
    items_xml.write(os.path.join(isaac_resources_directory, 'items.xml'))

    # Draw the start room background and copy it over
    if chosen_start != '0':
        if not os.path.exists(os.path.join(isaac_resources_directory, 'gfx/backdrop')):
            os.mkdir(os.path.join(isaac_resources_directory, 'gfx/backdrop/'))
        if os.path.exists(os.path.join(isaac_resources_directory, 'gfx/backdrop/controls.png')):
            os.unlink(os.path.join(isaac_resources_directory, 'gfx/backdrop/controls.png'))
        draw_startroom_background(items, removed_items, trinket, current_build.attrib['id']).save(os.path.join(isaac_resources_directory, 'gfx/backdrop/controls.png'))

    # Draw the character menu background and copy it over
    if chosen_start != '0':
        draw_character_menu(current_build)

    # Reset the "chosen_start" variable
    chosen_start = ''

    # If Isaac is running, kill it
    try:
        for process in psutil.process_iter():
            if process.name() == 'isaac-ng.exe':
                process.kill()
    except:
        error(mod_pretty_name + ' could not automatically close Isaac:', sys.exc_info())

    # Start Isaac
    try:
        webbrowser.open('steam://rungameid/250900')
    except:
        error(mod_pretty_name + ' was not able to automatically start Isaac:', sys.exc_info())


def uninstall_mod():
    # Remove everything from the resources directory EXCEPT the "packed" directory and config.ini
    for file_name in os.listdir(isaac_resources_directory):
        if file_name != 'packed' and file_name != 'config.ini':
            delete_file_if_exists(os.path.join(isaac_resources_directory, file_name))

    # If we backed anything up initially when launching the program, copy it back
    if backed_up_resources_directory is True:
        # Check to see if the temporary directory still exists
        if not os.path.isdir(temp_directory):
            error('The temporary directory that ' + mod_pretty_name + ' backed up files from the resources directory to cannot be found.', None)

        # Copy the files back
        for file_name in os.listdir(temp_directory):
            copy_file(os.path.join(temp_directory, file_name), os.path.join(isaac_resources_directory, file_name))

        # Remove the temporary directory we created
        delete_file_if_exists(temp_directory)

    # Exit the program
    exit()


# This gets executed first
if __name__ == '__main__':
    # Global variables
    chosen_start = ''
    no_start = False
    p_win = None  # Keep track of whether the practice window is open

    # Initialize the root GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI
    root.iconbitmap('images/d6.ico')  # Set the GUI icon
    root.title(mod_pretty_name)  # Set the GUI title

    # Validate that options.ini exists and contains the values we need
    if not os.path.isfile(os.path.join('..', 'options.ini')):
        error('The "options.ini" file was not found in the ' + mod_pretty_name + ' directory.\nPlease redownload this program.', None)
    mod_options = configparser.ConfigParser()
    mod_options.read(os.path.join('..', 'options.ini'))
    if not mod_options.has_section('options'):
        error('The "options.ini" file does not have an "[options]" section.\nPlease redownload this program.', None)
    if 'modversion' not in mod_options['options']:  # configparser defaults everything to lowercase
        error('The "options.ini" does not contain the version number of the mod.\nTry adding "modversion = 3.0.0" or redownloading the program.', None)
    if 'isaacresourcesdirectory' not in mod_options['options']:  # configparser defaults everything to lowercase
        error('The "options.ini" does not contain an entry for the location of your Isaac resources directory.\nTry adding "isaacresourcesdirectory = C:\Program Files (x86)\Steam\SteamApps\common\The Binding of Isaac Rebirth\resources" or redownloading the program.', None)

    # Get the version number of the mod and the Isaac resources path from options.ini
    mod_version = mod_options['options']['modversion']
    root.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title again now that we know the version
    isaac_resources_directory = mod_options['options']['isaacresourcesdirectory']

    # Check to see if the resources directory exists
    if not os.path.isdir(isaac_resources_directory):
        unable_to_find_message = tkinter.Message(root, justify=tkinter.CENTER, font='font 10', text=mod_pretty_name + ' was unable to find your Isaac resources directory.\nNavigate to the program "isaac-ng.exe" in your Steam directory.', width=600)
        unable_to_find_message.grid(row=0, pady=10)

        navigate_button = tkinter.Button(root, font='font 12', text='Navigate to "isaac-ng.exe"', command=set_custom_path)
        navigate_button.grid(row=2, pady=10)

        example_message = tkinter.Message(root, justify=tkinter.LEFT, font='font 10', text='Example location:\nC:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\isaac-ng.exe', width=800)
        example_message.grid(row=3, padx=15, pady=10)

        # Show the GUI
        root.deiconify()
        tkinter.mainloop()

    # Check if we are inside the resources path
    if os.path.normpath(isaac_resources_directory).lower() in os.path.normpath(os.getcwd()).lower():
        error(mod_pretty_name + ' is located in a subdirectory of the resources directory.\nMove it elsewhere before running it.', None)

    # See if the resources directory has anything in it that we need to back up
    backed_up_resources_directory = False
    for file_name in os.listdir(isaac_resources_directory):
        if file_name != 'packed' and file_name != 'config.ini':
            backed_up_resources_directory = True
            break

    # If necessary, move everything in the resources directory to a temporarily directory until the mod is closed
    if backed_up_resources_directory:
        # Create a temporarily directory
        epoch_time = str(int(time.time()))  # Get the current epoch timestamp
        temp_directory = os.path.join(isaac_resources_directory, '..', 'resources_backup' + epoch_time)
        delete_file_if_exists(temp_directory)
        os.makedirs(temp_directory)

        # Copy all files EXCEPT for the "packed" directory and config.ini
        for file_name in os.listdir(isaac_resources_directory):
            if file_name != 'packed' and file_name != 'config.ini':
                copy_file(os.path.join(isaac_resources_directory, file_name), os.path.join(temp_directory, file_name))

    # Show the mod selection GUI
    ModSelectionWindow(root)
    root.mainloop()
