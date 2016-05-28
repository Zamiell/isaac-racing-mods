#! C:\Python35\python.exe

# Imports
import sys                 # For quitting the application
import traceback           # For error handling
import logging             # For logging all exceptions to a file
import tkinter             # We use TKinter to draw the GUI
import tkinter.messagebox  # This is not automatically imported above
import os                  # For various file operations (1/2)
import shutil              # For various file operations (2/2)
import configparser        # For parsing options.ini
import urllib.request      # For checking GitHub for the latest version (1/2)
import json                # For checking GitHub for the latest version (2/2)
import webbrowser          # For helping the user update when a new version is released
import zipfile             # For automatically updating to the latest version
import subprocess          # For running the actual program

# Configuration
mod_pretty_name = 'Isaac Racing Mods'
mod_name = 'isaac-racing-mods'
log_file = mod_name + '-error-log.txt'


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


def make_directory(path):
    if os.path.exists(path):
        error('Failed to create the "' + path + '" directory, as a file or folder already exists by that name.', None)

    try:
        os.makedirs(path)
    except Exception as e:
        error('Failed to create the "' + path + '" directory:', e)


####################################
# The classes for the popup windows
####################################

class NewUpdaterVersion():
    def __init__(self, parent):
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/the_d6.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', sys.exit)

        new_updater_version_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 10', text='A new version of ' + mod_pretty_name + ' has been released.\nUnfortunately, this version cannot be automatically updated.\n(You are currently running version ' + mod_version + '.)', width=600)
        new_updater_version_message.grid(row=0, pady=10)

        hyperlink_button = tkinter.Button(self.window, font='font 12', text='Download the latest version')
        hyperlink_button.configure(command=self.hyperlink_button_function)
        hyperlink_button.grid(row=1, pady=10)

        i_dont_care_button = tkinter.Button(self.window, font='font 12', text='I don\'t care', command=parent.quit)
        i_dont_care_button.grid(row=2, pady=10)

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

    def hyperlink_button_function(self):
        webbrowser.open_new(r'https://github.com/Zamiell/' + mod_name + '/releases')
        sys.exit()

class NewVersion():
    def __init__(self, parent):
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/the_d6.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', sys.exit)

        # "Version X.X.X has been released" message
        new_version_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 10', text='Version ' + latest_version + ' of ' + mod_pretty_name + ' has been released.\n(You are currently running version ' + mod_version + '.)', width=600)
        new_version_message.grid(row=0, pady=10)

        # "Automatically update and launch the new version" button
        update_button = tkinter.Button(self.window, font='font 12', text='Automatically update and launch the new version')
        update_button.configure(command=self.update_button_function)
        update_button.grid(row=1, pady=10, padx=20)

        # "Launch the old version" button
        old_version_button = tkinter.Button(self.window, font='font 12', text='Launch the old version', command=parent.quit)
        old_version_button.grid(row=2, pady=10)

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

    def update_button_function(self):
        # Global variables
        global mod_version
        global mod_options

        # Destroy the current window
        self.window.destroy()

        # Initialize a new GUI window
        self.window = tkinter.Toplevel(self.parent)
        #self.window.withdraw()  # Hide the GUI
        self.window.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/the_d6.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', sys.exit)

        # Updating message
        updating_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 16', text='Updating...', width=600)
        updating_message.pack()

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
        self.window.update()  # Necessary because we are not in a mainloop()
        
        # Check to see if the zip file already exists
        delete_file_if_exists(mod_name + '.zip')

        # Download the zip file
        try:
            url = 'https://github.com/Zamiell/' + mod_name + '/releases/download/' + latest_version + '/' + mod_name + '.zip'
            urllib.request.urlretrieve(url, mod_name + '.zip')
        except Exception as e:
            error('Failed to download the latest version from GitHub:', e)

        # Define the name of the temporary directory
        temp_directory = 'temp'

        # Check to see if the temporary directory exists
        delete_file_if_exists(temp_directory)

        # Create the temporary directory
        make_directory(temp_directory)

        # Extract the zip file to the temporary directory
        try:
            with zipfile.ZipFile(mod_name + '.zip', 'r') as z:
                z.extractall(temp_directory)
        except Exception as e:
            error('Failed to extract the downloaded "' + mod_name + '.zip" file:', e)

        # Delete the zip file
        delete_file_if_exists(mod_name + '.zip')

        # Check to see if the directory corresponding to the latest version already exists
        delete_file_if_exists(latest_version)

        # Check to see if the "program" directory exists
        if not os.path.isdir(os.path.join(temp_directory, mod_name, latest_version)):
            error('There was not a "' + latest_version + '" directory in the downloaded zip file, so I don\'t know how to install it.\nTry downloading the latest version manually.', None)

        # Check to see if "program.exe" exists (not strictly necessary but it is a sanity check)
        if not os.path.isfile(os.path.join(temp_directory, mod_name, latest_version, 'program.exe')):
            error('There was not a "program.exe" file in the downloaded zip file, so I don\'t know how to install it.\nTry downloading the latest version manually.', None)

        # Move the version number (program) directory up two directories
        try:
            shutil.move(os.path.join(temp_directory, mod_name, latest_version), latest_version)
        except Exception as e:
            error('Failed to move the "program" directory:', e)

        # Delete the temporary directory
        delete_file_if_exists(temp_directory)

        # Delete the directory with the old version
        delete_file_if_exists(mod_version)

        # Update options.ini with the new version
        mod_version = latest_version
        mod_options['options']['modversion'] = mod_version
        try:
            with open('options.ini', 'w') as config_file:
                mod_options.write(config_file)
        except Exception as e:
            error('Failed to write the new version to the "options.ini" file:', e)

        # Close the GUI and proceed with launching the program
        self.parent.quit()

################
# Main function
################

def main():
    # Global variables
    global mod_options
    global mod_version
    global latest_version

    # TkInter callbacks run in different threads, so if we want to handle generic exceptions caused in a TkInter callback, we must define a specific custom exception handler for that
    tkinter.Tk.report_callback_exception = callback_error

    # Initialize the GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI
    root.iconbitmap('images/the_d6.ico')  # Set the GUI icon
    root.title(mod_pretty_name)  # Set the GUI title
    root.resizable(False, False)
    root.protocol('WM_DELETE_WINDOW', sys.exit)

    # Validate that options.ini exists and contains the values we need
    if not os.path.isfile('options.ini'):
        error('The "options.ini" file was not found in the ' + mod_pretty_name + ' directory.\nPlease redownload this program.', None)
    mod_options = configparser.ConfigParser()
    mod_options.read('options.ini')
    if not mod_options.has_section('options'):
        error('The "options.ini" file does not have an "[options]" section.\nPlease redownload this program.', None)
    if 'modupdaterversion' not in mod_options['options']:  # configparser defaults everything to lowercase
        error('The "options.ini" does not contain the version number of the mod updater.\nTry adding "modupdaterversion = 1.0.0" or redownloading the program.', None)
    if 'modversion' not in mod_options['options']:  # configparser defaults everything to lowercase
        error('The "options.ini" does not contain the version number of the mod.\nTry adding "modversion = 3.0.0" or redownloading the program.', None)

    # Get the version number of the mod and the mod updater from options.ini
    mod_updater_version = mod_options['options']['modupdaterversion']
    mod_version = mod_options['options']['modversion']
    root.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title again now that we know the version

    # Check to see what the latest version of the mod is
    try:
        url = 'https://api.github.com/repos/Zamiell/' + mod_name + '-updater/releases/latest'
        github_info_json = urllib.request.urlopen(url).read().decode('utf8')
        info = json.loads(github_info_json)
        latest_updater_version = info['name']

        url = 'https://api.github.com/repos/Zamiell/' + mod_name + '/releases/latest'
        github_info_json = urllib.request.urlopen(url).read().decode('utf8')
        info = json.loads(github_info_json)
        latest_version = info['name']
    except Exception as e:
        warning('Failed to check GitHub for the latest version:', e)
        latest_updater_version = mod_updater_version
        latest_version = mod_version

    # There is a new version of the updater, which cannot be automatically downloaded, so alert the user
    if mod_updater_version != latest_updater_version:
        NewUpdaterVersion(root)
        root.mainloop()

    # There is a new version of the mod, so ask the user if they want to automatically update
    elif mod_version != latest_version:
        NewVersion(root)
        root.mainloop()

    #####################################
    # Proceed with launching the program
    #####################################

    # Check to see if the directory for the program exists
    if not os.path.isdir(mod_version):
        error('The "' + mod_version + '" folder does not exist.\n(This is the folder that corresponds to the version of the mod that is installed.)\nPlease redownload the program.', None)

    # Check to see if the program exists
    if not os.path.isfile(os.path.join(mod_version, 'program.exe')):
        error('The "program.exe" file does not exist inside your "' + mod_version + '" folder.\n(This is the core program that powers the mod.)\nPlease redownload the program.', None)

    # Open the main program
    subprocess.Popen([os.path.join(mod_version, 'program.exe')], cwd=mod_version)
    sys.exit()


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
