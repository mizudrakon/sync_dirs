#!/usr/bin/env python3
from arguments import *
from sync import *
import time
import schedule
import signal

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