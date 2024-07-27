import json
import time
import datetime
import get_full_path
import os
import shutil #allows for copying a file to make a backup
import errno
from adafruit_servokit import ServoKit
from gpiozero import LED, RGBLED, Button
from main import GATES_FILE, TOOLS_FILE, BACKUP_DIR


    #print(f'These are your tools {gates}')

def backup_file(full_path, note = '', backup_directory = BACKUP_DIR):
    '''Takes backup directory and file_name and backs the file up with date stamp'''
    backup_dir_path = get_full_path(backup_directory)
    if note != '':
        note = f"_{note}"
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_file_name = f"{os.path.basename(full_path+note).split('.')[0]}_{timestamp}.json"
    backup_path = os.path.join(backup_dir_path, backup_file_name)
    if not os.path.exists(backup_dir_path):
        try:
            os.makedirs(backup_dir_path)
        except:
            print(f"Failed to create backup directory at {backup_dir_path}")
            return False
    try:
        shutil.copyfile(full_path, backup_path)
        print(f"Backup of {full_path} created at {backup_path}")
        return True
    except:
        print(f"Failed to create backup of {full_path} at {backup_path}")
        return False



def save_file(data, full_path):
    try:
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"Data saved to {full_path}")
            return True
    except:
        print(f"Failed to save data to {full_path}")
        return False
      

def get_full_path(filename):
    '''This gets a file associated in the working directory no matter where you run it.
        Useful for VSCode where the terminal doesn't always reside in the directory you are working out of.
        REQUIRES --- 
        from os.path import dirname, join
    '''
    current_dir = os.path.dirname(__file__)  # get current working directory
    full_path = os.path.join(current_dir, f"{filename}")  # set file path
    return(full_path)

# Function to convert hex string to integer
def hex_to_int(hex_str):
    return int(hex_str, 16)


if __name__ == "__main__":
    pass