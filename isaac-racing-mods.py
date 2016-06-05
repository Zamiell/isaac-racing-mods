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
import webbrowser          # For helping the user update when a new version is released
import zipfile             # For automatically updating to the latest version
import subprocess          # For running the actual program
import time                # For slowing down the spinning animation
import threading           # For spawning a new thread to do the update work in (1/2)
import queue               # For spawning a new thread to do the update work in (2/2)
from PIL import Image, ImageTk  # For rotating the dice

# Configuration
mod_pretty_name = 'Isaac Racing Mods'
mod_name = 'isaac-racing-mods'


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
        self.window.protocol('WM_DELETE_WINDOW', lambda: close_mod(self))

        new_updater_version_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 10', text='A new version of ' + mod_pretty_name + ' has been released.\nUnfortunately, this version cannot be automatically updated.\n(You are currently running version ' + mod_version + '.)', width=600)
        new_updater_version_message.grid(row=0, pady=10)

        hyperlink_button = tkinter.Button(self.window, font='font 12', text='Download the latest version')
        hyperlink_button.configure(command=self.hyperlink_button_function)
        hyperlink_button.grid(row=1, pady=10)

        i_dont_care_button = tkinter.Button(self.window, font='font 12', text='I don\'t care', command=parent.quit)
        i_dont_care_button.grid(row=2, pady=10)

        # Place the window at the X and Y coordinates from either the INI or the previous window
        self.window.deiconify()  # Show the GUI
        self.window.geometry('+%d+%d' % (window_x, window_y))

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
        self.window.protocol('WM_DELETE_WINDOW', lambda: close_mod(self))

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
        updating_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 40', text='Updating...', width=600)
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
        self.updater_task = UpdaterTask(self.queue)
        self.updater_task.start()
        self.parent.after(50, self.process_queue)

    def process_queue(self):
        # Global variables
        global mod_version
        global mod_options

        # Rotate the dice
        self.rotate_dice()

        # Let new things happen in GUI land
        #self.window.update_idletasks()

        try:
            # Poll to see if the updating thread is finished its work yet
            message = self.queue.get_nowait()

            # Check to see if the message is an exception
            if type(message) is tuple:
                # An exception has occurred
                error(message[0], message[1])
            elif message != 'Task finished':
                error('Got an unknown message from updater task.', None)

            # It has finished, so update options.ini with the new version
            global mod_version
            global mod_options

            mod_version = latest_version
            mod_options['options']['mod_version'] = mod_version
            try:
                with open('options.ini', 'w') as config_file:
                    mod_options.write(config_file)
            except Exception as e:
                error('Failed to write the new version to the "options.ini" file:', e)

            # Close the GUI and proceed with launching the program
            self.parent.quit()

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


class UpdaterTask(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        # Check to see if the zip file already exists
        self.delete_file_if_exists(mod_name + '.zip')

        # Download the zip file
        try:
            url = 'https://github.com/Zamiell/' + mod_name + '/releases/download/' + latest_version + '/' + mod_name + '.zip'
            urllib.request.urlretrieve(url, mod_name + '.zip')
        except Exception as e:
            self.error('Failed to download the latest version from GitHub:', e)

        # Define the name of the temporary directory
        temp_directory = 'temp'

        # Check to see if the temporary directory exists
        self.delete_file_if_exists(temp_directory)

        # Create the temporary directory
        if os.path.exists(temp_directory):
            self.error('Failed to create the "' + temp_directory + '" directory, as a file or folder already exists by that name.', None)
        try:
            os.makedirs(temp_directory)
        except Exception as e:
            self.error('Failed to create the "' + temp_directory + '" directory:', sys.exc_info())

        # Extract the zip file to the temporary directory
        try:
            with zipfile.ZipFile(mod_name + '.zip', 'r') as z:
                z.extractall(temp_directory)
        except Exception as e:
            self.error('Failed to extract the downloaded "' + mod_name + '.zip" file:', e)

        # Delete the zip file
        self.delete_file_if_exists(mod_name + '.zip')

        # Check to see if the directory corresponding to the latest version already exists
        self.delete_file_if_exists(latest_version)

        # Check to see if the "program" directory exists
        if not os.path.isdir(os.path.join(temp_directory, mod_name, latest_version)):
            self.error('There was not a "' + latest_version + '" directory in the downloaded zip file, so I don\'t know how to install it.\nTry downloading the latest version manually.', None)

        # Check to see if "program.exe" exists (not strictly necessary but it is a sanity check)
        if not os.path.isfile(os.path.join(temp_directory, mod_name, latest_version, 'program.exe')):
            self.error('There was not a "program.exe" file in the downloaded zip file, so I don\'t know how to install it.\nTry downloading the latest version manually.', None)

        # Move the version number (program) directory up two directories
        try:
            shutil.move(os.path.join(temp_directory, mod_name, latest_version), latest_version)
        except Exception as e:
            self.error('Failed to move the "program" directory:', e)

        # Delete the temporary directory
        self.delete_file_if_exists(temp_directory)

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
                
    def error(self, message, exception):
        self.queue.put((message, sys.exc_info() if exception != None else None))  # A tuple indicates an exception has occurred
        sys.exit()

def close_mod(self):
    # Write the new path to the INI file
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


################
# Main function
################

def main():
    # Global variables
    global mod_options
    global mod_version
    global window_x
    global window_y
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

    # Get variables from the "options.ini" file
    mod_updater_version = mod_options['options']['mod_updater_version']
    mod_version = mod_options['options']['mod_version']
    root.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title again now that we know the version
    window_x = int(mod_options['options']['window_x'])
    window_y = int(mod_options['options']['window_y'])

    # Check to see what the latest version of the mod is
    try:
        url = 'https://raw.githubusercontent.com/Zamiell/' + mod_name + '/master/options.ini'
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
