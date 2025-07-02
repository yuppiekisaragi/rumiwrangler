import os
import sys
import logging

from sqlalchemy.engine import reflection

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from command.base import BaseCommand
from model.lookup import raw_model_classes, raw_model_ormclasses

logger = logging.getLogger(__name__)

class ImportRawCommand(BaseCommand):

    def _setup_raw_table(self, raw_model_name):

        logger.info(f'_setup_raw_table {raw_model_name}')
        raw_model_ormclass = raw_model_ormclasses[raw_model_name]
        inspect = reflection.Inspector.from_engine(self._engine)
        #ignore checking schema at first
        if not inspect.has_table(raw_model_name, None):
            logger.info(f'creating table {raw_model_name}')
            #create table, only if it doesn't exist
            raw_model_ormclass.metadata.create_all(self._engine)
        else:
            logger.debug(f'{raw_model_name}: exists')

    def _get_dive_dataset(self, raw_model_name):
        raw_model_class = raw_model_classes[raw_model_name]
        if self.start_ts and self.end_ts:
            st = start_ts
            et = end_ts
        else:
            st = self.dive.onbottom
            et = self.dive.offbottom

        dataset = []
        for datum in raw_model_class.iter_data(self.cruisepath):
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

    #def _get_dive_data(self):
        

    def target(self):
        raw_model_names = [k for k in raw_model_classes.keys()]
        for raw_model_name in raw_model_names:
            logger.info(raw_model_name)
            self._setup_raw_table(raw_model_name)

            #parse everything and summarize info
            dataset = self._get_dive_dataset(raw_model_name)
            logger.info(f'dataset: {raw_model_name}')
            logger.info(f'values: {len(dataset)}')
            logger.info(f'first timestamp: {dataset[0].raw_ts}')
            logger.info(f'last timestamp: {dataset[-1].raw_ts}')

            #set up ORM models so we can put it in the db
            raw_model_ormclass = raw_model_ormclasses[raw_model_name]
            datasetorm = [d.to_orm(raw_model_ormclass) for d in dataset]
            self._db_session.add_all(datasetorm)
            self._db_session.commit()
