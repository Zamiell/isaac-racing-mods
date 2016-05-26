#! C:\Python35\python.exe

# Imports
import sys                 # To handle generic error catching
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


##############
# Subroutines
##############

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


def delete_if_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            try:
                os.remove(path)
            except:
                error(
                    'Failed to delete the existing "' +
                    path +
                    '" file.',
                    sys.exc_info())
        elif os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except:
                error(
                    'Failed to delete the existing "' +
                    path +
                    '" directory.',
                    sys.exc_info())


def immediately_exit():
    exit()


def close_window():
    root.quit()


def hyperlink_button_function():
    webbrowser.open_new(
        r'https://github.com/Zamiell/' +
        mod_name +
        '/releases')
    exit()


def update_button_function():
    # Update the GUI to show that we are updating
    new_version_message.grid_remove()
    root.update_idletasks()
    update_button.grid_remove()
    old_version_button.grid_remove()
    updating_message.grid(row=0, pady=10)
    root.update_idletasks()

    # Check to see if the zip file already exists
    delete_if_exists(mod_name + '.zip')

    # Download the zip file
    try:
        url = 'https://github.com/Zamiell/' + mod_name + \
            '/releases/download/' + latest_version + '/' + mod_name + '.zip'
        urllib.request.urlretrieve(url, mod_name + '.zip')
    except:
        error('Failed to download the latest version from GitHub:', sys.exc_info())

    # Define the name of the temporary directory
    temp_directory = 'temp'

    # Check to see if the temporary directory exists
    delete_if_exists(temp_directory)

    # Create the temporary directory
    os.makedirs(temp_directory)

    # Extract the zip file to the temporary directory
    try:
        with zipfile.ZipFile(mod_name + '.zip', 'r') as z:
            z.extractall(temp_directory)
    except:
        error('Failed to extract the downloaded "' +
              mod_name + '.zip" file:', sys.exc_info())

    # Delete the zip file
    delete_if_exists(mod_name + '.zip')

    # Check to see if the directory corresponding to the latest version
    # already exists
    delete_if_exists(latest_version)

    # Check to see if the "program" directory exists
    if not os.path.isdir(os.path.join(temp_directory, mod_name, 'program')):
        error('There was not a "program" directory in the downloaded zip file, so I don\'t know how to install it.\nTry downloading the latest version manually.', None)

    # Check to see if "program.exe" exists (not strictly necessary but it is a
    # sanity check)
    if not os.path.isfile(
        os.path.join(
            temp_directory,
            mod_name,
            'program',
            'program.exe')):
        error('There was not a "program.exe" file in the downloaded zip file, so I don\'t know how to install it.\nTry downloading the latest version manually.', None)

    # Rename the "program" directory to the version number and move it up a
    # directory
    try:
        os.rename(
            os.path.join(
                temp_directory,
                mod_name,
                'program'),
            latest_version)
    except:
        error('Failed to move the "program" directory:', sys.exc_info())

    # Delete the temporary directory
    delete_if_exists(temp_directory)

    # Update options.ini with the new version
    global mod_version
    mod_version = latest_version
    mod_options['options']['modversion'] = mod_version
    with open('options.ini', 'w') as config_file:
        mod_options.write(config_file)

    # Close the GUI and proceed with launching the program
    root.quit()

# This gets executed first
if __name__ == '__main__':
    # Initialize the GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI
    root.iconbitmap('images/d6.ico')  # Set the GUI icon
    root.title(mod_pretty_name)  # Set the GUI title

    # Validate that options.ini exists and contains values
    if not os.path.isfile('options.ini'):
        error(
            'The "options.ini" file was not found in the ' +
            mod_pretty_name +
            ' directory.\nPlease redownload this program.',
            None)
    mod_options = configparser.ConfigParser()
    mod_options.read('options.ini')
    if not mod_options.has_section('options'):
        error(
            'The "options.ini" file does not have an "[options]" section.\nPlease redownload this program.',
            None)
    if not 'ModVersion' in mod_options['options']:
        error('The "options.ini" does not contain the version number of the mod.\nTry adding "ModVersion=3.0.0" or redownload the program.', None)
    if not 'ModUpdaterVersion' in mod_options['options']:
        error('The "options.ini" does not contain the version number of the mod.\nTry adding "ModUpdaterVersion=1.0.0" or redownload the program.', None)

    # Get the version number of the mod and the mod updater from options.ini
    mod_updater_version = mod_options['options']['modupdaterversion']
    mod_version = mod_options['options']['modversion']
    root.title(mod_pretty_name + ' v' + mod_version)  # Set the GUI title

    # Check to see what the latest version of the mod is
    try:
        url = 'https://api.github.com/repos/Zamiell/' + \
            mod_name + '-updater/releases/latest'
        github_info_json = urllib.request.urlopen(url).read().decode('utf8')
        info = json.loads(github_info_json)
        latest_updater_version = info['name']

        url = 'https://api.github.com/repos/Zamiell/' + mod_name + '/releases/latest'
        github_info_json = urllib.request.urlopen(url).read().decode('utf8')
        info = json.loads(github_info_json)
        latest_version = info['name']
    except:
        warning(
            'Failed to check GitHub for the latest version:',
            sys.exc_info())
        latest_updater_version = mod_updater_version
        latest_version = mod_version

    # There is a new version of the updater, which cannot be automatically
    # downloaded, so alert the user
    if mod_updater_version != latest_updater_version:
        new_version_message = tkinter.Message(
            root,
            justify=tkinter.CENTER,
            font='font 10',
            text='A new version of ' +
            mod_pretty_name +
            ' has been released.\nUnfortunately, this version cannot be automatically updated.\n(You are currently running version ' +
            mod_version +
            '.)',
            width=600)
        new_version_message.grid(row=0, pady=10)

        hyperlink_button = tkinter.Button(
            root,
            font='font 12',
            text='Download the latest version',
            command=hyperlink_button_function)
        hyperlink_button.grid(row=1, pady=10)

        i_dont_care_button = tkinter.Button(
            root, font='font 12', text='I don\'t care', command=close_window)
        i_dont_care_button.grid(row=2, pady=10)

        root.protocol('WM_DELETE_WINDOW', immediately_exit)
        root.deiconify()  # Show the GUI
        tkinter.mainloop()

        # The user gave a response
        root.withdraw()  # Hide the GUI

    # There is a new version of the mod, so ask the user if they want to
    # automatically update
    elif mod_version != latest_version:
        new_version_message = tkinter.Message(
            root,
            justify=tkinter.CENTER,
            font='font 10',
            text='Version ' +
            latest_version +
            ' of ' +
            mod_pretty_name +
            ' has been released.\n(You are currently running version ' +
            mod_version +
            '.)',
            width=600)
        new_version_message.grid(row=0, pady=10)

        update_button = tkinter.Button(
            root,
            font='font 12',
            text='Automatically update and launch the new version',
            command=update_button_function)
        update_button.grid(row=1, pady=10, padx=20)

        old_version_button = tkinter.Button(
            root,
            font='font 12',
            text='Launch the old version',
            command=close_window)
        old_version_button.grid(row=2, pady=10)

        updating_message = tkinter.Message(
            root,
            justify=tkinter.CENTER,
            font='font 16',
            text='Updating...',
            width=600)

        root.protocol('WM_DELETE_WINDOW', immediately_exit)
        root.deiconify()  # Show the GUI
        tkinter.mainloop()

        # The user gave a response
        root.withdraw()  # Hide the GUI

    # Check to see if the directory for the program exists
    if not os.path.isdir(mod_version):
        error(
            'The "' +
            mod_version +
            '" folder does not exist.\n(This is the folder that corresponds to the version of the mod that is installed.)\nPlease redownload the program.',
            None)

    # Check to see if the program exists
    if not os.path.isfile(os.path.join(mod_version, 'program.exe')):
        error(
            'The "program.exe" file does not exist inside your "' +
            mod_version +
            '" folder.\n(This is the core program that powers the mod.)\nPlease redownload the program.',
            None)

    # Open the main program
    subprocess.Popen(
        [os.path.join(mod_version, 'program.exe')], cwd=mod_version)
    exit()
