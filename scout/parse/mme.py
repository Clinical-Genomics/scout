# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import json

from scout.resources import mme_schema_path

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


#def matchbox_patient_obj(json_patient):
#    """Converts a json patient into an object to be inserted into matchbox

#        Args:
#            json_patient(dict): a patient object as in https://github.com/ga4gh/mme-apis

#        Returns:
#            matchbox_patient(dict): a matchbox patient entity (org.broadinstitute.macarthurlab.matchbox.entities.Patient)
#    """
    # fix patient's features:
#    for feature in patient_obj.get('features'):
#        feature['_id'] = feature.get('id')
#        feature.pop('id')

#    matchbox_patient = {
#        '_id' : patient_obj['id'],
#        '_class' : 'org.broadinstitute.macarthurlab.matchbox.entities.Patient',
#        'label' : patient_obj.get('label'),
#        'contact' : patient_obj['contact'],
#        'features' : patient_obj['features'],
#        'genomicFeatures' : patient_obj.get('genomicFeatures'),
#        'disorders' : patient_obj.get('disorders'),
#        'species' : patient_obj.get('species'),
#        'ageOfOnset' : patient_obj.get('ageOfOnset'),
#        'inheritanceMode' : patient_obj.get('inheritanceMode')
#    }

#    return matchbox_patient
