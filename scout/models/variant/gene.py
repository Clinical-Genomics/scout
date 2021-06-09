from __future__ import absolute_import, division

from scout.constants import CONSEQUENCE, FEATURE_TYPES, SO_TERM_KEYS

from .transcript import Transcript

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
    # The SpliceAI predictions for the transcript with the most severe consequence
    spliceai_score=float,  # highest delta score
    spliceai_position=int,  # position relative to the variant for prediction with highest delta score
    spliceai_prediction=list,  # list of str, with more detailed spliceai info
)
