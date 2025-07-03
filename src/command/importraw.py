import os
import sys
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from command.base import BaseCommand
from model.lookup import (model_classes, 
        model_ormclasses,
        raw_model_names)

logger = logging.getLogger(__name__)

class ImportRawCommand(BaseCommand):

    def _get_dive_dataset(self, model_name):
        model_class = model_classes[model_name]
        if self.start_ts and self.end_ts:
            st = start_ts
            et = end_ts
        else:
            st = self.dive.onbottom
            et = self.dive.offbottom

        dataset = []
        for datum in model_class.iter_data(self.cruisepath):
            #if it's before the start time, skip it, but keep
            #iterating
            if datum.raw_ts < st:
                continue
            elif (not et) or (datum.raw_ts < et):
                #not et - means we're in the current dive
                #defined et - we're in the middle of a complete dive
                #ensure that dive is defined. note that self. dive
                #is a metadata object, in this case we just want the
                #str name of the dive.
                datum.dive = self.dive.dive
                dataset.append(datum)
            elif et and datum.raw_ts > et:
                #we've hit the end of the window, stop iterating.
                break
        return dataset

    #def _get_dive_data(self):
        

    def target(self):
        for raw_model_name in raw_model_names:
            logger.info(raw_model_name)
            self._setup_table(raw_model_name)

            #parse everything and summarize info
            dataset = self._get_dive_dataset(raw_model_name)
            logger.info(f'dataset: {raw_model_name}')
            logger.info(f'values: {len(dataset)}')
            logger.info(f'first timestamp: {dataset[0].raw_ts}')
            logger.info(f'last timestamp: {dataset[-1].raw_ts}')

            #set up ORM models so we can put it in the db
            model_ormclass = model_ormclasses[raw_model_name]
            datasetorm = [d.to_orm(model_ormclass) for d in dataset]
            self._db_session.add_all(datasetorm)
            self._db_session.commit()
