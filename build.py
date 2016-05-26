#! C:\Python34\python.exe

#------------------------------------------------------------------------------------
# build.py
# - This file will compile the Python code into an EXE and then into a neat ZIP file.
#------------------------------------------------------------------------------------

# Configuration
version = '1.6.8'
install_name = 'instant-start-mod-' + version

# Imports
import os                                   # For various file operations (1/2)
import shutil                               # For various file operations (2/2)
import sys                                  # To exit on error
import subprocess                           # To call pyinstaller
from PIL import Image, ImageFont, ImageDraw # For drawing the title screen

# Clean up build-related directories before we start to do anything
if os.path.exists('build'):
	shutil.rmtree('build')
if os.path.exists('dist'):
	shutil.rmtree('dist')
if os.path.exists('release'):
	shutil.rmtree('release')

# Compile the py file into an exe
if os.path.exists('C:\Python34\Scripts\pyinstaller.exe'):
    subprocess.call(['C:\Python34\Scripts\pyinstaller.exe', '--onefile', '--windowed', '--icon=images/options.ico', 'instant-start-mod.py'])
else:
    print('Error: Edit this file and specify the path to your pyinstaller.exe file.')
    sys.exit(1)

# Make the installation directory inside the "release" directory
install_directory = os.path.join('release', install_name)
shutil.copytree('dist/', install_directory)

# Copy over necessary files
for file_name in ['README.md', 'options.ini', 'Shortcut to BoIA Resources Folder.lnk']:
	shutil.copy(file_name, os.path.join(install_directory, file_name))
for directory_name in ['fonts', 'images', 'jud6s', 'other-files', 'seeded', 'xml']:
	shutil.copytree(directory_name, os.path.join(install_directory, directory_name))

# Rename README.md to README.txt extension so that noobs are less confused
shutil.move(os.path.join(install_directory, 'README.md'), os.path.join(install_directory, 'README.txt'))

# Make the zip file
shutil.make_archive(os.path.join('release', install_name), 'zip', 'release', install_name + '/')

# Clean up
shutil.rmtree('build')
shutil.rmtree('dist')
os.unlink('instant-start-mod.spec')
