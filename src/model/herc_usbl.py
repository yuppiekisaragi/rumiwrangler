import os
import sys
import logging
import re
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

class HercUSBLDatum(BaseDatum):

    # Human readable name of this class. Pydantic sets the 
    # __class__.__name__ attribute to ModelMetaclass which is great
    # for pydantic, but then we can't use it in log messages and
    # so forth...
    modelname: ClassVar[str] = 'HercUSBLDatum'

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = 'raw/datalog/*.SDYN'
    prefix : ClassVar[str] = 'SDYN'
    encoding : ClassVar[str] = 'latin-1'

    # Now, we have all of the Pydantic model attributes.

    dive : Optional[str] = ''
    raw_ts : dt
    ts : Optional[dt] = None
    latitude : float
    longitude : float
    accuracy : float
    depth : float
    beacon : int
    checksum : str

    @staticmethod
    def nmea2deg(degree, minute, card):
        if (card == 'N') or (card == 'E'):
            sign = 1
        else:
            sign = -1
        decideg = (float(degree) + float(minute)/60) * sign
        return decideg
         

    @classmethod
    def parse_line(cls, line, filename=''):
        sline = list(s for s in line.split(' ') if s)
        parsed = {}

        # for filename, we only care about the year/month/day, which
        # begins after the _
        filename = filename.split('_')[0]

        pattern = re.compile(
                r'\$GPGGA,'
                r'(\d+\.\d+),'  # Time (HHMMSS.SSS)
                r'(\d{2})(\d{2}\.\d+),'  # Latitude degrees and minutes
                r'([NS]),'
                r'(\d{3})(\d{2}\.\d+),'  # Longitude degrees and minutes
                r'([EW]),'
                r'\d+,\d+,'  # Skip satellites and fix quality
                r'([\d.]+),'  # Accuracy
                r'([-0-9.]+),'  # Depth
                r'M,0\.0,M,0\.0,' 
                r'(\d{4})\*'  # Beacon index
                r'([0-9A-F]+)' #checksum
                )
        try:
            groups = pattern.search(line).groups()
            d = dt.strptime(filename, '%Y%m%d')
            t = dt.strptime(groups[0], '%H%M%S.%f')
            parsed['raw_ts'] = dt.combine(d.date(), t.time())
            parsed['latitude'] = cls.nmea2deg(*groups[1:4])
            parsed['longitude'] = cls.nmea2deg(*groups[4:7])
            parsed['accuracy'] = float(groups[7])
            parsed['depth'] = float(groups[8])
            parsed['beacon'] = int(groups[9])
            parsed['checksum'] = groups[10]
        except AttributeError as e:
            raise ValueError('$GPGGA failed to match: {e}')
        except IndexError as e:
            raise ValueError('$GPGGA regex missing fields: {e}')
        return parsed

Base = declarative_base()
class HercUSBLORM(Base):

    __tablename__ = HercUSBLDatum.modelname

    id = Column(Integer, primary_key=True)
    dive = Column(String)
    raw_ts = Column(DateTime)
    ts = Column(DateTime, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Float)
    depth = Column(Float)
    beacon = Column(Integer)
    checksum = Column(String)
