#! C:\Python35\python.exe

####################
# Isaac Racing Mods
####################

# Imports
import sys                    # For quitting the application
import traceback              # For error handling
import logging                # For logging all exceptions to a file
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
import re                     # For the search text box
import string                 # For generating a random Diversity seed (1/2)
import binascii               # For generating a random Diversity seed (2/2)
from PIL import Image, ImageFont, ImageDraw, ImageTk  # For drawing things on the title and character screen

# Configuration
mod_pretty_name = 'Isaac Racing Mods'
mod_name = 'isaac-racing-mods'
log_file = os.path.join('..', mod_name + '-error-log.txt')


############################
# General purpose functions
############################

def error(message, exception):
    # Build the error message
    if exception is not None:
        message += '\n\n'
        message += traceback.format_exc()

    # Log the error to a file
    logging.error(message)
    with open(log_file, 'a') as file:
        file.write('\n')

    # Show the error to the user
    tkinter.messagebox.showerror('Error', message)

    # Exit the program immediately
    sys.exit()


def warning(message, exception):
    # Build the warning message
    if exception is not None:
        message += '\n\n'
        message += traceback.format_exc()

    # Log the warning to a file
    logging.warning(message)
    with open(log_file, 'a') as file:
        file.write('\n')

    # Show the warning to the user
    tkinter.messagebox.showwarning('Warning', message)


def callback_error(self, *args):
    # Build the error message
    message = 'Generic error:\n\n'
    message += traceback.format_exc()

    # Log the error to a file
    logging.error(message)
    with open(log_file, 'a') as file:
        file.write('\n')

    # Show the error to the user
    tkinter.messagebox.showerror('Error', message)

    # Exit the program immediately
    sys.exit()


##############################
# File manipulation functions
##############################

def delete_file_if_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                error('Failed to delete the "' + path + '" file:', e)
        elif os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except Exception as e:
                error('Failed to delete the "' + path + '" directory:', e)
        else:
            error('Failed to delete "' + path + '", as it is not a file or a directory.', None)


def copy_file(path1, path2):
    if not os.path.exists(path1):
        error('Copying "' + path1 + '" failed because it does not exist.', None)

    if os.path.isfile(path1):
        try:
            shutil.copyfile(path1, path2)
        except Exception as e:
            error('Failed to copy the "' + path1 + '" file:', e)
    elif os.path.isdir(path1):
        try:
            shutil.copytree(path1, path2)
        except Exception as e:
            error('Failed to copy the "' + path1 + '" directory:', e)
    else:
        error('Failed to copy "' + path1 + '", as it is not a file or a directory.', None)


def create_directory(path):
    if os.path.exists(path):
        error('Failed to create the "' + path + '" directory, as a file or directory already exists by that name.', None)

    try:
        os.makedirs(path)
    except Exception as e:
        error('Failed to create the "' + path + '" directory:', e)


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
    except Exception as e:
        error('Failed to write the new directory path to the "options.ini" file:', e)

    # Alert the user
    tkinter.messagebox.showinfo('Success', 'You have successfully set your Isaac resources directory.\nClick OK to restart ' + mod_pretty_name + '.')

    # Restart the program
    try:
        subprocess.Popen(['program.exe'])
    except Exception as e:
        error(mod_pretty_name + ' was not able to automatically restart itself. Please re-run it manually.', e)
    sys.exit()


##########################
# Isaac related functions
##########################

def launch_isaac():
    # If Isaac is running, kill it
    try:
        for process in psutil.process_iter():
            if process.name() == 'isaac-ng.exe':
                process.kill()
    except Exception as e:
        error(mod_pretty_name + ' could not automatically close Isaac:', e)

    # Launch Isaac
    try:
        webbrowser.open('steam://rungameid/250900')
    except Exception as e:
        error(mod_pretty_name + ' was not able to automatically start Isaac:', e)


# Draw and return the background image for the starting room that lists starting and removed items
def draw_start_room_background(items, removed_items=None, trinket=None):
    #######################################
    # draw_start_room_background functions
    #######################################

    # Create an image containing the specified text
    def create_text_image(text, font):
        img = Image.new('RGBA', (1000, 100))  # Dummy image
        w, h = ImageDraw.Draw(img).textsize(text, font=font)
        result = Image.new('RGBA', (w, h))  # Actual image, just large enough to fit the text
        ImageDraw.Draw(result).text((0, 0), text, (0, 0, 0), font=font)
        return result.resize((int(result.width / 2), int(result.height / 2)), Image.ANTIALIAS)

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

    #######################################
    # draw_start_room_background
    #######################################

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
        self.window.iconbitmap('images/icons/the_d6.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', uninstall_mod)  # Uninstall mod files when the window is closed

        # Start counting rows
        row = 0

        # Select a mod
        select_message = tkinter.Message(self.window, justify=tkinter.CENTER, text='Select a mod:', font='font 20', width=400)
        select_message.grid(row=row, column=0, pady=5)
        row += 1

        # "Jud6s" button
        jud6s_button = tkinter.Button(self.window, text=' Jud6s (1) ', compound='left', font='font 20', width=275)
        jud6s_button.configure(command=self.show_jud6s_window)
        jud6s_button.icon = ImageTk.PhotoImage(get_item_icon('The D6'))
        jud6s_button.configure(image=jud6s_button.icon)
        jud6s_button.grid(row=row, column=0, pady=5, padx=50)
        self.window.bind('1', lambda event: jud6s_button.invoke())
        row += 1

        # "Instant Start" button
        instant_start_button = tkinter.Button(self.window, text=' Instant Start (2) ', compound='left', font='font 20', width=275)
        instant_start_button.configure(command=self.show_instant_start_window)
        instant_start_button.icon = ImageTk.PhotoImage(get_item_icon('More Options'))
        instant_start_button.configure(image=instant_start_button.icon)
        instant_start_button.grid(row=row, column=0, pady=5)
        self.window.bind('2', lambda event: instant_start_button.invoke())
        row += 1

        # "Diversity" button
        diversity_button = tkinter.Button(self.window, text=' Diversity (3) ', compound='left', font='font 20', width=275)
        diversity_button.configure(command=self.show_diversity_window)
        diversity_button.image = Image.open('images/icons/rainbow_poop_small.ico')
        diversity_button.icon = ImageTk.PhotoImage(diversity_button.image)
        diversity_button.configure(image=diversity_button.icon)
        diversity_button.grid(row=row, column=0, pady=5)
        self.window.bind('3', lambda event: diversity_button.invoke())
        row += 1

        # Spacing
        spacing = tkinter.Message(self.window, text='', font='font 6')
        spacing.grid(row=row)
        row += 1

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
        self.window.iconbitmap('images/icons/the_d6.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', uninstall_mod)  # Uninstall mod files when the window is closed

        # Start counting rows
        row = 0

        # Select a mod
        select_message = tkinter.Message(self.window, justify=tkinter.CENTER, text='Select a ruleset:', font='font 20', width=400)
        select_message.grid(row=row, column=0, pady=5)
        row += 1

        # 1 - "Normal (Unseeded)" button
        ruleset1_button = tkinter.Button(self.window, text=' Normal / Unseeded (1) ', compound='left', width=375)
        ruleset1_button.configure(font=("Helvetica", 13, "bold"))
        ruleset1_button.configure(command=lambda: self.install_jud6s_mod(1))
        ruleset1_button.icon = ImageTk.PhotoImage(get_item_icon('The D6'))
        ruleset1_button.configure(image=ruleset1_button.icon)
        ruleset1_button.grid(row=row, column=0, pady=5, padx=50)
        self.window.bind('1', lambda event: ruleset1_button.invoke())
        row += 1

        # 2 - "Seeded" button
        ruleset2_button = tkinter.Button(self.window, text=' Seeded (2) ', compound='left', width=375)
        ruleset2_button.configure(font=("Helvetica", 13, "bold"))
        ruleset2_button.configure(command=lambda: self.install_jud6s_mod(2))
        ruleset2_button.icon = ImageTk.PhotoImage(get_item_icon('The Compass'))
        ruleset2_button.configure(image=ruleset2_button.icon)
        ruleset2_button.grid(row=row, column=0, pady=5)
        self.window.bind('2', lambda event: ruleset2_button.invoke())
        row += 1

        # 3 - "Dark Room" button
        ruleset3_button = tkinter.Button(self.window, text=' Dark Room (3) ', compound='left', width=375)
        ruleset3_button.configure(font=("Helvetica", 13, "bold"))
        ruleset3_button.configure(command=lambda: self.install_jud6s_mod(3))
        ruleset3_button.icon = ImageTk.PhotoImage(get_image('jud6s-extra/Ruleset 3 - Dark Room/gfx/items/collectibles/collectibles_327_thepolaroid.png'))
        ruleset3_button.configure(image=ruleset3_button.icon)
        ruleset3_button.grid(row=row, column=0, pady=5)
        self.window.bind('3', lambda event: ruleset3_button.invoke())
        row += 1

        # 4 - "The Lost Child Open Loser's Bracket" button
        ruleset4_button = tkinter.Button(self.window, text=' The Lost Child Open Loser\'s Bracket (4) ', compound='left', width=375)
        ruleset4_button.configure(font=("Helvetica", 13, "bold"))
        ruleset4_button.configure(command=lambda: self.install_jud6s_mod(4))
        ruleset4_button.icon = ImageTk.PhotoImage(get_item_icon('Judas\' Shadow'))
        ruleset4_button.configure(image=ruleset4_button.icon)
        ruleset4_button.grid(row=row, column=0, pady=5)
        self.window.bind('4', lambda event: ruleset4_button.invoke())
        row += 1

        # 5 - "Mega Satan" button
        ruleset5_button = tkinter.Button(self.window, text=' Mega Satan (5) ', compound='left', width=375)
        ruleset5_button.configure(font=("Helvetica", 13, "bold"))
        ruleset5_button.configure(command=lambda: self.install_jud6s_mod(5))
        ruleset5_button.icon = ImageTk.PhotoImage(get_item_icon('Key Piece 1'))
        ruleset5_button.configure(image=ruleset5_button.icon)
        ruleset5_button.grid(row=row, column=0, pady=5)
        self.window.bind('5', lambda event: ruleset5_button.invoke())
        row += 1

        # "Go Back" button
        go_back_button = tkinter.Button(self.window, text=' Go Back (6) ', compound='left')
        go_back_button.configure(font=("Helvetica", 13))
        go_back_button.configure(command=self.go_back)
        go_back_button.grid(row=row, column=0, pady=25)
        self.window.bind('6', lambda event: go_back_button.invoke())
        row += 1

        # Instructions
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will open when you start the mod.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Keep this program open while playing.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will return to normal when this program is closed.\n', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1

        # Spacing
        spacing = tkinter.Message(self.window, text='', font='font 6')
        spacing.grid(row=row)
        row += 1

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
            large_font = ImageFont.truetype('fonts/IsaacSans.ttf', 19)
            small_font = ImageFont.truetype('fonts/IsaacSans.ttf', 15)
            title_img = Image.open('images/main-menu/titlemenu-base.png')
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

        # We are finished, so launch Isaac
        launch_isaac()

    def go_back(self):
        self.window.destroy()
        ModSelectionWindow(self.parent)


###############################
# The Instant Start Mod window
###############################

class InstantStartWindow():
    def __init__(self, parent):
        self.builds = xml.etree.ElementTree.parse('xml/builds.xml').getroot()

        # By default, the user is not choosing a random build
        self.random_build = False

        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title('Instant Start Mod v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/icons/more_options.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', uninstall_mod)  # Uninstall mod files when the window is closed

        # Start counting rows
        row = 0

        # Spacing
        m = tkinter.Message(self.window, text='', font='font 7')
        m.grid(row=row, column=0)
        row += 1

        # "Choose a Start" button
        choose_start_button = tkinter.Button(self.window, text=' Choose a Start (1) ', compound='left', font='font 16', width=250)
        choose_start_button.configure(command=self.show_start_selector_window)
        choose_start_button.icon = ImageTk.PhotoImage(get_item_icon('More Options'))
        choose_start_button.configure(image=choose_start_button.icon)
        choose_start_button.grid(row=row, column=0, pady=5)
        self.window.bind('1', lambda event: choose_start_button.invoke())
        row += 1

        # "Random Start" button
        random_start_button = tkinter.Button(self.window, text=' Random Start (2) ', compound='left', font='font 16', width=250)
        random_start_button.configure(command=self.get_random_start)
        random_start_button.icon = ImageTk.PhotoImage(get_item_icon('???'))
        random_start_button.configure(image=random_start_button.icon)
        random_start_button.grid(row=row, column=0, pady=5)
        self.window.bind('2', lambda event: random_start_button.invoke())
        row += 1

        # Spacing
        m = tkinter.Message(self.window, text='', font='font 7')
        m.grid(row=row, column=0)
        row += 1

        # Seeded checkbox
        self.seeded_mode = tkinter.IntVar()
        seeded_checkbox = tkinter.Checkbutton(self.window, text='Seeded (3)', font='font 14', variable=self.seeded_mode)
        seeded_checkbox.grid(row=row, column=0)
        self.window.bind('3', lambda event: seeded_checkbox.invoke())
        row += 1

        # LCO checkbox
        self.LCO_mode = tkinter.IntVar()
        LCO_checkbox = tkinter.Checkbutton(self.window, anchor=tkinter.E, text='Lost Child Open (4)', font='font 14', variable=self.LCO_mode)
        LCO_checkbox.grid(row=row, column=0)
        self.window.bind('4', lambda event: LCO_checkbox.invoke())
        row += 1

        # Mega Satan checkbox
        self.mega_satan_mode = tkinter.IntVar()
        mega_satan_checkbox = tkinter.Checkbutton(self.window, text='Mega Satan (5)', font='font 14', variable=self.mega_satan_mode)
        mega_satan_checkbox.grid(row=row, column=0)
        self.window.bind('5', lambda event: mega_satan_checkbox.invoke())
        row += 1

        # "Go Back" button
        go_back_button = tkinter.Button(self.window, text=' Go Back (6) ', compound='left')
        go_back_button.configure(font=("Helvetica", 13))
        go_back_button.configure(command=self.go_back)
        go_back_button.grid(row=row, column=0, pady=25)
        self.window.bind('6', lambda event: go_back_button.invoke())
        row += 1

        # Instructions
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will open when you start the mod.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Keep this program open while playing.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will return to normal when this program is closed.\n', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1

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

    def show_start_selector_window(self):
        #######################################
        # show_start_selector_window variables
        #######################################

        icon_zoom = 1.3
        icon_filter = Image.BILINEAR

        #######################################
        # show_start_selector_window functions
        #######################################

        # Callback for clicking on a build
        def select_build(event=None, build_widget=None):
            widget = event.widget if event else build_widget
            while not hasattr(widget, 'build'):
                if widget == self.parent:
                    return
                widget = widget._nametowidget(widget.winfo_parent())
            self.current_build = widget.build.attrib['id']
            self.install_instant_start_mod()
            go_back()

        # Callback for the search entry changing; will hide any builds that don't match the search
        def search_builds(sv):
            search_term = sv.get().lower()
            for widget in build_frames:
                item_name = widget.build.attrib['id']

                # This is enclosed in a try/except block because the user can enter regex special characters that will break the parse
                try:
                    if re.search('^' + search_term, item_name):
                        widget.grid()
                    else:
                        widget.grid_remove()
                except Exception as e:  # No builds will match a regex special character, so default to not showing anything
                    widget.grid_remove()
            canvas.yview_moveto(0)

        # Callback for pressing enter in the search box: launch the topmost visible build
        def select_search_builds():
            for child in build_frames:
                if child.winfo_manager() != '':
                    select_build(build_widget=child)
                    break

        def make_hearts_and_consumables_canvas(parent, build):
            current_canvas = tkinter.Canvas(parent, bg=current_bgcolor)
            current = 0
            redhearts = build.attrib.get('redhearts')
            soulhearts = build.attrib.get('soulhearts')
            blackhearts = build.attrib.get('blackhearts')
            heartcontainers = build.attrib.get('heartcontainers')

            def add_hearts(amount, type):
                curr = current
                for i in range(0, amount):
                    widget = tkinter.Label(current_canvas, bg=current_bgcolor)
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
                widget = tkinter.Label(current_canvas, text='     Consumables:', bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1
            if build.attrib.get('coins'):
                widget = tkinter.Label(current_canvas, bg=current_bgcolor)
                widget.image = hud_list[0]
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2)
                current += 1
                widget = tkinter.Label(current_canvas, text=build.attrib['coins'], bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1
            if build.attrib.get('bombs'):
                widget = tkinter.Label(current_canvas, bg=current_bgcolor)
                widget.image = hud_list[3]
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2)
                current += 1
                widget = tkinter.Label(current_canvas, text=build.attrib['bombs'], bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1
            if build.attrib.get('keys'):
                widget = tkinter.Label(current_canvas, bg=current_bgcolor)
                widget.image = hud_list[1]
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2)
                current += 1
                widget = tkinter.Label(current_canvas, text=build.attrib['keys'], bg=current_bgcolor)
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
                widget = tkinter.Label(current_canvas, text='     Card: ' + card_name, bg=current_bgcolor)
                widget.bind('<Button-1>', select_build)
                widget.grid(column=current, row=0, rowspan=2, sticky=tkinter.NSEW)
                current += 1

            return current_canvas

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

        # _configure_interior - Track changes to the canvas and frame width and sync them (while also updating the scrollbar)
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame
            size = (imageBox.winfo_reqwidth(), imageBox.winfo_reqheight())
            canvas.config(scrollregion='0 0 %s %s' % size)
            if imageBox.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame
                canvas.config(width=imageBox.winfo_reqwidth())

        def _configure_canvas(event):
            if imageBox.winfo_reqwidth() != imageBox.winfo_width():
                # Update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        # _on_mousewheel - Code taken from: http://stackoverflow.com/questions/17355902/python-tkinter-binding-mousewheel-to-scrollbar
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        def go_back():
            self.window2.destroy()  # Destroy the "Start Selector" window
            self.window.deiconify()  # Show the main Instant Start window

        #############################
        # show_start_selector_window
        #############################

        # Initialize a new GUI window
        self.window.withdraw()  # Hide the main Instant Start window
        self.window2 = tkinter.Toplevel(self.parent)

        self.window2.withdraw()  # Hide the GUI
        self.window2.title('Start Selector')  # Set the GUI title
        self.window2.iconbitmap('images/icons/more_options.ico')  # Set the GUI icon
        self.window2.resizable(False, True)
        self.window2.protocol('WM_DELETE_WINDOW', uninstall_mod)

        # Initialize the scrolling canvas
        canvas = tkinter.Canvas(self.window2, borderwidth=0)
        scrollbar = tkinter.Scrollbar(canvas, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.configure(scrollregion=canvas.bbox('all'), width=200, height=200)
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)

        # Scrolling code taken from: http://stackoverflow.com/questions/16188420/python-tkinter-scrollbar-for-frame
        imageBox = tkinter.LabelFrame(canvas, borderwidth=0)
        interior_id = canvas.create_window(0, 0, window=imageBox, anchor=tkinter.NW)
        imageBox.bind('<Configure>', _configure_interior)
        canvas.bind('<Configure>', _configure_canvas)

        # Define keyboard bindings
        self.window2.bind('<MouseWheel>', _on_mousewheel)
        self.window2.bind('<Home>', lambda event: canvas.yview_moveto(0))
        self.window2.bind('<End>', lambda event: canvas.yview_moveto(1))
        self.window2.bind('<Prior>', lambda event: canvas.yview_scroll(-1, 'pages'))  # PgUp
        self.window2.bind('<Next>', lambda event: canvas.yview_scroll(1, 'pages'))  # PgDn
        self.window2.bind('<Escape>', lambda event: go_back())

        # Start counting rows
        row = 0

        # Start to build the GUI window
        hearts_list = get_heart_icons()
        hud_list = get_hud_icons()
        tkinter.Label(imageBox, text='Click a build to play it', font='font 32 bold').grid(row=row, pady=5)
        row += 1

        # Search label
        search_widget_space = tkinter.Label(imageBox)
        search_label = tkinter.Label(search_widget_space, text='Search: ', font=("Helvetica", 15))
        search_label.grid(row=0, column=0)

        # Search text box
        build_search_string = tkinter.StringVar()
        build_search_string.trace('w', lambda name, index, mode, sv=build_search_string: search_builds(sv))
        self.window2.entry = tkinter.Entry(search_widget_space, font=("Helvetica", 15), width=12, textvariable=build_search_string)
        self.window2.entry.bind('<Return>', lambda event: select_search_builds())
        self.window2.entry.grid(row=0, column=1)
        self.window2.entry.focus()  # Put the focus on the entry box whenever this window is opened
        search_widget_space.grid(row=row)
        row += 1

        # "Go Back" button
        go_back_button = tkinter.Button(imageBox, text=' Go Back (Esc)', compound='left')
        go_back_button.configure(font=("Helvetica", 11))
        go_back_button.configure(command=go_back)  # Goes to nested function
        go_back_button.grid(row=row, pady=15)
        row += 1

        # Parse builds.xml
        builds = xml.etree.ElementTree.parse('xml/builds.xml').getroot()  # This file contains all of the predetermined starts for the mod

        # Build the frames
        current_bgcolor = '#949494'
        build_frames = [None] * len(builds)
        for index, child in enumerate(builds):
            # Draw dividers in between the different kinds of starts
            if index == 0:
                tkinter.Message(imageBox, text='', font='font 12').grid(row=row)  # Spacing
                row += 1
                tkinter.Label(imageBox, text='Treasure Room Starts', font='font 20 bold').grid(row=row, pady=5)
                row += 1
            elif index == 19:
                tkinter.Message(imageBox, text='', font='font 12').grid(row=row)  # Spacing
                row += 1
                tkinter.Label(imageBox, text='Devil Room Starts', font='font 20 bold').grid(row=row, pady=5)
                row += 1
            elif index == 22:
                tkinter.Message(imageBox, text='', font='font 12').grid(row=row)  # Spacing
                row += 1
                tkinter.Label(imageBox, text='Angel Room Starts', font='font 20 bold').grid(row=row, pady=5)
                row += 1
            elif index == 25:
                tkinter.Message(imageBox, text='', font='font 12').grid(row=row)  # Spacing
                row += 1
                tkinter.Label(imageBox, text='Custom Starts', font='font 20 bold').grid(row=row, pady=5)
                row += 1

            # Background color
            current_bgcolor = '#E0E0E0' if current_bgcolor == '#949494' else '#949494'

            # Draw the build frame here
            build_frame = tkinter.LabelFrame(imageBox, bg=current_bgcolor)
            build_frame.bind('<Button-1>', select_build)
            build_frame.build = child
            build_frames[index] = build_frame

            # ID
            widget = tkinter.Label(build_frame, text=child.attrib['id'], font='font 32 bold', bg=current_bgcolor, width=2)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=0, rowspan=3)

            # Items
            widget = tkinter.Label(build_frame, text='Item: ', bg=current_bgcolor)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=0, column=1, sticky=tkinter.E)
            items_frame = tkinter.Canvas(build_frame)
            items = child.attrib.get('items')
            if items:
                items = items.split(' + ')
                luck_up = 0
                for i, item in enumerate(items):
                    if item == 'Lucky Foot':
                        luck_up += 1
                        continue
                    widget = tkinter.Label(items_frame, bg=current_bgcolor)
                    widget.image = get_item_icon(item)
                    widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                    widget.configure(image=widget.image)
                    widget.bind('<Button-1>', select_build)
                    widget.grid(row=0, column=i)
                if luck_up > 0:
                    widget = tkinter.Label(items_frame, bg=current_bgcolor)
                    widget.image = get_item_icon('Lucky Foot')
                    widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                    widget.configure(image=widget.image)
                    widget.bind('<Button-1>', select_build)
                    widget.grid(row=0, column=i + 1)
                    widget = tkinter.Label(build_frame, text='x' + str(luck_up), bg=current_bgcolor)
                    widget.grid(row=0, column=i + 2)

            # Trinket (appended to the end of the items)
            trinket = child.attrib.get('trinket')
            if trinket:
                widget = tkinter.Label(items_frame, bg=current_bgcolor)
                widget.image = get_trinket_icon(trinket)
                widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                widget.configure(image=widget.image)
                widget.bind('<Button-1>', select_build)
                widget.grid(row=0, column=len(items) + 1)
            items_frame.grid(row=0, column=2, sticky=tkinter.W)

            # Health (currently commented out since all builds will start with default health)
            '''
            widget = tkinter.Label(build_frame, text='Health: ', bg=current_bgcolor)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=1, column=1, sticky=tkinter.E)

            hearts_and_consumables_frame = make_hearts_and_consumables_canvas(build_frame, child)
            hearts_and_consumables_frame.bind('<Button-1>', select_build)
            hearts_and_consumables_frame.grid(row=1, column=2, sticky=tkinter.W)
            '''

            # Removed Items (currently commented out since all builds will not have any removed items)
            '''
            widget = tkinter.Label(build_frame, text='Removed Items: ', bg=current_bgcolor)
            widget.bind('<Button-1>', select_build)
            widget.grid(row=2, column=1, sticky=tkinter.E)
            '''
            removed_items = child.attrib.get('removed')
            if removed_items:
                removed_items = removed_items.split(' + ')
                removed_items_frame = tkinter.Canvas(build_frame, bg=current_bgcolor)
                for i, item in enumerate(removed_items):
                    widget = tkinter.Label(removed_items_frame, bg=current_bgcolor)
                    widget.image = get_item_icon(item)
                    widget.image = ImageTk.PhotoImage(widget.image.resize((int(widget.image.width * icon_zoom), int(widget.image.height * icon_zoom)), icon_filter))
                    widget.configure(image=widget.image)
                    widget.bind('<Button-1>', select_build)
                    widget.grid(row=2, column=i)
                removed_items_frame.grid(row=2, column=2, sticky=tkinter.W)
            else:
                # Keep the spacing consistent by adding an empty invisible frame of the same height as an item
                tkinter.Frame(build_frame, width=0, height=32, bg=current_bgcolor, borderwidth=0).grid(row=2, column=2, sticky=tkinter.W)
            build_frame.grid(row=row, pady=5, padx=3, sticky=tkinter.W + tkinter.E)
            row += 1

        # Place the window in the center of the screen
        self.window2.deiconify()  # Show the GUI
        self.window2.update_idletasks()  # Update the GUI
        window_width = imageBox.winfo_width() + scrollbar.winfo_width() + 2
        window_height = max(min(int(self.window2.winfo_vrootheight() * 2 / 3), imageBox.winfo_height() + 4), self.window2.winfo_height())
        screen_width = self.window2.winfo_screenwidth()
        screen_height = self.window2.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.window2.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

    def show_instant_start_window(self):
        self.window2.destroy()
        InstantStartWindow(self.parent)

    def get_random_start(self):
        self.current_build = str(random.randint(1, len(self.builds)))
        self.random_build = True
        self.install_instant_start_mod()

    def install_instant_start_mod(self):
        ####################
        # Utility functions
        ####################

        def remove_item_from_all_item_pools(item_name):
            item_id = get_item_id(item_name)
            for pool in itempools_info:
                for item in pool.findall('Item'):
                    if item.attrib['Id'] == item_id:  # Weirdly, it is capitalized this way in the vanilla XML
                        pool.remove(item)

        #############################
        # The main installation code
        #############################

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

        # Make a custom title menu graphic that represents which options were selected
        self.draw_title_graphic()

        # If this is seeded mode, copy over the special angel rooms
        if self.seeded_mode.get() == 1:
            # Copy the custom angel rooms
            copy_file('jud6s-extra/Ruleset 2 - Seeded/rooms/00.special rooms.stb', os.path.join(isaac_resources_directory, 'rooms/00.special rooms.stb'))

            # Copy the custom angel entity
            copy_file('jud6s-extra/Ruleset 2 - Seeded/entities2.xml', os.path.join(isaac_resources_directory, 'entities2.xml'))

        # If this is LCO mode, copy over the special graphics
        if self.LCO_mode.get() == 1:
            # Make the directories if they don't already exist
            if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/items')):
                create_directory(os.path.join(isaac_resources_directory, 'gfx/items'))
            if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/items/collectibles')):
                create_directory(os.path.join(isaac_resources_directory, 'gfx/items/collectibles'))
            if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/effects')):
                create_directory(os.path.join(isaac_resources_directory, 'gfx/effects'))

            # Copy the 3 special graphic files
            copy_file('jud6s-extra/Ruleset 4 - LCO Loser\'s Bracket/gfx/effects/effect_007_light.png', os.path.join(isaac_resources_directory, 'gfx/effects/effect_007_light.png'))
            copy_file('jud6s-extra/Ruleset 4 - LCO Loser\'s Bracket/gfx/items/collectibles/collectibles_327_thepolaroid.png', os.path.join(isaac_resources_directory, 'gfx/items/collectibles/collectibles_327_thepolaroid.png'))
            copy_file('jud6s-extra/Ruleset 4 - LCO Loser\'s Bracket/gfx/items/collectibles/collectibles_328_thenegative.png', os.path.join(isaac_resources_directory, 'gfx/items/collectibles/collectibles_328_thenegative.png'))

        # If this is Mega Satan mode, copy over the two modified floors
        if self.mega_satan_mode.get() == 1:
            # Copy the Dark Room and The Chest
            copy_file('jud6s-extra/Ruleset 5 - Mega Satan/rooms/16.dark room.stb', os.path.join(isaac_resources_directory, 'rooms/16.dark room.stb'))
            copy_file('jud6s-extra/Ruleset 5 - Mega Satan/rooms/17.chest.stb', os.path.join(isaac_resources_directory, 'rooms/17.chest.stb'))

        # Currently, "current_build" is an integer that corresponds to the build ID
        for build in self.builds:
            if build.attrib['id'] == self.current_build:
                self.current_build = build  # Set it to the XML element corresponding to the build from builds.xml
                break
        if isinstance(self.current_build, str):
            error('Something went wrong with selecting a build.\n(The selected build number of ' + self.current_build + ' did not match any of the builds.)', None)

        # Parse players.xml, items.xml, and itempools.xml
        players_xml = xml.etree.ElementTree.parse('jud6s/players.xml')
        players_info = players_xml.getroot()
        items_xml = xml.etree.ElementTree.parse('xml/items.vanilla.xml')
        items_info = items_xml.getroot()
        itempools_xml = xml.etree.ElementTree.parse('xml/itempools.vanilla.xml')
        itempools_info = itempools_xml.getroot()

        # Parse the build info
        items = self.current_build.get('items')
        trinket = self.current_build.get('trinket')
        removed_items = self.current_build.get('removed')
        redhearts = self.current_build.get('redhearts')
        soulhearts = self.current_build.get('soulhearts')
        blackhearts = self.current_build.get('blackhearts')
        heartcontainers = self.current_build.get('heartcontainers')
        keys = self.current_build.get('keys')
        coins = self.current_build.get('coins')
        bombs = self.current_build.get('bombs')
        card = self.current_build.get('card')
        blindfolded = self.current_build.get('blindfolded')

        # Remove Karma from the game (done in the Jud6s mod)
        for item in items_info:
            if item.tag == 'trinket' and item.attrib['name'] == 'Karma':
                item.attrib['achievement'] = '0'

        # Remove Cain's Eye from the game (done in the seeded Jud6s mod)
        if self.seeded_mode.get() == 1:
            for item in items_info:
                if item.tag == 'trinket' and item.attrib['name'] == 'Cain\'s Eye':
                    item.attrib['achievement'] = '0'

        # Add starting items
        if self.seeded_mode.get() == 1:
            if items:
                items += ' + The Compass'
            else:
                items = 'The Compass'
        if self.LCO_mode.get() == 1:
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
                    if self.LCO_mode.get() == 1:
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
        if self.seeded_mode.get() == 1:
            if removed_items:
                removed_items += ' + Pandora\'s Box + Teleport! + Undefined + The Book of Sin'
            else:
                removed_items = 'Pandora\'s Box + Teleport! + Undefined + The Book of Sin'
        if self.LCO_mode.get() == 1:
            if removed_items:
                removed_items += ' + We Need To Go Deeper!'
            else:
                removed_items = 'We Need To Go Deeper!'
        if removed_items:
            removed_items = removed_items.split(' + ')
            for item in removed_items:
                remove_item_from_all_item_pools(item)

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

        # Draw the start room background and save it in place
        if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/backdrop')):
            create_directory(os.path.join(isaac_resources_directory, 'gfx/backdrop'))
        start_room_background = draw_start_room_background(items, removed_items, trinket)
        start_room_background.save(os.path.join(isaac_resources_directory, 'gfx/backdrop/controls.png'))

        # Open the character menu graphic and write the item/build on it
        color = (54, 47, 45)
        character_menu = Image.open('images/main-menu/charactermenu.png')
        character_menu_draw = ImageDraw.Draw(character_menu)
        small_font = ImageFont.truetype('fonts/comicbd.ttf', 10)
        large_font = ImageFont.truetype('fonts/comicbd.ttf', 14)
        if self.random_build is True:
            seed_text = 'Random Item'
            self.random_build = False  # Set this back to the default value
        elif int(self.current_build.attrib['id']) >= 26:  # Build 26 should be the first custom build
            seed_text = 'Build #' + self.current_build.attrib['id']
        else:
            seed_text = self.current_build.get('items')
        w, h = character_menu_draw.textsize('Selected start:', font=small_font)
        w2, h2 = character_menu_draw.textsize(seed_text, font=large_font)
        character_menu_draw.text((240 - w / 2, 31), 'Selected start:', color, font=small_font)
        character_menu_draw.text((240 - w2 / 2, 41), seed_text, color, font=large_font)
        character_menu.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/charactermenu.png'))

        # We are finished, so launch Isaac
        launch_isaac()

    # Make a custom title menu graphic that represents which options were selected
    def draw_title_graphic(self):
        # Start by drawing the Instant Start logo on a clean Jud6s title menu graphic
        instant_start_logo = Image.open('images/main-menu/reset-logo.png')
        r, g, b, a = instant_start_logo.split()
        instant_start_logo = Image.merge('RGB', (r, g, b))
        mask = Image.merge('L', (a,))
        title_img = Image.open('images/main-menu/titlemenu-base.png')
        title_img.paste(instant_start_logo, (45, 178), mask)

        # Draw the Instant Start Mod text on it
        large_font = ImageFont.truetype('fonts/IsaacSans.ttf', 19)
        title_draw = ImageDraw.Draw(title_img)
        title_draw.text((10, 235), 'Instant Start', (134, 86, 86), font=large_font)
        w, h = title_draw.textsize('Mod v' + mod_version, font=large_font)
        title_draw.text((70 - w / 2, 250), 'Mod v' + mod_version, (134, 86, 86), font=large_font)

        # Draw the Jud6s text and version
        jud6s_text = 'Jud6s Mod ' + jud6s_version
        title_draw.text((345, 239), jud6s_text, (134, 86, 86), font=large_font)

        # Draw the text that shows the options that were selected
        if self.seeded_mode.get() == 1 or self.LCO_mode.get() == 1 or self.mega_satan_mode.get() == 1:
            # Create the text string
            mode_text = '('
            if self.seeded_mode.get() == 1:
                mode_text += 'Seeded + '
            if self.LCO_mode.get() == 1:
                mode_text += 'LCO + '
            if self.mega_satan_mode.get() == 1:
                mode_text += 'Mega Satan + '
            mode_text = mode_text[:-3]  # Remove the trailing " + "
            mode_text += ')'

            # Draw the text string
            small_font = ImageFont.truetype('fonts/IsaacSans.ttf', 15)
            w, h = title_draw.textsize(mode_text, font=small_font)
            title_draw.text((405 - w / 2, 255), mode_text, (134, 86, 86), font=small_font)

        # Save the result directly to the appropriate place in the Isaac resources folder
        title_img.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/titlemenu.png'))

    def go_back(self):
        self.window.destroy()
        ModSelectionWindow(self.parent)


###########################
# The Diversity Mod window
###########################

class DiversityWindow():
    def __init__(self, parent):
        # Class variables
        self.installed_diversity_seed = ''
        self.seed_was_randomly_selected = False
        self.random_button_was_clicked = False

        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title('Diversity Mod v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/icons/rainbow_poop.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', uninstall_mod)  # Uninstall mod files when the window is closed

        # Start counting rows
        row = 0
        row2 = 0

        # Central GUI box
        dmbox = tkinter.LabelFrame(self.window, text='', padx=5, pady=5)
        dmbox.grid(row=row, column=0, columnspan=2, pady=20)
        row += 1

        # "Enter seed" label
        enter_seed_label = tkinter.Label(dmbox, text='Enter seed (case sensitive):', font='font 14')
        enter_seed_label.grid(row=row2, column=0, pady=10)

        # "New Random Seed" button
        new_random_seed_button = tkinter.Button(dmbox, font='font 12')
        new_random_seed_button.configure(command=self.new_random_seed)
        new_random_seed_button.icon = ImageTk.PhotoImage(get_item_icon('D100'))
        new_random_seed_button.configure(image=new_random_seed_button.icon)
        new_random_seed_button.grid(row=row2, column=1, padx=7, sticky=tkinter.E)
        row2 += 1

        # Seed entry box functions
        def select_all(event=None):
            self.seed_entry_box.select_range(0, 'end')

        def check_seed_installed(*args):
            # Set the background to indicate that current entry is installed
            if self.entry_box_contents.get() == self.installed_diversity_seed and self.installed_diversity_seed != '':
                self.seed_entry_box.configure(bg='#d8fbf8')
            else:
                self.seed_entry_box.configure(bg='#f4e6e6')

            # They typed something, so it is not a randomly selected seed
            if self.random_button_was_clicked is True:
                self.random_button_was_clicked = False
            else:
                self.seed_was_randomly_selected = False

        # Seed entry box
        self.entry_box_contents = tkinter.StringVar()
        self.entry_box_contents.trace('w', check_seed_installed)
        self.seed_entry_box = tkinter.Entry(dmbox, justify=tkinter.CENTER, font='font 32 bold', width=15, textvariable=self.entry_box_contents)
        self.seed_entry_box.configure(bg='#f4e6e6')
        self.seed_entry_box.bind('<Return>', lambda event: self.install_diversity_mod())
        self.seed_entry_box.bind('<Control-a>', select_all)
        self.seed_entry_box.grid(row=row2, padx=7, columnspan=2, pady=5)
        self.seed_entry_box.focus()  # Make the seed box have focus automatically
        row2 += 1

        # "Start Diversity Mod" button
        start_diversity_mod_button = tkinter.Button(self.window, font='font 16', text='   Start Diversity Mod   ', compound='left')
        start_diversity_mod_button.configure(command=self.install_diversity_mod)
        start_diversity_mod_button.icon = ImageTk.PhotoImage(Image.open('images/diversity/rainbow.png'))
        start_diversity_mod_button.configure(image=start_diversity_mod_button.icon)
        start_diversity_mod_button.grid(row=row, pady=7, columnspan=2)
        row += 1

        # "Go Back" button
        go_back_button = tkinter.Button(self.window, text=' Go Back (6) ', compound='left')
        go_back_button.configure(font=("Helvetica", 13))
        go_back_button.configure(command=self.go_back)
        go_back_button.grid(row=row, column=0, pady=25)
        self.window.bind('6', lambda event: go_back_button.invoke())
        row += 1

        # Instructions
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will open when you start the mod.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Keep this program open while playing.', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1
        m = tkinter.Message(self.window, justify=tkinter.CENTER, text='Isaac will return to normal when this program is closed.\n', font='font 13', width=400)
        m.grid(row=row, column=0)
        row += 1

        # Spacing
        spacing = tkinter.Message(self.window, text='', font='font 6')
        spacing.grid(row=row)
        row += 1

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

    def new_random_seed(self):
        self.random_button_was_clicked = True
        self.seed_was_randomly_selected = True
        random_seed = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.entry_box_contents.set(random_seed)

    def install_diversity_mod(self):
        ####################
        # Utility functions
        ####################

        def remove_item_from_all_item_pools(item_name):
            item_id = get_item_id(item_name)
            for pool in itempools_info:
                for item in pool.findall('Item'):
                    if item.attrib['Id'] == item_id:  # Weirdly, it is capitalized this way in the vanilla XML
                        pool.remove(item)

        #############################
        # The main installation code
        #############################

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

        # Trim the whitespace on the seed string if there is any
        self.entry_box_contents.set("".join(self.entry_box_contents.get().split()))

        # If no seed was entered, generate a random one
        if self.entry_box_contents.get() == '':
            self.new_random_seed()

        # This is the seed we will install
        self.installed_diversity_seed = self.entry_box_contents.get()

        # Set the background on the seed entry box to indicate that current seed is installed
        self.seed_entry_box.configure(bg='#d8fbf8')

        # Set the RNG seed based on the diversity seed
        random.seed(binascii.crc32(bytes(self.installed_diversity_seed, 'UTF-8')))

        # "valid_items" is the list of all passive items in the game EXCLUDING the 25 items listed in the README file
        valid_items = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 17, 18, 19, 20, 21, 27,
            28, 32, 46, 48, 50, 51, 52, 53, 54, 55,
            57, 60, 62, 63, 64, 67, 68, 69, 70, 71,
            72, 73, 74, 75, 76, 79, 80, 81, 82, 87,
            88, 89, 90, 91, 94, 95, 96, 98, 99, 100,
            101, 103, 104, 106, 108, 109, 110, 112, 113, 114,
            115, 116, 117, 118, 120, 121, 122, 125, 128, 129,
            131, 132, 134, 138, 139, 140, 141, 142, 143, 144,
            148, 149, 150, 151, 152, 153, 154, 155, 156, 157,
            159, 161, 162, 163, 165, 167, 168, 169, 170, 172,
            173, 174, 178, 179, 180, 182, 183, 184, 185, 187,
            188, 189, 190, 191, 193, 195, 196, 197, 198, 199,
            200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
            210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
            220, 221, 222, 223, 224, 225, 227, 228, 229, 230,
            231, 232, 233, 234, 236, 237, 240, 241, 242, 243,
            244, 245, 246, 247, 248, 249, 250, 251, 252, 254,
            255, 256, 257, 259, 260, 261, 262, 264, 265, 266,
            267, 268, 269, 270, 271, 272, 273, 274, 275, 276,
            277, 278, 279, 280, 281, 299, 300, 301, 302, 303,
            304, 305, 306, 307, 308, 309, 310, 311, 312, 313,
            314, 315, 316, 317, 318, 319, 320, 321, 322, 327,
            328, 329, 330, 331, 332, 333, 335, 336, 337, 340,
            341, 342, 343, 345, 350, 353, 354, 356, 358, 359,
            360, 361, 362, 363, 364, 365, 366, 367, 368, 369,
            370, 371, 372, 373, 374, 375, 376, 377, 378, 379,
            380, 381, 384, 385, 387, 388, 389, 390, 391, 392,
            393, 394, 395, 397, 398, 399, 400, 401, 402, 403,
            404, 405, 407, 408, 409, 410, 411, 412, 413, 414,
            415, 416, 417, 418, 420, 423, 424, 425, 426, 429,
            430, 431, 432, 433, 435, 436, 438, 440
        ]

        # Put the items in a random order
        shuffed_items = list(valid_items)
        random.shuffle(shuffed_items)
        items = []
        items.append(get_item_dict(shuffed_items[0])['name'])
        items.append(get_item_dict(shuffed_items[1])['name'])
        items.append(get_item_dict(shuffed_items[2])['name'])

        # Load the fonts for drawing onto images
        small_font = ImageFont.truetype('/fonts/comicbd.ttf', 10)
        large_font = ImageFont.truetype('/fonts/comicbd.ttf', 16)

        # Draw the version number on the title menu graphic
        try:
            title_img = Image.open('images/diversity/titlemenu.png')
            title_draw = ImageDraw.Draw(title_img)
            title_draw.text((425, 240), 'v' + mod_version, (54, 47, 45), font=large_font)
            title_img.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/titlemenu.png'))
        except Exception as e:
            error('Failed to modify the title menu graphic:', e)

        # Copy over the splashes.png so that the title menu graphic looks correct
        copy_file('images/diversity/splashes.png', os.path.join(isaac_resources_directory, 'gfx/ui/main menu/splashes.png'))

        # Draw the seed on the character selection screen graphic
        try:
            character_img = Image.open('images/diversity/charactermenu.png')
            character_draw = ImageDraw.Draw(character_img)
            character_screen_tile_text = 'Diversity Mod seed:'
            w, h = character_draw.textsize(character_screen_tile_text, font=small_font)
            w2, h2 = character_draw.textsize(self.installed_diversity_seed, font=large_font)
            w3, h3 = character_draw.textsize('(random seed)', font=small_font)
            character_draw.text((240 - w / 2, 25), character_screen_tile_text, (54, 47, 45), font=small_font)
            character_draw.text((240 - w2 / 2, 35), self.installed_diversity_seed, (54, 47, 45), font=large_font)
            if self.seed_was_randomly_selected is True:
                character_draw.text((240 - w3 / 2, 190), '(random seed)', (54, 47, 45), font=small_font)
            character_img.save(os.path.join(isaac_resources_directory, 'gfx/ui/main menu/charactermenu.png'))
        except Exception as e:
            error('Failed to modify the character selection screen graphic:', e)

        # Parse players.xml, items.xml, and itempools.xml
        players_xml = xml.etree.ElementTree.parse('jud6s/players.xml')
        players_info = players_xml.getroot()
        items_xml = xml.etree.ElementTree.parse('xml/items.vanilla.xml')
        items_info = items_xml.getroot()
        itempools_xml = xml.etree.ElementTree.parse('xml/itempools.vanilla.xml')
        itempools_info = itempools_xml.getroot()

        # Remove Karma from the game (done in the Jud6s mod)
        for item in items_info:
            if item.tag == 'trinket' and item.attrib['name'] == 'Karma':
                item.attrib['achievement'] = '0'

        # Remove the "special" status from all items (done in the Diversity mod)
        for item in items_info:
            if 'special' in item.attrib.keys():
                del item.attrib['special']

        # Add the 3 random items to every character
        characters_to_skip = ['Eden', 'Lazarus II', 'Black Judas', 'Keeper']  # The game crashes if you try to give Keeper items
        for character in players_info:
            if character.attrib['name'] in characters_to_skip:
                continue
            character.attrib['items'] += ',' + get_item_id(items[0]) + ',' + get_item_id(items[1]) + ',' + get_item_id(items[2])

        # Define the item bans
        removed_items = []
        removed_items.append('Mom\'s Knife')
        removed_items.append('Epic Fetus')
        removed_items.append('Tech X')
        removed_items.append('D4')
        removed_items.append('D100')

        # Add some extra item bans if necessary
        if 'Soy Milk' in items or 'Libra' in items:
            if 'Soy Milk' not in removed_items:
                removed_items.append('Soy Milk')
            if 'Libra' not in removed_items:
                removed_items.append('Libra')

        if 'Isaac\'s Heart' in items:
            if 'Blood Rights' not in removed_items:
                removed_items.append('Blood Rights')

        if 'Brimstone' in items:
            if 'Tammy\'s Head' not in removed_items:
                removed_items.append('Tammy\'s Head')

        if 'Monstro\'s Lung' in items or 'Chocolate Milk' in items:
            if 'Monstro\'s Lung' not in removed_items:
                removed_items.append('Monstro\'s Lung')
            if 'Chocolate Milk' not in removed_items:
                removed_items.append('Chocolate Milk')

        if 'Ipecac' in items or 'Dr. Fetus' in items:
            if 'Ipecac' not in removed_items:
                removed_items.append('Ipecac')
            if 'Dr. Fetus' not in removed_items:
                removed_items.append('Dr. Fetus')

        if 'Technology 2' in items:
            if 'Ipecac' not in removed_items:
                removed_items.append('Ipecac')

        if 'Monstro\'s Lung' in items:
            if 'Ipecac' not in removed_items:
                removed_items.append('Ipecac')

        # Remove the banned items from all pools
        for item in removed_items:
            remove_item_from_all_item_pools(item)

        # Write the changes to the copied over XML files
        players_xml.write(os.path.join(isaac_resources_directory, 'players.xml'))
        itempools_xml.write(os.path.join(isaac_resources_directory, 'itempools.xml'))
        items_xml.write(os.path.join(isaac_resources_directory, 'items.xml'))

        # Draw the start room background and save it in place
        if not os.path.isdir(os.path.join(isaac_resources_directory, 'gfx/backdrop')):
            create_directory(os.path.join(isaac_resources_directory, 'gfx/backdrop'))
        start_room_background = draw_start_room_background(items, removed_items)
        start_room_background.save(os.path.join(isaac_resources_directory, 'gfx/backdrop/controls.png'))

        # We are finished, so launch Isaac
        launch_isaac()

    def go_back(self):
        self.window.destroy()
        ModSelectionWindow(self.parent)


#####################################
# "get" general functions
#####################################

# get_image - Load the image from the provided path in a format suitable for Tk
def get_image(path):
    raw_image_library = {}
    image = raw_image_library.get(path)
    if image is None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
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
        return get_image(os.path.join('images/collectibles', icon_file))
    else:
        return get_image('images/collectibles/question-mark.png')


# get_trinket_icon - Given the name or id of a trinket, return its icon image
def get_trinket_icon(id):
    id = str(id)
    if id.isdigit():
        for child in items_info:
            if child.attrib['id'] == id and child.tag == 'trinket':
                return get_image(os.path.join('images/trinkets', child.attrib['gfx']))
    else:
        for child in items_info:
            if child.attrib['name'].lower() == id.lower() and child.tag == 'trinket':
                return get_image(os.path.join('images/trinkets', child.attrib['gfx']))
    return get_image('images/trinkets/question-mark.png')


####################
# Cleanup functions
####################

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
    sys.exit()


################
# Main function
################

def main():
    # TkInter callbacks run in different threads, so if we want to handle generic exceptions caused in a TkInter callback, we must define a specific custom exception handler for that
    tkinter.Tk.report_callback_exception = callback_error

    # Initialize the root GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI
    root.iconbitmap('images/icons/the_d6.ico')  # Set the GUI icon
    root.title(mod_pretty_name)  # Set the GUI title
    root.resizable(False, False)
    root.protocol('WM_DELETE_WINDOW', sys.exit)

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
    global mod_version
    mod_version = mod_options['options']['modversion']
    root.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title again now that we know the version
    global isaac_resources_directory
    isaac_resources_directory = mod_options['options']['isaacresourcesdirectory']

    # Get the version number of the Jud6s mod specifically (which is different than the version number of Isaac Racing Mods)
    try:
        with open('jud6s/jud6s_version.txt', 'r') as file:
            global jud6s_version
            jud6s_version = file.read()
    except Exception as e:
        error('Failed to get the version number of the Jud6s mod from the "jud6s_version.txt" file:', e)

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
    global backed_up_resources_directory
    backed_up_resources_directory = False
    for file_name in os.listdir(isaac_resources_directory):
        if file_name != 'packed' and file_name != 'config.ini':
            backed_up_resources_directory = True
            break

    # If necessary, move everything in the resources directory to a temporarily directory until the mod is closed
    if backed_up_resources_directory:
        # Create a temporarily directory
        epoch_time = str(int(time.time()))  # Get the current epoch timestamp
        global temp_directory
        temp_directory = os.path.join(isaac_resources_directory, '..', 'resources_backup' + epoch_time)
        delete_file_if_exists(temp_directory)
        os.makedirs(temp_directory)

        # Copy all files EXCEPT for the "packed" directory and config.ini
        for file_name in os.listdir(isaac_resources_directory):
            if file_name != 'packed' and file_name != 'config.ini':
                copy_file(os.path.join(isaac_resources_directory, file_name), os.path.join(temp_directory, file_name))

    # Parse items.xml now so that we can display some images; it will be parsed again before installation
    try:
        items_xml = xml.etree.ElementTree.parse('xml/items.vanilla.xml')
        global items_info
        items_info = items_xml.getroot()
    except Exception as e:
        error('Failed to parse the "xml/items.vanilla.xml" file:', e)

    # Show the mod selection GUI
    ModSelectionWindow(root)
    root.mainloop()


######################
# Program entry point
######################

if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(
        filename=log_file,
        format='%(asctime)s - %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S'
    )

    # Run the program
    try:
        main()
    except Exception as e:
        # Show the error to the user and exit
        error('Generic error:', e)
