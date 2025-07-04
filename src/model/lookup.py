import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from model.herc_oct import HercOCTDatum, HercOCTORM
from model.herc_paro import HercParoDatum, HercParoORM
from model.herc_usbl import HercUSBLDatum, HercUSBLORM
from model.herc_vfr import HercVFRDatum, HercVFRORM

model_classes = {
        HercOCTDatum.modelname:HercOCTDatum,
        HercParoDatum.modelname:HercParoDatum,
        HercUSBLDatum.modelname:HercUSBLDatum,
        HercVFRDatum.modelname:HercVFRDatum}

model_ormclasses = {
        HercOCTDatum.modelname:HercOCTORM,
        HercParoDatum.modelname:HercParoORM,
        HercUSBLDatum.modelname:HercUSBLORM,
        HercVFRDatum.modelname:HercVFRORM}

raw_model_names = [
        HercOCTDatum.modelname,
        HercParoDatum.modelname,
        HercUSBLDatum.modelname,
        HercVFRDatum.modelname]
