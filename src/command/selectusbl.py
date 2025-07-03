import os
import sys
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from command.base import BaseCommand
from model.herc_usbl import HercUSBLDatum

logger = logging.getLogger(__name__)

def drop_us(ts):
    return ts.replace(microsecond=0)

def get_us(ts):
    return ts.microsecond

class SelectUSBLCommand(BaseCommand):

    def target(self):
        raw_models = self._select_rows(HercUSBLDatum.modelname)
        rawdata_1s = []

        bin_ts = last_bin_ts = None
        bin_data = []

        for i, raw in enumerate(raw_models):

            this_ts = drop_us(raw.raw_ts)
            if not bin_ts:
                bin_ts = last_bin_ts = this_ts
            if this_ts == bin_ts:
                #keep appending to the current bin
                bin_data.append(raw)

            else:
                #take the best accuracy reading from this bin
                bin_data.sort(key = (lambda d:d.accuracy))
                if bin_data[0].accuracy == bin_data[-1].accuracy:
                    #resort for most consistent time interval between
                    #samples.
                    resort = (lambda d:get_us(d.raw_ts) - get_us(last_bin_ts))
                    bin_data.sort(key = resort)
                bin_data[0].ts = this_ts
                rawdata_1s.append(bin_data[0])
   
                try:
                    #reset the bin
                    last_bin_ts = this_ts
                    bin_ts = drop_us(raw_models[i+1].raw_ts)
                    bin_data = []
                except IndexError:
                    #we're at the end, so nothing to advance
                    pass

        update_dicts = []
        for raw in rawdata_1s:
            update_dict = {}
            update_dict['id'] = raw.id
            update_dict['ts'] = raw.ts
            update_dicts.append(update_dict)

        self._update_rows(HercUSBLDatum.modelname, update_dicts)
