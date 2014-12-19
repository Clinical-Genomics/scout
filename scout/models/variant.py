# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals

from mongoengine import (
  Document, EmbeddedDocument, EmbeddedDocumentField, FloatField,
  IntField, ListField, MapField, StringField
)

from .event import Event


######## Common are attributes that is specific for the variant on this certain position ########

CONSERVATION = (
  'NotConserved', 
  'Conserved'
)
CONSEQUENCE = (
  'deleterious',
  'probably_damaging',
  'possibly_damaging',
  'tolerated',
  'benign',
  'unknown'
)

SO_TERMS = (
  'transcript_ablation',
  'splice_donor_variant',
  'splice_acceptor_variant',
  'stop_gained',
  'frameshift_variant',
  'stop_lost',
  'initiator_codon_variant',
  'transcript_amplification',
  'inframe_insertion',
  'inframe_deletion',
  'missense_variant',
  'splice_region_variant',
  'incomplete_terminal_codon_variant',
  'stop_retained_variant',
  'synonymous_variant',
  'coding_sequence_variant',
  'mature_miRNA_variant',
  '5_prime_UTR_variant',
  '3_prime_UTR_variant',
  'non_coding_exon_variant',
  'non_coding_transcript_exon_variant',
  'non_coding_transcript_variant',
  'nc_transcript_variant',
  'intron_variant',
  'NMD_transcript_variant',
  'non_coding_transcript_variant',
  'upstream_gene_variant',
  'downstream_gene_variant',
  'TFBS_ablation',
  'TFBS_amplification',
  'TF_binding_site_variant',
  'regulatory_region_ablation',
  'regulatory_region_amplification',
  'regulatory_region_variant',
  'feature_elongation',
  'feature_truncation',
  'intergenic_variant'
)

FEATURE_TYPES = (
  'exonic', 
  'splicing', 
  'ncRNA_exonic', 
  'intronic', 
  'ncRNA', 
  'upstream', 
  '5UTR',
  '3UTR',
  'downstream',
  'TFBS',
  'regulatory_region',
  'genomic_feature',
  'intergenic_variant'
)

class Transcript(EmbeddedDocument):
  transcript_id = StringField(required=True)
  sift_prediction = StringField(choices=CONSEQUENCE)
  polyphen_prediction = StringField(choices=CONSEQUENCE)
  functional_annotation = StringField(choices=SO_TERMS)
  region_annotation = StringField(choices=FEATURE_TYPES)
  exon = StringField()
  intron = StringField()
  coding_sequence_name = StringField()
  protein_sequence_name = StringField()

class Gene(EmbeddedDocument):
  hgnc_symbol = StringField(required=True)
  transcripts = ListField(EmbeddedDocumentField(Transcript))
  functional_annotation = StringField(choices=SO_TERMS)
  region_annotation = StringField(choices=FEATURE_TYPES)
  sift_prediction = StringField(choices=CONSEQUENCE)
  polyphen_prediction = StringField(choices=CONSEQUENCE)

class VariantCommon(EmbeddedDocument):
  genes = MapField(EmbeddedDocumentField(Gene))
  # Gene ids:
  hgnc_symbols = ListField(StringField())
  ensemble_gene_ids = ListField(StringField())
  # Frequencies:
  thousand_genomes_frequency = FloatField()
  exac_frequency = FloatField()
  # Predicted deleteriousness:
  cadd_score = FloatField()
  phast_conservation = ListField(StringField(choices=CONSERVATION))
  gerp_conservation = ListField(StringField(choices=CONSERVATION))
  phylop_conservation = ListField(StringField(choices=CONSERVATION))
  
  @property
  def region_annotations(self):
    """Returns a list with region annotation(s)."""
    region_annotations = []
    if len(self.genes) == 1:
      return [self.genes[gene].region_annotation for gene in genes]
    else:
      for gene in self.genes:
        region_annotations.append(':'.join([gene, self.genes[gene].region_annotation]))
    return region_annotations
  
  @property
  def hgnc_symbols(self):
    """Returns a list with the hgnc id:s for this variant."""
    return [gene for gene in self.genes]
  
  @property
  def sift_predictions(self):
    """Return a list with the sift prediction(s) for this variant. The most severe for each gene."""
    sift_predictions = []
    if len(self.genes) == 1:
      sift_predictions = [self.genes[gene].sift_prediction for gene in self.genes]
    else:
      for gene in self.genes:
        sift_predictions.append(':'.join([gene, self.genes[gene].sift_prediction]))
    return sift_predictions
  
  @property
  def polyphen_predictions(self):
    """Return a list with the polyphen prediction(s) for this variant. The most severe for each gene."""
    polyphen_predictions = []
    if len(self.genes) == 1:
      polyphen_predictions = [self.genes[gene].polyphen_prediction for gene in self.genes]
    else:
      for gene in self.genes:
        polyphen_predictions.append(':'.join([gene, self.genes[gene].polyphen_prediction]))
    return polyphen_predictions

  @property
  def functional_annotations(self):
    """Return a list with the functional annotation(s) for this variant. The most severe for each gene."""
    functional_annotations = []
    if len(self.genes) == 1:
      functional_annotations = [self.genes[gene].functional_annotation for gene in self.genes]
    else:
      for gene in self.genes:
        functional_annotation.append(':'.join([gene, self.genes[gene].functional_annotation]))
    return functional_annotation
  
  # def __unicode__(self):
  #   return "%s:%s" % (self.chromosome, self.position)

######## Common are attributes that is specific for the variant on this certain position ########


GENETIC_MODELS = (('AR_hom', 'Autosomal Recessive Homozygote'),
                  ('AR_hom_dn', 'Autosomal Recessive Homozygote De Novo'),
                  ('AR_comp', 'Autosomal Recessive Compound'),
                  ('AR_comp_dn', 'Autosomal Recessive Compound De Novo'),
                  ('AD', 'Autosomal Dominant'),
                  ('AD_dn', 'Autosomal Dominant De Novo'),
                  ('XR', 'X Linked Recessive'),
                  ('XR_dn', 'X Linked Recessive De Novo'),
                  ('XD', 'X Linked Dominant'),
                  ('XD_dn', 'X Linked Dominant De Novo'),
)

class Compound(EmbeddedDocument):
  variant_id = StringField(required=True)
  display_name = StringField(required=True)
  rank_score = FloatField(required=True)
  combined_score = FloatField(required=True)
  region_annotations = ListField(StringField())
  functional_annotations = ListField(StringField())

class GTCall(EmbeddedDocument):
  sample = StringField()
  genotype_call = StringField()
  allele_depths = ListField(IntField())
  read_depth = IntField()
  genotype_quality = IntField()

  def __unicode__(self):
    return self.sample

class VariantCaseSpecific(EmbeddedDocument):
  rank_score = FloatField()
  variant_rank = IntField()
  quality = FloatField()
  filters = ListField(StringField())
  samples = ListField(EmbeddedDocumentField(GTCall))
  genetic_models = ListField(StringField(choices=GENETIC_MODELS))
  compounds = ListField(EmbeddedDocumentField(Compound))
  events = ListField(EmbeddedDocumentField(Event))

  def __unicode__(self):
    return 'placeholder'


class Variant(Document):
  variant_id = StringField(primary_key=True)
  display_name = StringField(required=True)
  chromosome = StringField(required=True)
  position = IntField(required=True)
  reference = StringField(required=True)
  alternative = StringField(required=True)
  db_snp_ids = ListField(StringField())
  common = EmbeddedDocumentField(VariantCommon)
  specific = MapField(EmbeddedDocumentField(VariantCaseSpecific))
  meta = {
    'indexes': [
      'position',
      'common.thousand_genomes_frequency',
      'common.exac_frequency',
      'common.cadd_score',
      'specific.rank_score',
      'specific.variant_rank',
    ]
  }

  @property
  def end_position(self):
    # which alternative allele contains most bases
    alt_bases = max([len(alt) for alt in self.alternatives])
    # vs. reference allele
    bases = max(len(self.reference), alt_bases)

    return self.position + (bases - 1)

  def __unicode__(self):
    return self.display_name
