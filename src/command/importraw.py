import os
import sys
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from command.base import BaseCommand
from model.herc_oct import HercOCTDatum
from model.herc_usbl import HercUSBLDatum
from model.herc_vfr import HercVFRDatum

logger = logging.getLogger(__name__)

class ImportRawCommand(BaseCommand):

    def _get_dive_dataset(self, model):
        if self.start_ts and self.end_ts:
            st = start_ts
            et = end_ts
        else:
            st = self.dive.onbottom
            et = self.dive.offbottom

        dataset = []
        for datum in model.iter_data(self.cruisepath):
            #if it's before the start time, skip it, but keep
            #iterating
            if datum.raw_ts < st:
                continue
            elif (not et) or (datum.raw_ts < et):
                #not et - means we're in the current dive
                #defined et - we're in the middle of a complete dive
                dataset.append(datum)
            elif et and datum.raw_ts > et:
                #we've hit the end of the window, stop iterating.
                break
        return dataset

    def _get_dive_data(self):
        divemodels = [HercOCTDatum]
        for model in divemodels:
            dataset = self._get_dive_dataset(model)
            logger.info(f'dataset: {model.modelname}')
            logger.info(f'values: {len(dataset)}')
            logger.info(f'first timestamp: {dataset[0].raw_ts}')
            logger.info(f'last timestamp: {dataset[-1].raw_ts}')

    def target(self):
        self._get_dive_data()


