#!/usr/bin/env python3
from arguments import *
from sync import *

if __name__ == '__main__':
    args = parse_arguments()
    args = linux_home(args)
    printls(args.source)
    sys.exit(0)