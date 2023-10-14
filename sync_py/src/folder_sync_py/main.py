#!/usr/bin/env python3
from arguments import *
from sync import *
import time
import schedule
import signal

def signal_handler(num,frame):
    print("Synchronization process stopped")
    sys.exit(0)

def synchronize(src, dest, log, sync_time, min = False, hour = False):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    
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
    
    #signal.signal(signal.SIGINT, signal_handler)
    #signal.signal(signal.SIGTSTP, signal_handler)
    
    args = parse_arguments()
    args = arg_format_fix(args)
    if not arg_file_system_check(args):
        sys.exit(1)    
    
    synchronize(args.source, args.destination, args.output, args.time, args.minute, args.hour)
    
    #unit = "seconds"
    #if args.minute:
    #    schedule.every(args.time).minutes.do(sync_folder,args.source,args.destination, args.output)
    #    unit = "minutes"
    #elif args.hour:
    #    schedule.every(args.time).hours.do(sync_folder,args.source,args.destination, args.output)
    #    unit = "hours"
    #else:
    #    schedule.every(args.time).seconds.do(sync_folder,args.source,args.destination, args.output)

    #write first log message
#    with open(args.output, 'a') as log_file:
      #  print_msg("synchronizing " + args.destination + " to " + args.source + " with " + str(args.time) + ' ' + unit + " interval", log_file)
    #do first sync
 #   sync_folder(args.source, args.destination, args.output)
    #continue on schedule
  #  while (True):
   #     schedule.run_pending()
    #    time.sleep(1)