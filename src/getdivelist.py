import os
import sys
import logging

from model.herc_dive import HercDiveDatum

logger = logging.getLogger(__name__)

def get_selected_dives(cruisepath, 
        skip=[], 
        only=[], 
        start_ts=None, 
        end_ts=None):

    #load complete list of dives and ensure it's sorted
    dives = [d for d in HercDiveDatum.iter_data(cruisepath)]
    dives.sort(key = (lambda d:d.dive))

    #process commandline skip/only options
    if skip:
        dives = [d for d in dives if d.dive not in skip]
    if only:
        dives = [d for d in dives if d.dive in only]

    #if the --start-ts/--end-ts window was specified, only return
    #dives that fit into this window. note that --now/--since are
    #normalized to --start-ts/--end-ts
    if start_ts and end_ts:
        all_dives = dives.copy()
        select_dives = []
        for dive in all_dives:
            inwater = dive.inwater
            onbottom = dive.onbottom
            offbottom = dive.offbottom
            ondeck = dive.ondeck

            before = (start_ts < onbottom) and (end_ts < onbottom)
            # after is only set for complete dives (all four markers).
            # if the dive is still happening, offbottom is None, so
            # catch this potential TypeError ahead of time.
            after = offbottom and (start_ts > offbottom)

            windowname = f'{start_ts} - {end_ts}'
            if before:
                logger.debug(f'{windowname} before {dive.dive}, skipping')
                continue
            elif after:
                logger.debug(f'{windowname} after {dive.dive}, skipping')
                continue
            else:
                select_dives.append(dive)
        #replace dives with the updated list
        dives = select_dives

    return dives
