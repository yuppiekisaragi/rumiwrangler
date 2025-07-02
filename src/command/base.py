import os
import sys
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)

class BaseCommand():
    def __init__(self, 
            args, 
            cruisepath, 
            dive, 
            start_ts=None,
            end_ts=None):

        self.args = args
        self.cruisepath = cruisepath
        self.dive = dive
        self.start_ts = start_ts
        self.end_ts = end_ts

    def execute(self):
        try:
            self.target()
        except AttributeError:
            subclass = self.__class__.__name__
            err = f'BaseCommand subclass {subclass} has no target()'
            raise NotImplementedError(err)
