import os
import sys
import logging

from model.herc_oct import HercOCTDatum
from model.herc_usbl import HercUSBLDatum
from model.herc_vfr import HercVFRDatum

logger = logging.getLogger(__name__)

def get_dive_dataset(cruisepath, dive, model, start_ts=None, end_ts=None):
    if start_ts and end_ts:
        st = start_ts
        et = end_ts
    else:
        st = dive.onbottom
        et = dive.offbottom

    dataset = []
    bin_ts = None
    bin_data = []
    for datum in model.iter_data(cruisepath):
        #skip any datum that's before our start time, but continue
        #iterating in this loop.
        if datum.raw_ts < st:
            continue
        
        #we've ruled out conditions where this is skipped entirely.
        #in the import phase (where raw data is being read from files)
        #we don't care about binning/selecting/anything yet, that's
        #done later. So all datums within the time range go into 
        #dataset

        elif (not et) or (datum.raw_ts < et):
            dataset.append(datum)
            #while we're in the middle of the dataset, now we deal
            #with binning this on 1-second intervals.
            #this_bin_ts = datum.raw_ts.replace(microsecond=0)
            
            #if not bin_ts:
            #    bin_ts = this_bin_ts
            #if this_bin_ts == bin_ts:
                #append this datum to the current bin
            #    bin_data.append(datum)
            #elif bin_data and (this_bin_ts > bin_ts):
                #we're onto a new bin, now. pick a datum from the last
                #bin and append it to the main dataset.
                #bin_data.sort(key=(lambda d:d.raw_ts.microsecond))
            #    bin_data.sort(key=model.bin_sort_lambda)
            #    print(f'winner: {bin_data[0]}')
            #    print(f'loser: {bin_data[-1]}')
            
                #pick whatever is sorted to the top. we know *something*
                #is in this bin, since bin_data == True.
            #    dataset.append(bin_data[0])

            #    bin_data = []
            #    bin_ts = this_bin_ts
            dataset.append(datum)

        #we've reached the endpoint of the time window, so stop
        #iterating.
        elif et and datum.raw_ts > et:
            break 

    return dataset

def get_dive_data(cruisepath, dive, start_ts=None, end_ts=None):

    #divedata = {}
    #divemodels = [HercOCTDatum, HercUSBLDatum, HercVFRDatum]
    divemodels = [HercOCTDatum]

    for model in divemodels:
        #key = model.modelname
        #divedata[key] = 
        dataset = get_dive_dataset(cruisepath, 
                dive, 
                model, 
                start_ts=start_ts,
                end_ts=end_ts)

        logger.info(f'dataset: {model.modelname}')
        logger.info(f'values: {len(dataset)}')
        logger.info(f'first timestamp: {dataset[0].raw_ts}')
        logger.info(f'last timestamp: {dataset[-1].raw_ts}')
