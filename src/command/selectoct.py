import os
import sys
import logging

from sqlalchemy import create_engine, select
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

        stmt = select(HercOCTORM).where(HercOCTORM.dive == self.dive.dive)
        result = self._db_session.execute(stmt)
        for row in result.scalars():
            octdatum = HercOCTDatum.from_orm(row.__dict__)
            logger.info(octdatum.raw_ts)
