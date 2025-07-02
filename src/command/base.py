import os
import sys
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)

class BaseCommand():
    def __init__(self, 
            args, 
            cruise, 
            dive, 
            start_ts=None,
            end_ts=None):

        self.args = args
        self.cruise = cruise
        cpath = os.path.join(self.args.cruise_location, cruise)
        logger.debug(f'cpath: {cpath}')
        self.cruisepath = cpath
        #dbpath = os.path.join(self.args.db_location, f'{cruise}.db')
        dburl = f'sqlite:///./{self.cruise}.db'
        logger.debug(f'dburl: {dburl}')
        self.dburl = dburl 
        self.dive = dive
        self.start_ts = start_ts
        self.end_ts = end_ts


    def execute(self):

        #self._engine = create_engine(self.dburl) 
        self._engine = create_engine(self.dburl)
        Session = sessionmaker(bind=self._engine)
        self._db_session = Session()

        self.target()
