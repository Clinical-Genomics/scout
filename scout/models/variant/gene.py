from __future__ import absolute_import, division
from mongoengine import (EmbeddedDocument, EmbeddedDocumentField, StringField,
                         ListField, IntField)

from .transcript import Transcript
from scout.constants import (CONSEQUENCE, FEATURE_TYPES, SO_TERM_KEYS)

gene = dict(
    # The hgnc gene id
    hgnc_id = int, # required
    # A list of Transcript objects
    transcripts = list, # list of <transcript>
    # This is the worst functional impact of all transcripts
    functional_annotation = str, # choices=SO_TERM_KEYS
    # This is the region of the most severe functional impact
    region_annotation = str, # choices=FEATURE_TYPES
    # This is most severe sift prediction of all transcripts
    sift_prediction = str, # choices=CONSEQUENCE
    # This is most severe polyphen prediction of all transcripts
    polyphen_prediction = str, # choices=CONSEQUENCE
)

class Gene(EmbeddedDocument):

    meta = {'strict': False}

    # The hgnc gene id
    hgnc_id = IntField(required=True)
    # A list of Transcript objects
    transcripts = ListField(EmbeddedDocumentField(Transcript))
    # This is the worst functional impact of all transcripts
    functional_annotation = StringField(choices=SO_TERM_KEYS)
    # This is the region of the most severe functional impact
    region_annotation = StringField(choices=FEATURE_TYPES)
    # This is most severe sift prediction of all transcripts
    sift_prediction = StringField(choices=CONSEQUENCE)
    # This is most severe polyphen prediction of all transcripts
    polyphen_prediction = StringField(choices=CONSEQUENCE)

    # will be filled in dynamically
    # disease_terms

    @property
    def genecards_link(self):
        return ("http://www.genecards.org/cgi-bin/carddisp.pl?gene={}"
                .format(self.hgnc_id))
