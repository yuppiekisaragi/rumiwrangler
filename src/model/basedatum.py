import os
import sys
import glob
import logging
from datetime import datetime as dt
from datetime import timezone as tz

from pydantic import BaseModel, ValidationError
from typing import ClassVar

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)

class BaseDatum(BaseModel):

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = ''
    prefix : ClassVar[str] = ''
    encoding : ClassVar[str] = 'utf-8'
    assume_utc : ClassVar[bool] = True

    # There are no model attributes defined on BaseDatum. This primarily
    # exists to contain the basic classmethods (get all files from glob,
    # factory function to return a model instance for each line in the glob,
    # et cetera). 

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
            with open(data_file, 'r', encoding='latin-1') as data_fh:
                for line in data_fh:
                    line = line.strip()
                    filename = os.path.basename(data_file)
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
                        err = f'{errloc}: parse {line}: {e}'
                        logger.error(err)
                        continue

                    try:
                        model = cls(**parsed)
                    except ValidationError as e:
                        err = f'{errloc}: validate {line}: {e}\n'
                        err += f'model: {cls.__name__}\n'
                        err += f'{parsed}'
                        logger.error(err)
                        continue

                    if cls.assume_utc and hasattr(model, 'raw_ts'):
                        model.raw_ts = model.raw_ts.replace(tzinfo=tz.utc)
                    yield model


