import os
import sys
import logging
from datetime import datetime as dt
from datetime import timezone as tz

from pydantic import ValidationError
from typing import ClassVar, Optional

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from model.basedatum import BaseDatum

logger = logging.getLogger(__name__)

class HercDiveDatum(BaseDatum):

    # Human readable name of this class. Pydantic sets the 
    # __class__.__name__ attribute to ModelMetaclass which is great
    # for pydantic, but then we can't use it in log messages and
    # so forth...
    modelname : ClassVar[str] = 'HercDiveDatum'

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = 'processed/dive_reports/dives.tsv'
    prefix : ClassVar[str] = 'H'
    encoding : ClassVar[str] = 'latin-1'

    # Now, we have all of the Pydantic model attributes.

    dive: str
    site: str
    inwater: dt	
    onbottom: Optional[dt]
    offbottom: Optional[dt]
    ondeck: Optional[dt]

    @classmethod
    def parse_line(cls, line, filename=''):
        sline = list(s for s in line.split('\t') if s)
        parsed = {}
        #logger.debug(sline)

        try:
            parsed['dive'] = sline[0]
        except IndexError:
            raise ValueError('cannot parse field 0, dive')
        try:
            parsed['site'] = sline[1].replace('_', ' ')
        except IndexError:
            raise ValueError('cannot parse field 1, site')
        try:
            parsed['inwater'] = sline[2]
        except IndexError:
            raise ValueError('cannot parse field 2, inwater')
        try:
            parsed['onbottom'] = sline[3]
        except IndexError:
            raise ValueError('cannot parse field 3, onbottom')
        try:
            parsed['offbottom'] = sline[4]
        except IndexError:
            #offbottom is None for dives that are still happening
            parsed['offbottom'] = None
        try:
            parsed['ondeck'] = sline[5]
        except IndexError:
            parsed['ondeck'] = None
            #ondeck is None for dives that are still happening

        return parsed

class HercDiveStatsDatum(BaseDatum):

    # Human readable name of this class. Pydantic sets the 
    # __class__.__name__ attribute to ModelMetaclass which is great
    # for pydantic, but then we can't use it in log messages and
    # so forth...
    modelname : ClassVar[str] = 'HercDiveStatsDatum'

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = 'processed/dive_reports/H*/H*-stats.tsv'
    prefix : ClassVar[str] = ''
    encoding : ClassVar[str] = 'latin-1'

    # Now, we have all of the Pydantic model attributes.
    cruise: str
    dive: str
    site: str
    inwatertime: dt
    inwaternav: str
    ondecktime: str
    ondecknav: str
    onbottomtime: dt
    onbottomnav: str
    onbottomdepth: float
    offbottomtime: dt
    offbottomnav: str
    offbottomdepth: float
    hercmaxdepth: float
    hercavgdepth: float
    argusmaxdepth: float
    argusavgdepth: float
    totaltime: float
    bottomtime: float

    @classmethod
    def parse_line(cls, line, filename=''):
        sline = list(s for s in line.split('\t') if s)
        parsed = {}

        try:
            parsed['cruise'] = sline[0]
            parsed['dive'] = sline[1]
            parsed['site'] = sline[2].replace('_', ' ')
            parsed['inwatertime'] = sline[3]
            parsed['inwaternav'] = sline[4]
            parsed['ondecktime'] = sline[5]
            parsed['ondecknav'] = sline[6]
            parsed['onbottomtime'] = sline[7]	
            parsed['onbottomnav'] = sline[8]
            parsed['onbottomdepth'] = float(sline[9])
            parsed['offbottomtime'] = sline[10]
            parsed['offbottomnav'] = sline[11]
            parsed['offbottomdepth'] = float(sline[12])
            parsed['hercmaxdepth'] = float(sline[13])
            parsed['hercavgdepth'] = float(sline[14])
            parsed['argusmaxdepth'] = float(sline[15])
            parsed['argusavgdepth'] = float(sline[16])
            parsed['totaltime'] = float(sline[17])
            parsed['bottomtime'] = float(sline[18])
        except IndexError as e:
            raise ValueError(e)

        return parsed

class HercDiveSummaryDatum(BaseDatum):

    # Human readable name of this class. Pydantic sets the 
    # __class__.__name__ attribute to ModelMetaclass which is great
    # for pydantic, but then we can't use it in log messages and
    # so forth...
    modelname : ClassVar[str] = 'HercDiveSummaryDatum'

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = 'raw/nav/navest/*.DAT'
    prefix : ClassVar[str] = 'OCT'
    encoding : ClassVar[str] = 'latin-1'

    # Now, we have all of the Pydantic model attributes.
