import os
import sys
import logging
import statistics

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
        picked_models = []
   
        #only pick data where beacon==1 (Herc). This dataset is only recorded
        #on a 3-second interval, so we don't need to do anything special to
        #decimate it down to a 1Hz interval.
        herc_models = [m for m in raw_models if m.beacon==1]
        for herc_model in herc_models:
            #drop off the microsecond
            this_ts = drop_us(herc_model.raw_ts)

            #always save the first model, then save models which are 
            #in a new time bin.
            if not picked_models or (this_ts > picked_models[-1].ts):
                herc_model.ts = this_ts
                picked_models.append(herc_model)

        update_dicts = []
        for picked_model in picked_models:
            update_dict = {}
            update_dict['id'] = picked_model.id
            update_dict['ts'] = picked_model.ts
            update_dicts.append(update_dict)

        self._update_rows(HercUSBLDatum.modelname, update_dicts)
