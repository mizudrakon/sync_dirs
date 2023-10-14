#!/usr/bin/env python3
import sys
import os
import argparse


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

#testing
if __name__ == '__main__':
    args = parse_arguments()
    args = arg_format_fix(args)
    print(args)
    if not arg_file_system_check(args):
        print("Error in user input!")
        sys.exit(1)
    sys.exit(0)