import os
import sys
import logging

from sqlalchemy import create_engine, select, update
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from model.lookup import model_classes, model_ormclasses

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
        self.cruisepath = cpath
        #dbpath = os.path.join(self.args.db_location, f'{cruise}.db')
        dburl = f'sqlite:///./{self.cruise}.db'
        self.dburl = dburl 
        self.dive = dive
        self.start_ts = start_ts
        self.end_ts = end_ts

    def _setup_table(self, model_name):

        logger.info(f'_setup_table {model_name}')
        model_ormclass = model_ormclasses[model_name]
        inspect = reflection.Inspector.from_engine(self._engine)
        #ignore checking schema at first
        if not inspect.has_table(model_name, None):
            logger.info(f'creating table {model_name}')
            #create table, only if it doesn't exist
            model_ormclass.metadata.create_all(self._engine)

    #create
    def _insert_rows(self, model_name):
        pass

    #read
    def _select_rows(self, model_name):
        model_class = model_classes[model_name]
        model_ormclass = model_ormclasses[model_name]

        #TODO - handle start_ts and end_ts
        stmt = (select(model_ormclass)
                .where(model_ormclass.dive == self.dive.dive))
        selectr = self._db_session.execute(stmt)

        #return as list of model instances...
        selected = []
        for row in selectr.scalars():
            rowmodel = model_class.from_orm(row.__dict__)
            selected.append(rowmodel)

        return selected

    #update
    def _update_rows(self, model_name, update_dicts):
        model_ormclass = model_ormclasses[model_name]
        updater = self._db_session.execute(
                update(model_ormclass),
                update_dicts)
        self._db_session.commit()
    
    #delete
    def _delete_rows(self, model_name):
        pass

    def execute(self):

        #self._engine = create_engine(self.dburl) 
        self._engine = create_engine(self.dburl)
        Session = sessionmaker(bind=self._engine)
        self._db_session = Session()

        self.target()
