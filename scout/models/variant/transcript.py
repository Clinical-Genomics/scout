# -*- coding: utf-8 -*-
"""
"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""

transcript = dict(
    # The ensemble transcript id
    transcript_id=str,  # required=True
    # The hgnc gene id
    hgnc_id=int,
    ### Protein specific predictions ###
    # The ensemble protein id
    protein_id=str,
    # The sift consequence prediction for this transcript
    sift_prediction=str,  # choices=CONSEQUENCE
    # The polyphen consequence prediction for this transcript
    polyphen_prediction=str,  # choices=CONSEQUENCE
    # The swiss protein id for the product
    swiss_prot=str,
    # The pfam id for the protein product
    pfam_domain=str,
    # The prosite id for the product
    prosite_profile=str,
    # The smart id for the product
    smart_domain=str,
    # The biotype annotation for the transcript
    biotype=str,
    # The functional annotations for the transcript
    functional_annotations=list,  #  list(str(choices=SO_TERM_KEYS))
    # The region annotations for the transcripts
    region_annotations=list,  # list(str(choices=FEATURE_TYPES))
    # The exon number in the transcript e.g '2/7'
    exon=str,
    # The intron number in the transcript e.g '4/6'
    intron=str,
    # The strand of the transcript e.g '+'
    strand=str,
    # the CDNA change of the transcript e.g 'c.95T>C'
    coding_sequence_name=str,
    # The amino acid change on the transcript e.g. 'p.Phe32Ser'
    protein_sequence_name=str,
    # If the transcript is relevant
    is_canonical=bool,
    # The MANE select transcript
    mane_transcript=str,
)
