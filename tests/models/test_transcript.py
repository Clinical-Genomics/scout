# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .setup_objects import setup_transcript


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
  
  
  
  
  
  
