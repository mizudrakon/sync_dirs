#!/usr/bin/env python3

""" This is the collection of all the modules from sync_py/src/ folder to work as a single script for conveninet copying. """

import sys
import os
import argparse
import shutil
import datetime
import time
import schedule
import signal

#ARGUMENT PARSING:
def parse_arguments():
    """parses the arguments for the synchronization script, only the source folder address is required, the rest is optional"""
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="address of the source folder for sync")
    parser.add_argument("destination", help="adress to store the replica folder", default=os.getcwd())
    parser.add_argument("-o","--output", help="specify the desired log file location", default=os.getcwd() + "/sync.log")
    parser.add_argument("-t","--time", help="specify the time interval",type=int, default=30)
    parser.add_argument("-m","--minute", help="specify the time interval unit to minutes",action="store_true")
    parser.add_argument("--hour", help="specify the time interval unit to hours",action="store_true")
    return parser.parse_args()

#remove the end slash, change ~ into home dir on linux
def arg_format_fix(args):
    for arg in [args.source, args.destination, args.output]:
        if sys.platform == 'linux' and arg[0] == '~':
            arg = os.getenv('HOME')+arg[1:]
        if arg[-1] == '\\' or arg[-1] == '/':
            arg = arg[:-2]
    return args

def arg_file_system_check(args):
    """checks if the source folder and destination exists"""
    if not os.path.isdir(args.source) or not os.path.isdir(args.destination): 
        print("ERROR: source or destination are not real addresses!")
        return False
    if not os.path.isdir(args.output) and not os.path.isdir(os.path.dirname(args.output)):
        return False
    if os.path.isdir(args.output):
        args.output = args.output + '/sync.log'
    return True

#SYNCHRONIZATION FUNCTIONS:
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


#MAIN FUNCTIONS:
def signal_handler(num,frame):
    print("Synchronization process stopped")
    sys.exit(0)

def get_args():
    """Manages arguments from command line"""
    args = parse_arguments()
    args = arg_format_fix(args)
    if not arg_file_system_check(args):
        sys.exit(1)   
    return args 

def synchronize(src, dest, log, sync_time, min = False, hour = False):
    """Encapsulates the whole process of synchronization"""
    signal.signal(signal.SIGINT, signal_handler)
    #signal.signal(signal.SIGTSTP, signal_handler)
    
    unit = "seconds"
    if args.minute:
        schedule.every(sync_time).minutes.do(sync_folder,src,dest,log)
        unit = "minutes"
    elif args.hour:
        schedule.every(sync_time).hours.do(sync_folder,src,dest,log)
        unit = "hours"
    else:
        schedule.every(sync_time).seconds.do(sync_folder,src,dest,log)

    #write first log message
    with open(log, 'a') as log_file:
        print_msg("synchronizing " + dest + " to " + src + " with " + str(sync_time) + ' ' + unit + " interval", log_file)
    #do first sync
    sync_folder(src, dest, log)
    #continue on schedule
    while (True):
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    args = parse_arguments()
    args = arg_format_fix(args)
    if not arg_file_system_check(args):
        sys.exit(1)    
    args = get_args()
    synchronize(args.source, args.destination, args.output, args.time, args.minute, args.hour)