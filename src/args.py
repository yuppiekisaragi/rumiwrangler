import os
import sys
import argparse
import logging
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta as td

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from const import CRUISE_LOCATION

logger = logging.getLogger(__name__)

def start_end(args):
    fmt = '%Y%m%dT%H%M%S'
    if args.start_ts and args.end_ts:
        start_ts = dt.strptime(args.start_ts, fmt).replace(tzinfo=tz.utc)
        args.start_ts = start_ts
        end_ts = dt.strptime(args.end_ts, fmt).replace(tzinfo=tz.utc)
        args.end_ts = end_ts
    elif args.start_ts and not args.end_ts:
        raise ValueError('--start-ts also requires --end-ts')
    elif args.end_ts and not args.start_ts:
        raise ValueError('--end-ts also requires --start-ts')
    return args

def now_since(args):
    if args.now and args.since:
        now_ts = dt.now(tz=tz.utc).replace(microsecond=0)
        args.start_ts = now_ts - td(seconds=args.since)
        args.end_ts = now_ts
    elif args.now and not args.since:
        raise ValueError('--now also requires --since')
    elif args.since and not args.now:
        raise ValueError('--since also requires --now')
    return args

def parse_cli_args():
    parser = argparse.ArgumentParser()

    #options to manage list of dives
    parser.add_argument('cruise')
    parser.add_argument('command')
    parser.add_argument('--skip', action='append')
    parser.add_argument('--only', action='append')
    parser.add_argument('--cruise-location', default=CRUISE_LOCATION)
    parser.add_argument('--db-location', default=os.getcwd())

    #options to manage logging
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--verbose', action='store_true')

    #options to manage processing within limited time ranges
    #process over absolute time range
    parser.add_argument('--start-ts',
            default=None,
            help='Absolute UTC timestamp to start at. %Y%m%dT%H%M%S.')
    parser.add_argument('--end-ts', 
            default=None,
            help='Absolute UTC timestamp to end at. %Y%m%dT%H%M%S.')
    #process over relative time range
    parser.add_argument('--now', 
            action='store_true',
            help='Use current time as --end_ts.')
    parser.add_argument('--since', 
            default=0, 
            type=int,
            help='Use this number of seconds before now as --start-ts.')

    #this will exit w/ error code 2 if it fails, and print usage
    #to stderr
    args = parser.parse_args()

    #normalize argument values
    #for processing over specific time ranges, the main program always
    #deals in absolute, aware DateTimes. So the --now and --since 
    #options get normalized to datetime instances.
    try:
        args = start_end(args)
    except (ValueError, AttributeError) as e:
        parser.error(f'cannot parse --start-ts/--end-ts: {str(e)}')
        #this will exit with exit code 2

    try:
        args = now_since(args)
    except (ValueError, AttributeError) as e:
        parser.error(f'cannot parse --now/--since: {str(e)}')
        #this will exit with exit code 2

    return args

