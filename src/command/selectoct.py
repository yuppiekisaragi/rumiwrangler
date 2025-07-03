import os
import sys
import logging

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from command.base import BaseCommand
#from model.lookup import raw_model_classes, raw_model_ormclasses
from model.herc_oct import HercOCTDatum, HercOCTORM

logger = logging.getLogger(__name__)

class SelectOCTCommand(BaseCommand):

    def target(self):

        stmt = (select(HercOCTORM)
                .where(HercOCTORM.dive == self.dive.dive))
        result = self._db_session.execute(stmt)

        octdata_1s = []
        last_ts = None

        for row in result.scalars():
            octdatum = HercOCTDatum.from_orm(row.__dict__)
            this_ts = octdatum.raw_ts.replace(microsecond=0)
            if not last_ts:
                #first iteration
                last_ts = this_ts
            if this_ts > last_ts:
                #moving to the next time bin
                octdatum.ts = this_ts
                octdata_1s.append(octdatum)    
                last_ts = this_ts

        octdicts = []
        for octdatum in octdata_1s:
            octdict = {}
            octdict['id'] = octdatum.id
            octdict['ts'] = octdatum.ts
            logger.info(octdict)
            octdicts.append(octdict)

        self._db_session.execute(update(HercOCTORM),octdicts)
        self._db_session.commit()
