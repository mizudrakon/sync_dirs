#!/usr/bin/env python3
import os
import sys
import shutil

# t is the required number of \t when printing, f is just check if we're supposed to print files
def printls(path = '.',tab='\t', t = 0,f = True):
    """function to go through a file system tree given an address"""
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


#making a function that will copy the entire tree from root
def copy(origin = '.', replica = '../..', out = './log'):
    #make the root dir
    origin = os.path.abspath(origin)
    origin_name = origin.split('/')[-1]
    replica = os.path.abspath(replica)
    os.mkdir(replica + '/' + origin_name, os.stat(origin).st_mode)
    
    L = [e for e in os.scandir(origin)]
    for e in L:
        #skip symlinks or hidden files
        if e.is_symlink() or e.name[0] == '.':
            continue
        #if file and we want file: print
        if e.is_file():
            shutil.copy2(e,replica) 
            print(e.name + ' modified:' + str(e.stat().st_mtime))
        #if dir go deeper
        if e.is_dir():
            print(e.name + '/')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
    else:
        src_dir = os.getcwd()
    if len(sys.argv) > 2:
        dest_dir = sys.argv[2]
    print(src_dir.split('/')[-1])
    printls(src_dir)

