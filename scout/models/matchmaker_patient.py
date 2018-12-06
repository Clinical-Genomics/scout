# -*- coding: utf-8 -*-
"""
This class builds a MatchMaker patient object as close as possible to the
model described in MatchMaker Exchange APIs: https://www.ncbi.nlm.nih.gov/pubmed/26255989
"""
class MatchMaker_patient(dict):
    """ MatchMaker_patient dictionary

        id = str,case_obj['_id'] + '_' + sample id of the affected individual
        label = str, # case_obj['display_name'] + '_' + display name of the affected individual
        contact = dict, # {name, institution, href(email)}
        sex = str
        features = list of objects, {id (hpo), label(hpo label), observed(['yes','no'])}
        genomicFeatures = list of objects, (variants or genes)
        disorders = list of objects, {id(omim) }

    """
    def __init__(self, id, label, contact, sex, features, genomic_features, disorders):

        super(MatchMaker_patient, self).__init__()
        self['id'] = id
        self['label'] = label
        self['contact'] = contact
        self['sex'] = sex or ''
        self['features'] = features or []
        self['genomicFeatures'] = genomic_features or []
        self['disorders'] = disorders or []
