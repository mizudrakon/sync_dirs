#!/usr/bin/env python3
import os
import sys
import shutil
import datetime
import time

# t is the required number of \t when printing, f is just check if we're supposed to print files
def printls(path = '.',tab='\t', t = 0,f = True):
    """function to simply write out a folder contents recursively"""
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
        #if dir go deeper
        if  e.is_dir():
            print(tab*t,end='')
            print(e.name + '/')
            printls(path + '/' + e.name,tab,t+1,f)

def remove_dir(dir_path):
    return True

def copy_folder_content(origin, replica, out):
    """Copy contents of the origin folder to the replica folder"""
    Ls = [entry for entry in os.scandir(origin)]
    ###
    replica_LS = [entry.name for entry in os.scandir(replica)]
    At = [False]*len(replica_LS)
    ###
    for entry in Ls:
        #skip symlinks or hidden files
        if entry.is_symlink() or entry.name[0] == '.':
            continue
        
        #cataloguing files and dirs for possible removal
        if entry.name in replica_LS:
            At[replica_LS.index(entry.name)] = True
        
        replica_entry_path = replica + '/' + entry.name
        if entry.is_file():
            if not os.path.isfile(replica_entry_path) or entry.stat().st_mtime > os.stat(replica_entry_path).st_mtime:
                shutil.copy2(entry,replica) 
                print(str(datetime.datetime.now()) + ' ' + entry.path + ' copied file')
        #make dir with same rights and enter copy it's contents too
        if entry.is_dir():
            if not os.path.isdir(replica_entry_path):
                os.mkdir(replica_entry_path,entry.stat().st_mode)
                #shutil.copystat(origin + '/' + entry.name,replica_entry_path)
                #print(str(os.stat(replica_entry_path).st_mtime) + ' ' + str(entry.stat().st_mtime))
                print(str(datetime.datetime.now()) + ' ' + replica_entry_path + ' made folder')
            copy_folder_content(origin + '/' + entry.name, replica_entry_path, out)
    #print(At) 
    for entry in replica_LS:
        if not At[replica_LS.index(entry)]:
            os.remove(replica + '/' + entry)
            print(str(datetime.datetime.now()) + ' ' + replica + '/' + entry + ' removed')



#first preparation function for the copy_folder_content
def copy_folder(origin = '.', replica = '../..', out = './log'):
    """Creates or enters the replica folder and starts the process"""
    #make the root dir
    #origin = os.path.abspath(origin)
    origin_name = origin.split('/')[-1]
    #replica = os.path.abspath(replica)
    replica = replica + '/' + origin_name 
    if not os.path.isdir(replica):
        os.mkdir(replica, os.stat(origin).st_mode)
        print(str(datetime.datetime.now()) + origin_name + ' made folder')
    copy_folder_content(origin, replica, out)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
    else:
        src_dir = "/home/cryptid/Programs/Python/Veeam/TESTdir/original/simple"
    if len(sys.argv) > 2:
        dest_dir = sys.argv[2]
    else:
        dest_dir = "/home/cryptid/Programs/Python/Veeam/TESTdir/replica"
    #print(src_dir)
    #printls(src_dir)
    copy_folder(src_dir, dest_dir)
