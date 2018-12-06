# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import json
LOG = logging.getLogger(__name__)

def mme_patients(json_patients_file):
    """Reads a json file containing MME patients
    and returns a list of patient dictionaries

        Args:
            json_patients_file(str) : string path to json patients file

        Returns:
            mme_patients(list) : a list of MME patient objects
    """
    with open(json_patients_file) as json_data:
        patients = json.load(json_data)
        return patients
