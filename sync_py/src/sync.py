#!/usr/bin/env python3
import os
import sys
import shutil
import datetime

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

def copy_folder_content(origin, replica, out):
    """Copy contents of the origin folder to the replica folder"""
    L = [e for e in os.scandir(origin)]
    for e in L:
        #skip symlinks or hidden files
        if e.is_symlink() or e.name[0] == '.':
            continue
        #copy files and write message
        if e.is_file():
            shutil.copy2(e,replica) 
            print(datetime.datetime.now() + ' ' + e.path + ' copied')
        #make dir with same rights and enter copy it's contents too
        if e.is_dir():
            print(datetime.datetime.now() + ' ' + e.path + '/')
            os.mkdir(replica + '/' + e.name,e.stat().st_mode)
            copy_folder_content(origin + '/' + e.name, replica + '/' + e.name,out)


#first preparation function for the copy_folder_content
def copy_folder(origin = '.', replica = '../..', out = './log'):
    """Creates or enters the replica folder and starts the process"""
    #make the root dir
    origin = os.path.abspath(origin)
    origin_name = origin.split('/')[-1]
    replica = os.path.abspath(replica)
    replica = replica + '/' + origin_name 
    os.mkdir(replica, os.stat(origin).st_mode)
    copy_folder_content(origin + '/' + origin_name, replica, out)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
    else:
        src_dir = os.getcwd()
    if len(sys.argv) > 2:
        dest_dir = sys.argv[2]
    print(src_dir.split('/')[-1])
    printls(src_dir)

