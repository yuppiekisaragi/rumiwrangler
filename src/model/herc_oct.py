import os
import sys
import logging
from datetime import datetime as dt
from datetime import timezone as tz

from pydantic import ValidationError
from typing import ClassVar, Optional
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from model.basedatum import BaseDatum

logger = logging.getLogger(__name__)

class HercOCTDatum(BaseDatum):

    # Human readable name of this class. Pydantic sets the 
    # __class__.__name__ attribute to ModelMetaclass which is great
    # for pydantic, but then we can't use it in log messages and
    # so forth...
    modelname: ClassVar[str] = 'HercOCTDatum'

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = 'raw/nav/navest/*.DAT'
    prefix : ClassVar[str] = 'OCT'
    encoding : ClassVar[str] = 'latin-1'

    # Now, we have all of the Pydantic model attributes.

    dive : Optional[str] = ''
    raw_ts : dt
    ts : Optional[dt] = None
    octheading : float
    octpitch : float
    octroll : float

    @classmethod
    def parse_line(cls, line, filename=''):
        sline = list(s for s in line.split(' ') if s)
        parsed = {}

        try:
            parsed['raw_ts'] = sline[1].replace('/', '-') + 'T' + sline[2]
            parsed['octheading'] = sline[7]
            parsed['octpitch'] = sline[8]
            parsed['octroll'] = sline[9]
        except IndexError as e:
            raise ValueError(e)
        except Exception as e:
            err = f'{e.__name__}: {str(e)}'
            raise ValueError(err)

        return parsed

Base = declarative_base()
class HercOCTORM(Base):

    __tablename__ = HercOCTDatum.modelname

    id = Column(Integer, primary_key=True)
    dive = Column(String)
    raw_ts = Column(DateTime)
    ts = Column(DateTime, nullable=True)
    octheading = Column(Float)
    octpitch = Column(Float)
    octroll = Column(Float)
