#!/usr/bin/env python3
import os
import sys
import shutil
import datetime

#I'm just using '/' as delimiter in paths becaue I expect os and shutil to handle it in Windows too
#I'll test it later and switch to a platform dependant variable if it doesn't work

# t is the required number of \t when printing, f is just check if we're supposed to print files
def printls(path = '.',tab='\t', t = 0,f = True):
    """Function to simply write out a folder contents recursively"""
    # make a list using os.scandir()
    L = [e for e in os.scandir(path)]
    for e in L:
        #skip symlinks or hidden files
        if e.is_symlink() or e.name[0] == '.':
            continue
        #if file and we want file: print
        if f and e.is_file():
            print(tab*t,end='')
            print(e.name + ' modified:' + str(e.stat().st_mtime))
            continue
        #if dir go deeper
        if  e.is_dir():
            print(tab*t,end='')
            print(e.name + '/')
            printls(path + '/' + e.name,tab,t+1,f)

def remove_dir(dir_path):
    """Function that removes all contents of a specified directory and the directory itself"""
    #remove the directory contents
    Ls = [entry for entry in os.scandir(dir_path)]
    for entry in Ls:
        if entry.is_file():
            os.remove(entry)
            print(str(datetime.datetime.now()) + ' ' + dir_path + '/' + entry.name + ' file removed')
            continue
        #if dir, remove each file first
        if  entry.is_dir():
            remove_dir(entry.path())
    #remove the directory
    os.rmdir(dir_path)
    print(str(datetime.datetime.now()) + ' ' + dir_path + ' folder removed')
    return True

def sync_folder_content(origin, replica, out):
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
        
        replica_entry_path = replica + '/' + entry.name
        if entry.is_file():
            #copy file if it doesn't exist, or copy over if it needs updating
            if not os.path.isfile(replica_entry_path) or entry.stat().st_mtime > os.stat(replica_entry_path).st_mtime:
                shutil.copy2(entry,replica) 
                print(str(datetime.datetime.now()) + ' ' + entry.path + ' copied file')
                continue
        if entry.is_dir():
            #make dir with same rights and content if it doesn't exist
            #we don't copytree() to have more control and report each file copied
            if not os.path.isdir(replica_entry_path):
                os.mkdir(replica_entry_path,entry.stat().st_mode)
                print(str(datetime.datetime.now()) + ' ' + replica_entry_path + ' made folder')
            #even if it does, we need to enter it and check its content
            sync_folder_content(origin + '/' + entry.name, replica_entry_path, out)
    #removing deleted files and directories 
    for entry in replica_Ls:
        path_to_entry = replica + '/' + entry
        if not At[replica_Ls.index(entry)]:
            if os.path.isfile(path_to_entry):
                os.remove(path_to_entry)
                print(str(datetime.datetime.now()) + ' ' + path_to_entry + ' file removed')
                continue
            if os.path.isdir(path_to_entry):
                remove_dir(path_to_entry)


#first preparation function for the copy_folder_content
def sync_folder(origin, replica, out = '.'):
    """Creates or enters the replica folder and starts the process"""
    #make the root dir
    origin_name = os.path.basename(origin)
    replica = replica + '/' + origin_name 
    if not os.path.isdir(replica):
        os.mkdir(replica, os.stat(origin).st_mode)
        print(str(datetime.datetime.now()) + origin_name + ' made folder')
    sync_folder_content(origin, replica, out)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
    else:
        #sys.exit(1)
        src_dir = "/home/cryptid/Programs/Python/Veeam/TESTdir/original/simple"
    if len(sys.argv) > 2:
        dest_dir = sys.argv[2]
    else:
        #sys.exit(1)
        dest_dir = "/home/cryptid/Programs/Python/Veeam/TESTdir/replica"
    sync_folder(src_dir, dest_dir)
