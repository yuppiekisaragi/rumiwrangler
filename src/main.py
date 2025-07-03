import os
import sys
import logging

from args import parse_cli_args
from getdivelist import get_selected_dives
from log.debug import debug_args
from command.importraw import ImportRawCommand
from command.selectoct import SelectOCTCommand
from command.selectvfr import SelectVFRCommand

logger = logging.getLogger()

#setup dictionary of command-class mapping
commanddict = {}
commanddict['importraw'] = ImportRawCommand
commanddict['selectoct'] = SelectOCTCommand
commanddict['selectvfr'] = SelectVFRCommand

if __name__ == '__main__':

    logging.basicConfig()

    #argparse will terminate and print usage if anything goes wrong, so
    #no need to trap and handle exceptions here.
    args = parse_cli_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug(debug_args(args))
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
        try:
            cmdclass = commanddict[args.command]
            cmd = cmdclass(args, 
                    args.cruise, 
                    dive, 
                    start_ts=args.start_ts,
                    end_ts=args.end_ts)
            cmd.execute()

        #except Exception as e:
        except NotImplementedError as e:
            logger.error(f'{e.__class__}: {str(e)}')
            sys.exit(1)
