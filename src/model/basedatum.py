import os
import sys
import glob
import logging
from datetime import datetime as dt
from datetime import timezone as tz

from pydantic import BaseModel, ValidationError
from typing import ClassVar, Optional

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)

class BaseDatum(BaseModel):

    # Human readable name of this class. Pydantic sets the 
    # __class__.__name__ attribute to ModelMetaclass which is great
    # for pydantic, but then we can't use it in log messages and
    # so forth...
    modelname: ClassVar[str] = 'BaseDatum'

    # Lambda expression used to select the winning datum when sorting
    # them into 1Hz bins. The simplest approach is just to pick the 
    # datum closest to microsecond=0.
    bin_sort_lambda = (lambda d: d.raw_ts.microsecond)

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = ''
    prefix : ClassVar[str] = ''
    encoding : ClassVar[str] = 'utf-8'
    assume_utc : ClassVar[bool] = True

    #this is dropped going from Pydantic -> ORM, but we keep it
    #in the model when going from ORM -> Pydantic -> do stuff -> update DB

    id : Optional[int] = 0

    @classmethod
    def get_data_files(cls, basepath):
        logger.debug(f'get data files from :{basepath} {cls.glob}')
        data_files = glob.glob(os.path.join(basepath,cls.glob))
        data_files.sort()
        logger.debug(f'found {len(data_files)} files')
        return data_files

    @classmethod
    def parse_line(cls, line, filename=''):
        return {}

    @classmethod
    def iter_data(cls, basepath):
        data_files = cls.get_data_files(basepath)
        for data_file in data_files:
            fileline = 0
            filename = os.path.basename(data_file)
            with open(data_file, 'r', encoding='latin-1') as data_fh:
                for line in data_fh:
                    line = line.strip()
                    fileline += 1
                    errloc = f'{filename},{fileline}'

                    if not line:
                        #logger.debug(f'{errloc} skipping empty line')
                        continue
                    elif line.startswith('#'):
                        #logger.debug(f'{errloc} skipping comment line')
                        continue
                    elif cls.prefix and not line.startswith(cls.prefix):
                        #logger.debug(f'{errloc} skipping non-matching prefix')
                        continue

                    try:
                        parsed = cls.parse_line(line, filename=filename)
                    except ValueError as e:
                        err = f'{errloc}: cannot parse as {cls.modelname}:\n'
                        err += f'{line}'
                        logger.error(err)
                        continue 

                    try:
                        model = cls(**parsed)
                    except ValidationError as e:
                        err = f'{errloc}: cannot validate as {cls.modelname}\n'
                        err += f'{line}: {e}\n'
                        err += f'{parsed}\n'
                        err += f'Exception {e.__class__}: {str(e)}'
                        logger.error(err)
                        continue

                    if cls.assume_utc and hasattr(model, 'raw_ts'):
                        model.raw_ts = model.raw_ts.replace(tzinfo=tz.utc)
                    yield model

    def to_orm(self, ormclass):
        modeldict = self.model_dump()
        if 'id' in modeldict:
            modeldict.pop('id')
        return ormclass(**modeldict)

    @classmethod
    def from_orm(cls, ormdict):
        if '_sa_instance_state' in ormdict:
            ormdict.pop('_sa_instance_state')
        #We actually do want id when going from ORM -> Pydantic.
        #When rows are getting pulled from the db back into Pydantic
        #models, having id since nice, since it makes db updates very
        #simple.
        #if 'id' in ormdict:
        #    ormdict.pop('id')
        return cls(**ormdict)
