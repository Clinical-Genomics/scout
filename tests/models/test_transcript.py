# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import Transcript


def setup_transcript(**kwargs):
  """
  Setup an Transcript object
  """
  transcript = Transcript(
    transcript_id = kwargs.get('transcript_id', 'ENST001'),
    refseq_ids = kwargs.get('refseq_ids', 'NM_001'),
    hgnc_symbol = kwargs.get('hgnc_symbol', 'NOCL1'),
    protein_id = kwargs.get('protein_id', 'ENSP001'),
    sift_prediction = kwargs.get('sift_prediction', 'deleterious'),
    polyphen_prediction = kwargs.get('polyphen_prediction', 'deleterious'),
    swiss_prot = kwargs.get('swiss_prot', 'LRP2_HUMAN'),
    pfam_domain = kwargs.get('pfam_domain', 'PF00648'),
    prosite_profile = kwargs.get('pfam_domain', 'PS50203'),
    smart_domain = kwargs.get('pfam_domain', 'SM00230'),
    biotype = kwargs.get('biotype', 'protein_coding'),
    functional_annotations = kwargs.get('functional_annotations', ['transcript_ablation']),
    region_annotations = kwargs.get('region_annotations', ['exonic']),
    exon = kwargs.get('exon', '2/7'),
    intron = kwargs.get('intron', ''),
    strand = kwargs.get('strand', '+'),
    coding_sequence_name = kwargs.get('coding_sequence_name', 'c.95T>C'),
    protein_sequence_name = kwargs.get('protein_sequence_name', 'p.Phe32Ser')
  )

  return transcript
  
def test_transcript():
  """
  Test the Transcript class
  """
  transcript = setup_transcript()
  
  assert transcript.transcript_id == 'ENST001'
  assert transcript.refseq_ids == 'NM_001'
  assert transcript.hgnc_symbol == 'NOCL1'
  assert transcript.protein_id == 'ENSP001'
  assert transcript.sift_prediction == 'deleterious'
  assert transcript.polyphen_prediction == 'deleterious'
  assert transcript.swiss_prot == 'LRP2_HUMAN'
  assert transcript.pfam_domain == 'PF00648'
  assert transcript.prosite_profile == 'PS50203'
  assert transcript.smart_domain == 'SM00230'
  assert transcript.biotype == 'protein_coding'
  assert transcript.functional_annotations == ['transcript_ablation']
  assert transcript.region_annotations == ['exonic']
  assert transcript.exon == '2/7'
  assert transcript.intron == ''
  assert transcript.strand == '+'
  assert transcript.coding_sequence_name == 'c.95T>C'
  assert transcript.protein_sequence_name == 'p.Phe32Ser'
  assert transcript.transcript_id == 'ENST001'
  assert transcript.refseq_ids == 'NM_001'
  
  
  
  
  
  
