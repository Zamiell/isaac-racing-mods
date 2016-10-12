#! C:\Python34\python.exe

# Notes:
# - This file will "freeze" the Python code into an EXE and then package it into a ZIP file.

# Imports
import os            # For various file operations (1/2)
import shutil        # For various file operations (2/2)
import subprocess    # To call pyinstaller
import configparser  # For parsing options.ini
import fileinput     # For updating the webpage
import re            # For parsing the webpage
import sys

# Configuration
mod_pretty_name = 'Isaac Racing Mods'
mod_name = 'isaac-racing-mods'
#mod_name = 'isaac-test'
pyinstaller_path = 'C:\Python34\Scripts\pyinstaller.exe'

# Subroutines
def error(message):
    print(message)
    sys.exit(1)

# Get the version number of the mod from options.ini
mod_options = configparser.ConfigParser()
mod_options.read('options.ini')
mod_version = mod_options['options']['mod_version']

# Make sure the options.ini file is set to the proper default values
mod_options.set('options', 'isaac_resources_directory', 'C:/Program Files (x86)/Steam/SteamApps/common/The Binding of Isaac Rebirth/resources')
mod_options.set('options', 'window_x', '50')
mod_options.set('options', 'window_y', '50')
mod_options.set('options', 'remove_boss_cutscenes', 'true')
mod_options.set('options', 'automatically_close_isaac', 'true')
mod_options.set('options', 'language', 'autodetect')
with open('options.ini', 'w') as config_file:
    mod_options.write(config_file)

# Set the correct download link on the webpage
updated_link = False
webpage_file = 'docs/index.html'
with fileinput.FileInput(webpage_file, inplace=True) as file:
    for line in file:
        line = line.rstrip()
        match = re.search(r'<a id="download-button" class="button" href="https://github.com/Zamiell/isaac-racing-mods/releases/download/\d+\.\d+\.\d+/isaac-racing-mods.zip">Download v\d+\.\d+\.\d+</a>', line) # v\d+\.\d+\.\d+
        if match:
            new_link = r'<a id="download-button" class="button" href="https://github.com/Zamiell/isaac-racing-mods/releases/download/' + mod_version + '/isaac-racing-mods.zip">Download v' + mod_version + '</a>'
            print(line.replace(match.group(), new_link))
            updated_link = True
        else:
            print(line)
if updated_link == False:
    error('Failed to update the webpage.')

# Clean up build-related directories before we start to do anything
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('__pycache__'):
    shutil.rmtree('__pycache__')
if os.path.exists('program/__pycache__'):
    shutil.rmtree('program/__pycache__')
if os.path.exists('release'):
    shutil.rmtree('release')

# Check if pyinstaller is installed
if not os.path.isfile(pyinstaller_path):
    print('Error: Edit this file and specify the path to your pyinstaller.exe file.')
    exit(1)

# Freeze the updater into an exe
return_code = subprocess.call([pyinstaller_path, '--onefile', '--windowed', '--clean', '--log-level=ERROR', '--icon=program/images/icons/the_d6.ico', mod_name + '.py'])
if return_code != 0:
    error('Failed to freeze "' + mod_name + '.py".')
print('Finished building. (1/3)')

# Freeze the main program into an exe
return_code = subprocess.call([pyinstaller_path, '--onefile', '--windowed', '--clean', '--log-level=ERROR','--icon=program/images/icons/the_d6.ico', 'program/program.py'])
if return_code != 0:
    error('Failed to freeze "program.py".')
print('Finished building. (2/3)')

# Freeze the standalone updater into an exe
return_code = subprocess.call([pyinstaller_path, '--onefile', '--windowed', '--clean', '--log-level=ERROR','--icon=program/images/icons/the_d6.ico', mod_name + '-standalone-updater.py'])
if return_code != 0:
    error('Failed to freeze "' + mod_name + '-standalone-updater.py".')
print('Finished building. (3/3)')

# Clean up
shutil.rmtree('__pycache__')
shutil.rmtree('program/__pycache__')

# Rename the "dist" directory to the name of the mod and move it to the "release" folder
install_directory = os.path.join('release', mod_name)
shutil.move('dist', install_directory)  # We use shutil.move() instead of os.rename() because it will create the intermediary directories

# Copy over necessary files
for file_name in ['options.ini', 'README.md', 'Shortcut to BoIA Resources Folder.lnk']:
    shutil.copy(file_name, os.path.join(install_directory, file_name))
for directory_name in ['program']:
    shutil.copytree(directory_name, os.path.join(install_directory, directory_name))

# Remove "program.py"
os.unlink(os.path.join(install_directory, 'program/program.py'))

# Move "program.exe" to the "program" directory
shutil.move(os.path.join(install_directory, 'program.exe'), os.path.join(install_directory, 'program/program.exe'))

# Rename the "program" directory to the version number of the mod
os.rename(os.path.join(install_directory, 'program'), os.path.join(install_directory, mod_version))

# Rename README.md to README.txt so that noobs are less confused
shutil.move(os.path.join(install_directory, 'README.md'), os.path.join(install_directory, 'README.txt'))

# Move the standalone updater next to where the zip files will be created
shutil.move(os.path.join(install_directory, mod_name + '-standalone-updater.exe'), 'release')

# Make the zip file
shutil.make_archive(os.path.join('release', mod_name), 'zip', os.path.join('release', mod_name))

# Make a second zip file for people just updating the program
for file_name in ['README.txt']:  # Include the README file in it
    shutil.copy(os.path.join(install_directory, file_name), os.path.join(install_directory, mod_version, file_name))
shutil.make_archive(os.path.join('release', mod_name + '-patch-package'), 'zip', os.path.join(install_directory, mod_version))
for file_name in ['README.txt']:
    os.unlink(os.path.join(install_directory, mod_version, file_name))

# Clean up
shutil.rmtree('build')
os.unlink(mod_name + '.spec')
os.unlink('program.spec')
os.unlink(mod_name + '-standalone-updater.spec')

# Finished
print('Built version ' + mod_version + ' successfully.')
