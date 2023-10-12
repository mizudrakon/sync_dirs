#!/usr/bin/env python3
import sys
import os
import argparse


def parse_arguments():
    """parses the arguments for the synchronization script, only the source folder address is required, the rest is optional"""
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="address of the source folder for sync")
    parser.add_argument("-d","--destination", help="adress to store the replica folder", default=os.getcwd())
    parser.add_argument("-o","--output", help="specify the desired log file location", default=os.getcwd())
    parser.add_argument("-t","--time", help="specify the time interval",type=int, default=60)
    return parser.parse_args()

def linux_home(args):
    for arg in [args.source, args.destination, args.output]:
        if sys.platform == 'linux' and arg[0] == '~':
            arg = os.getenv('HOME')+arg[1:]
    return args

def file_system_check(args):
    """checks if the source folder and destination exists"""
    if not os.path.isdir(args.source) or not os.path.isdir(args.destination): 
        return False
    if not os.path.isdir(args.output):
        return False
    return True

if __name__ == '__main__':
    args = parse_arguments()
    args = linux_home(args)
    print(args)
    if not file_system_check(args):
        print("Error in user input!")
        sys.exit(1)
    sys.exit(0)