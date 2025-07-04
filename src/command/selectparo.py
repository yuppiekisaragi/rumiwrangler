import os
import sys
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from command.base import BaseCommand
from model.herc_paro import HercParoDatum

logger = logging.getLogger(__name__)

class SelectParoCommand(BaseCommand):

    def target(self):

        raw_models = self._select_rows(HercParoDatum.modelname)

        rawdata_1s = []
        last_ts = None

        for raw in raw_models:
            this_ts = raw.raw_ts.replace(microsecond=0)
            if not last_ts:
                #first iteration
                last_ts = this_ts
            if this_ts > last_ts:
                #moving to the next time bin
                raw.ts = this_ts
                rawdata_1s.append(raw)    
                last_ts = this_ts

        update_dicts = []
        for raw in rawdata_1s:
            update_dict = {}
            update_dict['id'] = raw.id
            update_dict['ts'] = raw.ts
            update_dicts.append(update_dict)

        self._update_rows(HercParoDatum.modelname, update_dicts)
