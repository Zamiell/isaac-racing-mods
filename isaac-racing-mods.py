#! C:\Python34\python.exe

#############################
# Isaac Racing Mods Launcher
#############################

# Imports
import sys                 # For quitting the application
import traceback           # For error handling
import logging             # For logging all exceptions to a file
import tkinter             # We use TKinter to draw the GUI
import tkinter.messagebox  # This is not automatically imported above
import os                  # For various file operations (1/2)
import shutil              # For various file operations (2/2)
import configparser        # For parsing options.ini
import urllib.request      # For checking GitHub for the latest version
import re                  # For parsing the options.ini file from GitHub
import tempfile            # For figuring out where to put binary that updates the updater
import zipfile             # For unzipping the downloaded latest version
import subprocess          # For running the actual program
import time                # For slowing down the spinning animation
import threading           # For spawning a new thread to do the update work in (1/2)
import queue               # For spawning a new thread to do the update work in (2/2)
from PIL import Image, ImageTk  # For rotating the dice
import platform               # For autodetecting the user's language (1/3)
import locale                 # For autodetecting the user's language (2/3)
import ctypes                 # For autodetecting the user's language (3/3)

# Configuration
mod_pretty_name = 'Isaac Racing Mods'
mod_name = 'isaac-racing-mods'
#mod_name = 'isaac-test'
repository_owner = 'Zamiell'


############################
# General purpose functions
############################

def error(message, exception):
    # Build the error message
    if exception is not None:
        message += '\n\n'
        if type(exception) is tuple:  # We are not in an exception; we got passed the exception information from the thread
            list_of_strings = traceback.format_exception(exception[0], exception[1], exception[2])
            for line in list_of_strings:
                message += line
        else:  # We are in an exception
            message += traceback.format_exc()

    # Print the message to standard out
    print(message)

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

    # Print the message to standard out
    print(message)

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

    # Print the message to standard out
    print(message)

    # Log the error to a file
    logging.error(message)
    with open(log_file, 'a') as file:
        file.write('\n')

    # Show the error to the user
    tkinter.messagebox.showerror('Error', message)

    # Exit the program immediately
    sys.exit()


#####################################
# General window functions
#####################################

def get_window_x_y(self):
    # Global variables
    global window_x
    global window_y

    # Get the X and Y location of the current window
    match = re.search(r'\d+x\d+\+(-*\d+)\+(-*\d+)', self.window.geometry())
    if match:
        window_x = int(match.group(1))
        window_y = int(match.group(2))
    else:
        error('Failed to parse the current window\'s X and Y coordinates.', None)


##################################
# The nagging update popup window
##################################

class NewVersion():
    def __init__(self, parent, action):
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/the_d6.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', lambda: close_mod(self))

        # Store the action for later and show the appropriate update message
        self.action = action
        if self.action == 'update_updater':
            # "A new version" message
            text = get_text('A new version of') + ' ' + mod_pretty_name + ' ' + get_text('has been released.')
            new_version_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 10', text=text, width=600)
            new_version_message.grid(row=0, pady=10)
        elif self.action == 'update_mod':
            # "Version X.X.X has been released" message
            text = get_text('Version') + ' ' + latest_version + ' ' + get_text('of') + ' ' + mod_pretty_name + ' ' + get_text('has been released.') + '\n'
            text += '(' + get_text('You are currently running version') + ' ' + mod_version + '.)'
            new_version_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 10', text=text, width=600)
            new_version_message.grid(row=0, pady=10)
        else:
            error('The "NewVersion" class was called without a valid action.', None)

        # "Automatically update and launch the new version" button
        text = get_text('Automatically update and launch the new version')
        update_button = tkinter.Button(self.window, font='font 12', text=text)
        update_button.configure(command=self.update_button_function)
        update_button.grid(row=1, pady=10, padx=20)

        # "Launch the old version" button
        text = get_text('Launch the old version')
        old_version_button = tkinter.Button(self.window, font='font 12', text=text, command=parent.quit)
        old_version_button.grid(row=2, pady=10)

        # Place the window at the X and Y coordinates from either the INI or the previous window
        self.window.deiconify()  # Show the GUI
        self.window.geometry('+%d+%d' % (window_x, window_y))

    def update_button_function(self):
        # Destroy the current window
        self.window.destroy()

        # Initialize a new GUI window
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title
        self.window.iconbitmap('images/the_d6.ico')  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', lambda: close_mod(self))

        # Updating message
        text = get_text('Updating') + '...'
        updating_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 40', text=text, width=600)
        updating_message.pack()

        # Rotating dice
        self.canvas = tkinter.Canvas(self.window, width=100, height=100)
        self.canvas.pack()
        self.dice_angle = 0
        self.d6_image = Image.open('images/the_d6.ico')
        self.rotated_d6 = ImageTk.PhotoImage(self.d6_image)
        self.d6 = self.canvas.create_image(50, 35, image=self.rotated_d6)

        # Place the window at the X and Y coordinates from either the INI or the previous window
        self.window.deiconify()  # Show the GUI
        self.window.geometry('+%d+%d' % (window_x, window_y))

        # Spawn an update thread
        self.parent.after(1, self.start_update)

    def start_update(self):
        self.thread_potentially_failed = False
        self.queue = queue.Queue()
        self.updater_task = UpdaterTask(self.queue, self.action)
        self.updater_task.start()
        self.parent.after(50, self.process_queue)

    def process_queue(self):
        # Global variables
        global mod_version
        global mod_options

        # Rotate the dice
        self.rotate_dice()

        try:
            # Poll to see if the updating thread is finished its work yet
            message = self.queue.get_nowait()

            # Check to see if the message is an exception
            if type(message) is tuple:
                # An exception has occurred
                error(message[0], message[1])
            elif message != 'Task finished':
                error('Got an unknown message from updater task.', None)

            # It has finished
            if self.action == 'update_updater':
                # Check to see if the program exists
                updater_exe_name = mod_name + '-standalone-updater.exe'
                updater_exe_path = os.path.join(tempfile.gettempdir(), updater_exe_name)
                if not os.path.isfile(updater_exe_path):
                    error('The updater was supposed to be downloaded to "' + updater_exe_path + '", but that file does not exist.\nPlease redownload the program manually.', None)

                # Open the updater
                subprocess.Popen([updater_exe_path, os.path.dirname(os.path.realpath(__file__))])  # Pass the argument of the current directory
                sys.exit()

            elif self.action == 'update_mod':
                # Update options.ini with the new version
                mod_version = latest_version
                mod_options['options']['mod_version'] = mod_version
                try:
                    with open('options.ini', 'w') as config_file:
                        mod_options.write(config_file)
                except Exception as e:
                    error('Failed to write the new version to the "options.ini" file:', e)

                # Close the GUI and proceed with launching the program
                self.parent.quit()
            else:
                error('The "UpdaterTask" class finished without a valid action.', None)

        except queue.Empty:
            if self.updater_task.is_alive() == True:
                self.parent.after(50, self.process_queue)
            else:
                # The thread could have ended before the queue processor got a chance to read the queue message, so let it go one more time
                if self.thread_potentially_failed == False:
                    self.thread_potentially_failed = True
                    self.parent.after(100, self.process_queue)

                # This is the second go around, so the update thread must have really failed
                else:
                    sys.exit()

    def rotate_dice(self):
        self.canvas.delete(self.d6)
        self.dice_angle -= 15
        self.dice_angle -= 360
        self.rotated_d6 = ImageTk.PhotoImage(self.d6_image.rotate(self.dice_angle))
        self.d6 = self.canvas.create_image(50, 35, image=self.rotated_d6)


###############################################
# The updater task that actually does the work
###############################################

class UpdaterTask(threading.Thread):
    def __init__(self, queue, action):
        threading.Thread.__init__(self)
        self.queue = queue
        self.action = action

    def run(self):
        if self.action == 'update_updater':
            self.run_update_updater()
        elif self.action == 'update_mod':
            self.run_update_mod()
        else:
            self.error('The UpdaterTask class was passed an invalid action.', None)

    def run_update_updater(self):
        # Check to see if the updater exe file already exists
        updater_exe_name = mod_name + '-standalone-updater.exe'
        updater_exe_path = os.path.join(tempfile.gettempdir(), updater_exe_name)
        self.delete_file_if_exists(updater_exe_path)

        # Download the updater exe file
        try:
            url = 'https://github.com/' + repository_owner + '/' + mod_name + '/releases/download/' + latest_version + '/' + updater_exe_name
            urllib.request.urlretrieve(url, updater_exe_path)
        except Exception as e:
            self.error('Failed to download the self-updater from GitHub:', e)

        # Signal that the update is completed
        self.queue.put('Task finished')
        sys.exit()  # This will only terminate the existing thread

    def run_update_mod(self):
        # Check to see if the zip file already exists
        mod_zip_name = mod_name + '-patch-package.zip'
        self.delete_file_if_exists(mod_zip_name)

        # Download the zip file
        try:
            url = 'https://github.com/' + repository_owner + '/' + mod_name + '/releases/download/' + latest_version + '/' + mod_zip_name
            urllib.request.urlretrieve(url, mod_zip_name)
        except Exception as e:
            self.error('Failed to download the latest version from GitHub:', e)

        # Check to see if a directory corresponding to the latest version already exists
        self.delete_file_if_exists(latest_version)

        # Create the new directory for the new version
        if os.path.exists(latest_version):
            self.error('I can\'t create the "' + latest_version + '" directory, as a file or folder already exists by that name.', None)
        try:
            os.makedirs(latest_version)
        except Exception as e:
            self.error('Failed to create the "' + latest_version + '" directory:', e)

        # Extract the zip file to the new directory
        try:
            with zipfile.ZipFile(mod_zip_name, 'r') as z:
                z.extractall(latest_version)
        except Exception as e:
            self.error('Failed to extract the downloaded "' + mod_zip_name + '" file:', e)

        # Delete the zip file
        self.delete_file_if_exists(mod_zip_name)

        # Check to see if "program.exe" exists (not strictly necessary but it is a sanity check)
        if not os.path.isfile(os.path.join(latest_version, 'program.exe')):
            self.error('There was not a "program.exe" file in the downloaded zip file, so something went wrong.\nTry downloading the latest version manually.', None)

        # Copy the README file
        for file_name in ['README.txt']:
            if not os.path.isfile(os.path.join(latest_version, file_name)):
                self.error('There was not a "' + file_name + '" file in the downloaded zip file, so something went wrong.\nTry downloading the latest version manually.', None)
            self.delete_file_if_exists(file_name);
            self.copy_file(os.path.join(latest_version, file_name), file_name)
            self.delete_file_if_exists(os.path.join(latest_version, file_name))

        # Delete the directory with the old version
        self.delete_file_if_exists(mod_version)

        # Signal that the update is completed
        self.queue.put('Task finished')
        sys.exit()  # This will only terminate the existing thread

    def delete_file_if_exists(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except Exception as e:
                    self.error('Failed to delete the "' + path + '" file:', e)
            elif os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    self.error('Failed to delete the "' + path + '" directory:', e)
            else:
                self.error('Failed to delete "' + path + '", as it is not a file or a directory.', None)

    def copy_file(self, path1, path2):
        if not os.path.exists(path1):
            self.error('Copying "' + path1 + '" failed because it does not exist.', None)

        if os.path.isfile(path1):
            try:
                shutil.copyfile(path1, path2)
            except Exception as e:
                self.error('Failed to copy the "' + path1 + '" file:', e)
        elif os.path.isdir(path1):
            try:
                shutil.copytree(path1, path2)
            except Exception as e:
                self.error('Failed to copy the "' + path1 + '" directory:', e)
        else:
            self.error('Failed to copy "' + path1 + '", as it is not a file or a directory.', None)

    def error(self, message, exception):
        self.queue.put((message, sys.exc_info() if exception != None else None))  # A tuple indicates an exception has occurred
        sys.exit()

def close_mod(self):
    # Write the current window coordinates to the INI file
    get_window_x_y(self)
    mod_options.set('options', 'window_x', str(window_x))
    mod_options.set('options', 'window_y', str(window_y))
    try:
        with open(os.path.join('..', 'options.ini'), 'w') as config_file:
            mod_options.write(config_file)
    except Exception as e:
        error('Failed to write the window location to the "options.ini" file:', e)

    # Exit the program in a messy way if there is an existing thread
    if hasattr(self, 'updater_task'):
        if self.updater_task.is_alive() == True:
            os._exit(1)  # Can't use "sys.exit()" here because it won't terminate the existing thread

    # There is no existing thread, so exit the program normally
    sys.exit()


###################################
# Language text retrieval function
###################################

def get_text(text):
    languages = {
        'A new version of': {
            'en': 'A new version of',
            'fr': 'Une version de',
        },
        'has been released.': {
            'en': 'has been released.',
            'fr': 'est disponible.',
        },
        'Version': {
            'en': 'Version',
            'fr': 'Version',
        },
        'You are currently running version': {
            'en': 'You are currently running version',
            'fr': 'Vous utilisez actuellement la version',
        },
        'of': {
            'en': 'of',
            'fr': 'de',
        },
        'Automatically update and launch the new version': {
            'en': 'Automatically update and launch the new version',
            'fr': 'Mettre à jour automatiquement et lancer la nouvelle version',
        },
        'Launch the old version': {
            'en': 'Launch the old version',
            'fr': 'Lancer l\'ancienne version',
        },
        'Updating': {
            'en': 'Updating',
            'fr': 'Mise à jour',
        },

        # Template
        '': {
            'en': '',
            'fr': '',
        },
    }
    return languages[text][language]



################
# Main function
################

def main():
    # Global variables
    global mod_options
    global mod_version
    global window_x
    global window_y
    global language
    global latest_version

    # TkInter callbacks run in different threads, so if we want to handle generic exceptions caused in a TkInter callback, we must define a specific custom exception handler for that
    tkinter.Tk.report_callback_exception = callback_error

    # Initialize the GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI

    # Validate that "options.ini" file exists and contains the values we need
    if not os.path.isfile('options.ini'):
        error('The "options.ini" file was not found in the ' + mod_pretty_name + ' directory. Please redownload this program.', None)
    mod_options = configparser.ConfigParser()
    mod_options.read('options.ini')
    if not mod_options.has_section('options'):
        error('The "options.ini" file does not have an "[options]" section. Please redownload this program.', None)
    if 'mod_updater_version' not in mod_options['options']:
        error('The "options.ini" file does not contain the version number of the mod updater. Try adding "mod_updater_version = 1.0.0" or redownloading the program.', None)
    if 'mod_version' not in mod_options['options']:
        error('The "options.ini" file does not contain the version number of the mod. Try adding "mod_version = 3.0.0" or redownloading the program.', None)
    if 'window_x' not in mod_options['options']:
        error('The "options.ini" file does not contain an entry for the X position of your window. Try adding "window_x = 50" or redownloading the program.', None)
    if 'window_y' not in mod_options['options']:
        error('The "options.ini" file does not contain an entry for the Y position of your window. Try adding "window_y = 50" or redownloading the program.', None)
    if 'language' not in mod_options['options']:
        error('The "options.ini" file does not contain an "language" entry. Try adding "language = autodetect" or redownloading the program.', None)

    # Get variables from the "options.ini" file
    mod_updater_version = mod_options['options']['mod_updater_version']
    mod_version = mod_options['options']['mod_version']
    root.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title again now that we know the version
    window_x = int(mod_options['options']['window_x'])
    window_y = int(mod_options['options']['window_y'])
    language = mod_options['options']['language']
    if language != 'autodetect' and language != 'en' and language != 'fr':
        error('The "options.ini" value for "automatically_close_isaac" is not set to a valid language.', None)
    if language == 'autodetect':
        # Find the user's locale, from: http://stackoverflow.com/questions/3425294/how-to-detect-the-os-default-language-in-python
        if platform.system() == 'Windows':
            lang_identifier = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
        else:
            lang_identifier = locale.getdefaultlocale()[0]
        if lang_identifier == 'fr_FR':
            language = 'fr'
        else:
            # Default to English
            language = 'en'

    # Check to see what the latest version of the mod is
    try:
        url = 'https://raw.githubusercontent.com/' + repository_owner + '/' + mod_name + '/master/options.ini'
        master_options_ini = urllib.request.urlopen(url).read().decode('utf8')

        # Get the mod version
        failed_check = False
        match = re.search(r'mod_version = (\d+.\d+.\d+)', master_options_ini)
        if match:
            latest_version = match.group(1)
        else:
            warning('When trying to find what the latest version is, I failed to find the "mod_version" line in the "options.ini" file from GitHub.', None)
            latest_version = mod_version
            failed_check = True

        # Get the mod updater version
        match = re.search(r'mod_updater_version = (\d+.\d+.\d+)', master_options_ini)
        if match:
            latest_updater_version = match.group(1)
        elif failed_check == True:
            pass  # Don't spam the user with 2 warning dialog boxes
        else:
            warning('When trying to find what the latest version is, I failed to find the "mod_updater_version" line in the "options.ini" file from GitHub.', None)
            latest_updater_version = mod_updater_version

    except Exception as e:
        warning('Failed to check GitHub for the latest version:', e)
        latest_version = mod_version
        latest_updater_version = mod_updater_version

    # There is a new version of the updater, so ask the user if they want to automatically update
    if mod_updater_version != latest_updater_version:
        NewVersion(root, 'update_updater')
        root.mainloop()

    # There is a new version of the mod, so ask the user if they want to automatically update
    elif mod_version != latest_version:
        NewVersion(root, 'update_mod')
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
    log_file = mod_name + '-error-log.txt'
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
