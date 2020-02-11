from __future__ import absolute_import, division

from .transcript import Transcript
from scout.constants import CONSEQUENCE, FEATURE_TYPES, SO_TERM_KEYS

gene = dict(
    # The hgnc gene id
    hgnc_id=int,  # required
    hgnc_symbol=str,
    # A list of Transcript objects
    transcripts=list,  # list of <transcript>
    # This is the worst functional impact of all transcripts
    functional_annotation=str,  # choices=SO_TERM_KEYS
    # This is the region of the most severe functional impact
    region_annotation=str,  # choices=FEATURE_TYPES
    # This is most severe sift prediction of all transcripts
    sift_prediction=str,  # choices=CONSEQUENCE
    # This is most severe polyphen prediction of all transcripts
    polyphen_prediction=str,  # choices=CONSEQUENCE
)
