#!/usr/bin/env python3
from arguments import *
from sync import *
import time
import schedule
import signal

def signal_handler(num,frame):
    print("Synchronization process stopped")
    sys.exit(0)

if __name__ == '__main__':
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    
    args = parse_arguments()
    args = format_fix(args)
    if not file_system_check(args):
        sys.exit(1)    
    unit = "seconds"
    if args.minute:
        schedule.every(args.time).minutes.do(sync_folder,args.source,args.destination, args.output)
        unit = "minutes"
    elif args.hour:
        schedule.every(args.time).hours.do(sync_folder,args.source,args.destination, args.output)
        unit = "hours"
    else:
        schedule.every(args.time).seconds.do(sync_folder,args.source,args.destination, args.output)

    #write first log message
    with open(args.output, 'a') as log_file:
        print_msg("synchronizing " + args.destination + " to " + args.source + " with " + str(args.time) + ' ' + unit + " interval", log_file)
    #do first sync
    sync_folder(args.source, args.destination, args.output)
    #continue on schedule
    while (True):
        schedule.run_pending()
        time.sleep(1)