import os
import sys
import logging

from args import parse_cli_args
from getdivelist import get_selected_dives
from getdivedata import get_dive_data
from model.herc_dive import HercDiveDatum
from model.herc_oct import HercOCTDatum
from model.herc_vfr import HercVFRDatum

logger = logging.getLogger()


if __name__ == '__main__':

    logging.basicConfig()

    #argparse will terminate and print usage if anything goes wrong, so
    #no need to trap and handle exceptions here.
    args = parse_cli_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    cruisepath = os.path.join(args.cruise_location, args.cruise)
    dives = get_selected_dives(cruisepath, 
            skip=args.skip, 
            only=args.only,
            start_ts=args.start_ts,
            end_ts=args.end_ts)

    for dive in dives:
        logger.info(f'RUMIWrangling {args.cruise}/{dive.dive}')
        logger.info(f'inwater: {dive.inwater}')
        logger.info(f'onbottom: {dive.onbottom}')
        logger.info(f'offbottom: {dive.offbottom}')
        logger.info(f'ondeck: {dive.ondeck}')
        get_dive_data(cruisepath, 
                dive, 
                start_ts=args.start_ts, 
                end_ts=args.end_ts) 
