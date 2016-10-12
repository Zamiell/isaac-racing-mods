#! C:\Python34\python.exe

############################
# Isaac Racing Mods Updater
############################

# Imports
import sys                 # For quitting the application
import traceback           # For error handling
import logging             # For logging all exceptions to a file
import tkinter             # We use TKinter to draw the GUI
import tkinter.messagebox  # This is not automatically imported above
import os                  # For various file operations (1/2)
import shutil              # For various file operations (2/2)
import urllib.request      # For checking GitHub for the latest version
import re                  # For parsing the options.ini file from GitHub
import tempfile            # For figuring out where to put the log file
import zipfile             # For unzipping the downloaded latest version
import subprocess          # For running the program once it is finished updating
import time                # For slowing down the spinning animation
import threading           # For spawning a new thread to do the update work in (1/2)
import queue               # For spawning a new thread to do the update work in (2/2)
import base64              # For decoding the included D6 picture
from PIL import Image, ImageTk  # For rotating the dice

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
    print(message.encode('utf-8'))

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
    print(message.encode('utf-8'))

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
    print(message.encode('utf-8'))

    # Log the error to a file
    logging.error(message)
    with open(log_file, 'a') as file:
        file.write('\n')

    # Show the error to the user
    tkinter.messagebox.showerror('Error', message)

    # Exit the program immediately
    sys.exit()


####################
# Make the D6 image
####################

def make_d6_picture():
    d6_image_raw = base64.b64decode(b'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AAcAAAAHgAAAB4AAAAfgAAAH4AAAB/wAAA/+AAAP/gAAD/+AAH//gAB///AP/ygAAAAwAAAAYAAAAAEAIAAAAAAAACQAAMMOAADDDgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACG0AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACLYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACG0AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACLYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACEUAAAh5AAAIeQAACHkAAAh5AAAIeQAACHkAAAh5AAAIeQAACLIAAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACNkAAAh5AAAIeQAACHkAAAh5AAAIIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACJIAAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAISQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACJIAAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAISQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjPAAAI8gAACPkAAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/xMNNv8sHnT/LB50/ywedP8sHnT/LB50/ywedP8sHnT/LB50/x8WVf8AAAj/AAAI/wAACP8AAAj/AAAI9QAACPIAAAiKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjbAAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/xQOOf8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/yEXWf8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAiSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjbAAAI/wAACP8AAAj/BgQW/xMNOP8TDTj/Ew04/xMNOP8bFEj/HhdO/yofa/85KZD/OSmQ/zkpkP85KZD/OSmQ/zkpkP8uIHb/JRpj/x4UUP8LByH/Cwch/wsHIf8LByH/AwIP/wAACP8AAAjAAAAIawAACGsAAAhrAAAIawAACA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjbAAAI/wAACP8AAAj/DQkp/y4gev8uIHr/LiB6/y4gev9BMKD/SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/8tIXH/GRFD/xkRQ/8ZEUP/GRFD/xkRQ/8ZEUP/BwUZ/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjbAAAI/wAACP8AAAj/DQkp/y4gev8uIHr/LiB6/y4gev9BMKD/SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/8tIXH/GRFD/xkRQ/8ZEUP/GRFD/xkRQ/8ZEUP/BwUZ/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAghAAAI5AAACOQAAAj7AAAI/xgQQv8pHW7/MSN//0U0qf9FNKn/RTSp/0U0qf9HNa3/SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/8tIXH/GRFD/xwTSv8iF1v/Ihdb/yIXW/8iF1v/GhJF/xYPPf8NCSb/AAAI/wAACP8AAAj/AAAI/wAACOgAAAjkAAAIYgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgkAAAI/wAACP8AAAj/AAAI/xoSSf8uIHr/NSaJ/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/8tIXH/GRFD/xwTS/8jGF7/Ixhe/yMYXv8jGF7/HBNL/xkRQ/8OCir/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgkAAAI/wAACP8AAAj/AAAI/xoSSf8uIHr/NSaJ/0g2r/9INq//SDav/0g2r/9INq//SDav/z0tlf8tInH/MSV6/0g2r/9INq//QC+e/z4um/8pHWn/GRFD/xwTS/8jGF7/Ixhe/ycbaP8nG2j/IBZV/x0UTf8UDjn/CQYe/wkGHv8JBh7/CQYe/wEBC/8AAAj/AAAIowAACF4AAAhDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgkAAAI/wAACP8AAAj/AAAI/xoSSf8uIHr/NSaJ/0g2r/9INq//SDav/0g2r/9INq//SDav/ykfZ/8AAAj/Cggg/0g2r/9INq//MiOC/y4gev8iF1v/GRFD/xwTS/8jGF7/Ixhe/y4gev8uIHr/Jhpm/yMYXv8fFVL/GRFD/xkRQ/8ZEUP/GRFD/wQCEP8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgkAAAI/wAACP8AAAj/AAAI/xoSSf8uIHr/NSaJ/0g2r/9INq//SDav/0g2r/9INq//SDav/ykfZ/8AAAj/Cggg/0g2r/9INq//MiOC/y4gev8iF1v/GRFD/xwTS/8jGF7/Ixhe/y4gev8uIHr/Jhpm/yMYXv8fFVL/GRFD/xkRQ/8ZEUP/GRFD/wQCEP8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgkAAAI/wAACP8AAAj/AAAI/ycdY/9EM6f/RTSp/0g2r/9INq//SDav/0g2r/9INq//SDav/0MypP89LZX/Pi+Y/0g2r/9INq//Ixha/xwTTP8fFVT/IRda/yUZYv8sH3b/LB92/y4gev8uIHr/LR93/ywfdv8sHnT/Kx5x/ykdbv8hF1r/IRda/xcQPv8VDjr/CQYd/wAACP8AAAjzAAAI1wAACNcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgkAAAI/wAACP8AAAj/AAAI/ykfZ/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//IBZS/xkRQ/8fFVL/Ixhe/yYaZv8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ywfdv8jGF7/Ixhe/xoSR/8ZEUP/Cwch/wAACP8AAAj/AAAI/wAACP8AAAAAAAAAAAAAAAAAAAAAAAAIIwAACFEAAAhpAAAI/wAACP8MCSf/Dwos/y8jd/9INq//SDav/0g2r/9INq//MSV6/zElev9CMaD/SDav/0g2r/9INq//RzWt/0Avnv9AL57/HxVQ/xkRQ/8fFVL/Ixhe/yYaZv8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y0fd/8mG2f/Jhtn/xsSSP8ZEUP/Cwch/wAACP8AAAj/AAAI/wAACP8AAAAAAAAAAAAAAAAAAAAAAAAIbQAACP8AAAj/AAAI/wAACP8nG2r/LiB6/z0tmP9INq//SDav/0g2r/9INq//AAAI/wAACP8zJ3//SDav/0g2r/9INq//RDOn/y4gev8uIHr/HBNL/xkRQ/8fFVL/Ixhe/yYaZv8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/xwTS/8ZEUP/Cwch/wAACP8AAAj/AAAI/wAACP8AAAAAAAAAAAAAAAAAAAAAAAAIbQAACP8AAAj/AAAI/wAACP8nG2r/LiB6/z0tmP9INq//SDav/0g2r/9INq//AAAI/wAACP8zJ3//SDav/0g2r/9INq//RDOn/y4gev8uIHr/HBNL/xkRQ/8fFVL/Ixhe/yYaZv8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/xwTS/8ZEUP/Cwch/wAACP8AAAj/AAAI/wAACP8AAAAAAAAAAAAAAAAAAAAAAAAIbQAACP8AAAj/AAAI/wAACP85Ko7/QzGk/0Y0qv9INq//SDav/0g2r/9INq//OSuM/zkrjP9EM6X/SDav/0g2r/9INq//QjGh/x0UT/8dFE//IBZX/yEXWP8nG2j/LB50/ywfdv8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/wsII/8FBBT/AgIN/wAACP8AAAjFAAAINgAACDYAAAAAAAAAAAAAAAAAAAAAAAAIbQAACP8AAAj/AAAI/wAACP8+Lpf/SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//QTGg/xkRQ/8ZEUP/Ihda/yMYXv8pHW7/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/wcFGP8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAAAAAAAAAAACDAAAAhDAAAIlAAACP8CAQz/DAgm/wwIJv8/L5v/SDav/z0ulv81KIP/OiyQ/0g2r/9INq//SDav/0g2r/9INq//SDav/0U0qf9BMKH/OyyU/xkRQ/8ZEUP/Ihda/yMYXv8pHW7/LiB6/y4gev8uIHr/LiB6/yIYXP8iGFz/Kx5x/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/wcFGP8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAAAAAAAAAAACLYAAAj/AAAI/wAACP8HBRj/LiB6/y4gev9EM6f/SDav/x8XUP8AAAj/FQ84/0g2r/9INq//SDav/0g2r/9INq//SDav/z0tmP8uIHr/Kx5y/xkRQ/8ZEUP/Ihda/yMYXv8pHW7/LiB6/y4gev8uIHr/LiB6/wAACP8AAAj/IRdZ/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/wcFGP8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAAAAAAAAAAACLYAAAj/AAAI/wAACP8HBRj/LiB6/y4gev9EM6f/SDav/x8XUP8AAAj/FQ84/0g2r/9INq//SDav/0g2r/9INq//SDav/z0tmP8uIHr/Kx5y/xkRQ/8ZEUP/Ihda/yMYXv8pHW7/LiB6/y4gev8uIHr/LiB6/wAACP8AAAj/IRdZ/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/wcFGP8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAAAAAAAAAAACLYAAAj/AAAI/wAACP8JBx7/QTCh/0Ewof9HNa3/SDav/z0ulv81KIP/OiyQ/0g2r/9INq//SDav/0g2r/86KpP/NSaI/ysfcf8fFVH/HxVS/yAWV/8gFlf/Kh1v/ysec/8tH3f/LiB6/y4gev8uIHr/LiB6/yIYXP8iGFz/Kx5x/y4gev8uIHr/LiB6/y0fd/8mGmX/Jhpl/wUEFf8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAAAAAAAAAAACLYAAAj/AAAI/wAACP8KCCD/SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/9INq//SDav/0g2r/81Jon/LiB6/yUaYv8ZEUP/GhJH/yMYXv8jGF7/LB92/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ywfdv8jGF7/Ixhe/wUDFP8AAAj/AAAI/wAACP8AAAi2AAAAAAAAAAAAAAg2AAAINgAACMUAAAj/BAMS/woHIP8TDTT/SDav/0g2r/9DMqX/QzGk/0Awnf8+Lpj/Pi6Y/z4umP8+Lpj/Pi6Y/z4umP8vInr/Kh1u/yIYXP8ZEUP/GhJH/yMYXv8jGF7/LB92/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ysec/8cE0z/HBNM/wQDEv8AAAj/AAAI4AAACMkAAAiQAAAAAAAAAAAAAAj/AAAI/wAACP8AAAj/FA45/y4gev8yI4L/SDav/0g2r/8yI4L/LiB6/yIXW/8ZEUP/GRFD/xkRQ/8ZEUP/GRFD/xkRQ/8ZEUP/GRFD/xkRQ/8ZEUP/GhJH/yMYXv8jGF7/LB92/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ycbav8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAj/AAAI/wAACP8AAAj/FA45/y4gev8yI4L/SDav/0g2r/8yI4L/LiB6/yIXW/8ZEUP/GRFD/xkRQ/8ZEUP/GRFD/xkRQ/8ZEUP/GRFD/xkRQ/8ZEUP/GhJH/yMYXv8jGF7/LB92/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ycbav8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAj/AAAI/wAACP8AAAj/Dgkp/yAWVP8hF1f/KB1l/ygdZf8hF1f/IBZU/yAWVf8gFlX/Ihdb/ycbaf8nG2n/Jxtp/ycbaf8nG2n/Jxtp/yQZYP8gFlX/HxVU/xwTTP8cE0z/HxVT/yAWVP8oHGr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ycbav8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAj/AAAI/wAACP8AAAj/Cwch/xkRQ/8ZEUP/GRFD/xkRQ/8ZEUP/GRFD/x8VUv8jGF7/Jhpm/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ykdbv8jGF7/Ihda/xkRQ/8ZEUP/GRFD/xkRQ/8lGmL/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ycbav8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAjXAAAI1wAACPMAAAj/CQYd/xUOOv8VDjr/FQ46/xUOOv8aEkX/GxJH/yAWV/8lGWL/Jxtp/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/yodcP8lGWL/JBhf/xwTTP8cE0z/GxJI/xsSR/8kGV//Kx5x/ywedP8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ycbav8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACLYAAAj/AAAI/wAACP8AAAj/AAAI/wAACP8eFVL/Ixhe/ykdbv8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/JRli/yMYXv8dFE//GRFD/x8VU/8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ycbav8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACLYAAAj/AAAI/wAACP8AAAj/AAAI/wAACP8eFVL/Ixhe/ykdbv8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/JRli/yMYXv8dFE//GRFD/x8VU/8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/ycbav8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACEMAAAheAAAIowAACP8AAAj/AAAI/wAACP8LCCP/DQko/xwTTf8nG2j/KRxt/y4gev8uIHr/EQwy/xEMMv8mGmX/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/Kx1x/yodcP8kGWD/HxVU/yAWVf8hF1f/IRdX/y4gev8uIHr/LiB6/y4gev8rHnL/Jxto/yEXW/8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIbQAACP8AAAj/AAAI/wAACP8AAAj/AAAI/xQOOf8jGF7/Jhpm/y4gev8uIHr/AAAI/wAACP8hF1n/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8oG2r/Ixhe/yAWVv8ZEUP/GRFD/y4gev8uIHr/LiB6/y4gev8pHW7/Ixhe/x4VUv8AAAj/AAAI/wAACP8AAAj/AAAIbQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIYgAACOQAAAjkAAAI5AAACOQAAAj7AAAI/xIMNP8fFVX/JBhg/y4gev8uIHr/BQMU/wUDFP8iGF3/LiB6/y4gev8uIHr/LSB4/ykdbv8pHW7/LSB4/y4gev8oHGz/JBlh/yEXWf8aEkb/GhJG/ywedP8sHnT/LB50/ywedP8mG2f/HxVV/xsSSv8AAAj/AAAI/wAACOgAAAjkAAAIYgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjbAAAI/wAACP8AAAj/DQkp/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/Jxtq/wAACP8AAAj/Jxtq/y4gev8uIHr/LiB6/ysecv8jGF7/Ixhe/xkRQ/8ZEUP/GRFD/xkRQ/8OCir/AAAI/wAACP8AAAj/AAAI/wAACCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjbAAAI/wAACP8AAAj/DQkp/y4gev8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8uIHr/Jxtq/wAACP8AAAj/Jxtq/y4gev8uIHr/LiB6/ysecv8jGF7/Ixhe/xkRQ/8ZEUP/GRFD/xkRQ/8OCir/AAAI/wAACP8AAAj/AAAI/wAACCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhcAAAIawAACMAAAAj/BgQW/xMNOP8TDTj/Ew04/xMNOP8iF1z/KBtq/yodcf8uIHr/Kx5z/xsTSv8bE0r/Kx5z/y4gev8qHXH/KBtq/yEWWP8PCiz/Dwos/wsHIf8LByH/Cwch/wsHIf8GBBb/AAAI/wAACP8AAAj/AAAI/wAACCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACJIAAAj/AAAI/wAACP8AAAj/AAAI/wAACP8ZEUX/Ixhe/ygbav8uIHr/LiB6/y4gev8uIHr/LiB6/y4gev8oG2r/Ixhe/xkRRf8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACIoAAAjyAAAI9QAACP8AAAj/AAAI/wAACP8YEEL/IRdZ/yYaZf8sHnT/LB50/ywedP8sHnT/LB50/ywedP8mGmX/IRdZ/xgQQv8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj5AAAI8gAACPIAAAjyAAAI8gAACCMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAISQAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAiSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAISQAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAiSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIIwAACHkAAAh5AAAIeQAACHkAAAjZAAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACNkAAAh5AAAIeQAACHkAAAh5AAAIeQAACHkAAAhFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAi2AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACLYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAi2AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACP8AAAj/AAAI/wAACLYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///AD//8AAP//8AP//wAA/+AAAB//AAD/4AAAH/8AAP/gAAAf/wAA/4AAAAf/AAD/gAAAB/8AAP+AAAAAPwAA/4AAAAA/AAD/gAAAAD8AAPwAAAAADwAA/AAAAAAPAAD8AAAAAAMAAPwAAAAAAwAA/AAAAAADAAD8AAAAAAAAAPwAAAAAAAAA8AAAAAAAAADwAAAAAAAAAPAAAAAAAAAA8AAAAAAAAADwAAAAAAMAAMAAAAAAAwAAwAAAAAADAADAAAAAAAMAAMAAAAAAAwAAwAAAAAADAAAAAAAAAAMAAAAAAAAADwAAAAAAAAAPAAAAAAAAAA8AAAAAAAAADwAAAAAAAAAPAADAAAAAAA8AAMAAAAAADwAAwAAAAAAPAADwAAAAAA8AAPAAAAAADwAA/4AAAAA/AAD/gAAAAD8AAP+AAAAAPwAA/+AAAAA/AAD/4AAAAD8AAP/4AAAH/wAA//gAAAf/AAD/+AAAB/8AAP//wAP//wAA///AA///AAA=')

    with open(os.path.join(tempfile.gettempdir(), 'the_d6.ico'), 'wb') as f:
        f.write(d6_image_raw)


########################
# The "Updating" window
########################

class UpdateWindow():
    def __init__(self, parent):
        # Initialize a new GUI window
        self.parent = parent
        self.window = tkinter.Toplevel(self.parent)
        self.window.withdraw()  # Hide the GUI
        self.window.title(mod_pretty_name + ' Updater')  # Set the GUI title
        self.window.iconbitmap(os.path.join(tempfile.gettempdir(), 'the_d6.ico'))  # Set the GUI icon
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', lambda: close_mod(self))

        # Updating message
        updating_message = tkinter.Message(self.window, justify=tkinter.CENTER, font='font 40', text='Updating...', width=600)
        updating_message.pack()

        # Rotating dice
        self.canvas = tkinter.Canvas(self.window, width=100, height=100)
        self.canvas.pack()
        self.dice_angle = 0
        self.d6_image = Image.open(os.path.join(tempfile.gettempdir(), 'the_d6.ico'))
        self.rotated_d6 = ImageTk.PhotoImage(self.d6_image)
        self.d6 = self.canvas.create_image(50, 35, image=self.rotated_d6)

        # Show the GUI
        self.window.deiconify()

        # Spawn an update thread
        self.parent.after(1, self.start_update)

    def start_update(self):
        self.thread_potentially_failed = False
        self.queue = queue.Queue()
        self.updater_task = UpdaterTask(self.queue)
        self.updater_task.start()
        self.parent.after(50, self.process_queue)

    def process_queue(self):
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

            # The update has finished, so as a sanity check, see if the program exists
            program_exe = os.path.join(program_directory, mod_name + '.exe')
            if not os.path.isfile(program_exe):
                error('The ' + mod_pretty_name + ' program was updated, but the "' + program_exe + '" file does not exist, so something went wrong along the way.\nPlease redownload the program manually.', None)

            # Open the program
            subprocess.Popen([program_exe], cwd=program_directory)
            sys.exit()

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
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        # Check to see if the zip file already exists
        mod_zip_name = mod_name + '.zip'
        mod_zip_path = os.path.join(tempfile.gettempdir(), mod_zip_name)
        self.delete_file_if_exists(mod_zip_path)

        # Download the zip file
        try:
            url = 'https://github.com/' + repository_owner + '/' + mod_name + '/releases/download/' + latest_version + '/' + mod_zip_name
            urllib.request.urlretrieve(url, mod_zip_path)
        except Exception as e:
            self.error('Failed to download the latest version from GitHub:', e)

        # Delete everything in the program directory
        for file_name in os.listdir(program_directory):
            self.delete_file_if_exists(os.path.join(program_directory, file_name))

        # Extract the zip file to the program directory
        try:
            with zipfile.ZipFile(mod_zip_path, 'r') as z:
                z.extractall(program_directory)
        except Exception as e:
            self.error('Failed to extract the downloaded "' + mod_zip_path + '" file:', e)

        # Delete the zip file
        self.delete_file_if_exists(mod_zip_path)

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
    global program_directory
    global latest_version

    # Initialize the GUI
    root = tkinter.Tk()
    root.withdraw()  # Hide the GUI

    # Validate command-line arguments
    if len(sys.argv) != 2:
        error('The updater must be provided with an argument of the directory that the program is installed to.', None)
    program_directory = sys.argv[1]
    if not os.path.isdir(program_directory):
        error('The program directory provided does not exist or is not a directory.', None)

    # TkInter callbacks run in different threads, so if we want to handle generic exceptions caused in a TkInter callback, we must define a specific custom exception handler for that
    tkinter.Tk.report_callback_exception = callback_error

    # Create the D6 image
    make_d6_picture()

    # Check to see what the latest version of the mod is
    try:
        url = 'https://raw.githubusercontent.com/' + repository_owner + '/' + mod_name + '/master/options.ini'
        master_options_ini = urllib.request.urlopen(url).read().decode('utf8')

        # Get the mod version
        match = re.search(r'mod_version = (\d+.\d+.\d+)', master_options_ini)
        if match:
            latest_version = match.group(1)
        else:
            error('When trying to find what the latest version is, I failed to find the "mod_version" line in the "options.ini" file from GitHub.', None)

    except Exception as e:
        error('Failed to check GitHub for the latest version:', e)

    # Sleep for 0.5 seconds to allow the parent program time to close
    time.sleep(0.5)

    # Show the updating window
    UpdateWindow(root)
    root.mainloop()


######################
# Program entry point
######################

if __name__ == '__main__':
    # Initialize logging
    log_file = os.path.join(tempfile.gettempdir(), mod_name + '-standalone-updater-error-log.txt')
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
