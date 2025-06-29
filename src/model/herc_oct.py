import os
import logging
from datetime import datetime as dt
from datetime import timezone as tz

from pydantic import ValidationError
from typing import ClassVar

from basedatum import BaseDatum

logger = logging.getLogger(__name__)

class HercOCTDatum(BaseDatum):

    # parameters that we'll need to actually find all of the files
    # in this "series" of data. Note these need to be marked as 
    # ClassVar[str] so that pydantic doesn't interpret them as model 
    # attributes. If so, it'll try and validate them, and raise
    # lots of ValidationErrors.

    glob : ClassVar[str] = 'raw/nav/navest/*.DAT'
    prefix : ClassVar[str] = 'OCT'
    encoding : ClassVar[str] = 'latin-1'

    # Now, we have all of the Pydantic model attributes.

    raw_ts : dt
    heading : float
    pitch : float
    roll : float

    @classmethod
    def parse_line(cls, line, filename=''):
        sline = list(s for s in line.split(' ') if s)
        parsed = {}

        try:
            parsed['raw_ts'] = sline[1].replace('/', '-') + 'T' + sline[2]
            parsed['heading'] = sline[7]
            parsed['pitch'] = sline[8]
            parsed['roll'] = sline[9]
        except IndexError as e:
            raise ValueError(e)

        return parsed

if __name__ == '__main__':
    for datum in HercOCTDatum.iter_data('/mnt/nautilusfs/data/NA171'):
        print(datum)

