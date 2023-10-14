#!/usr/bin/env python3
import os
import sys
import shutil
import datetime

#I'm just using '/' as delimiter in paths becaue I expect os and shutil to handle it in Windows too
#I'll test it later and switch to a platform dependant variable if it doesn't work
def separator():
    if sys.platform == 'linux':
        return '/'
    return '\\'

def print_msg(msg, file, quiet = False):
    """Function to write messages both to stdout and file"""
    if not quiet:
        print(msg)
    file.write(msg + '\n')

def remove_dir(dir_path,log_file):
    """Function that removes all contents of a specified directory and the directory itself"""
    #remove the directory contents
    Ls = [entry for entry in os.scandir(dir_path)]
    for entry in Ls:
        if entry.is_file():
            os.remove(entry)
            print_msg(str(datetime.datetime.now()) + ' ' + dir_path + separator() + entry.name + ' file removed', log_file)
            continue
        #if dir, remove each file first
        if  entry.is_dir():
            remove_dir(entry.path())
    #remove the directory
    os.rmdir(dir_path)
    print(str(datetime.datetime.now()) + ' ' + dir_path + ' folder removed')
    return True

def sync_folder_content(origin, replica, log_file):
    """Copy contents of the origin folder to the replica folder"""
    #getting contents of the original directory
    Ls = [entry for entry in os.scandir(origin)]
    #getting contents of the replica to see if any need deleting
    replica_Ls = [entry.name for entry in os.scandir(replica)]
    At = [False]*len(replica_Ls)
    #main loop going throuhg the list of original dir contents and dealing with entries accordingly 
    for entry in Ls:
        #skip symlinks or hidden files
        if entry.is_symlink() or entry.name[0] == '.':
            continue
        
        #files still present in the origin are marked True
        if entry.name in replica_Ls:
            At[replica_Ls.index(entry.name)] = True
        
        replica_entry_path = replica + separator() + entry.name
        if entry.is_file():
            #copy file if it doesn't exist, or copy over if it needs updating
            if not os.path.isfile(replica_entry_path) or entry.stat().st_mtime > os.stat(replica_entry_path).st_mtime:
                shutil.copy2(entry,replica) 
                print_msg(str(datetime.datetime.now()) + ' ' + entry.path + ' - file copied', log_file)
                continue
        if entry.is_dir():
            #make dir with same rights and content if it doesn't exist
            #we don't copytree() to have more control and report each file copied
            if not os.path.isdir(replica_entry_path):
                os.mkdir(replica_entry_path,entry.stat().st_mode)
                print_msg(str(datetime.datetime.now()) + ' ' + replica_entry_path + ' - folder made', log_file)
            #even if it does, we need to enter it and check its content
            sync_folder_content(origin + separator() + entry.name, replica_entry_path, log_file)
    #removing deleted files and directories 
    for entry in replica_Ls:
        path_to_entry = replica + separator() + entry
        if not At[replica_Ls.index(entry)]:
            if os.path.isfile(path_to_entry):
                os.remove(path_to_entry)
                print_msg(str(datetime.datetime.now()) + ' ' + path_to_entry + ' file removed', log_file)
                continue
            if os.path.isdir(path_to_entry):
                remove_dir(path_to_entry, log_file)


#first preparation function for the copy_folder_content
def sync_folder(origin, replica, log_file_name):
    """Creates or enters the replica folder and starts the process"""
    #open a log file in append
    log_file = open(log_file_name,'a')

    print_msg(str(datetime.datetime.now()) + ' started synch process on: ' + origin, log_file)
    origin_name = os.path.basename(origin)
    #replica = replica + separator() + origin_name 
    replica = replica + origin_name 
    if not os.path.isdir(replica):
    #make the root dir
        os.mkdir(replica, os.stat(origin).st_mode)
        print_msg(str(datetime.datetime.now()) + ' ' + origin_name + ' folder made', log_file)
    sync_folder_content(origin, replica, log_file)
    log_file.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
    if len(sys.argv) > 2:
        dest_dir = sys.argv[2]
    else:
        sys.exit(1)
    sync_folder(src_dir, dest_dir)
