# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import (absolute_import, unicode_literals, division)
from itertools import chain

from mongoengine import (Document, EmbeddedDocument, EmbeddedDocumentField,
                         FloatField, IntField, ListField, StringField,
                         ReferenceField)

from .._compat import zip
from .event import Event
from .case import Case

######## These are defined terms for different categories ########


CONSERVATION = ('NotConserved', 'Conserved')

CONSEQUENCE = ('deleterious', 'probably_damaging', 'possibly_damaging',
               'tolerated', 'benign', 'unknown')

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

GENETIC_MODELS = (
  ('AR_hom', 'Autosomal Recessive Homozygote'),
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

ACMG_TERMS = (
  'pathegenic',
  'likely pathegenic',
  'uncertain significance',
  'likely benign',
  'benign'
)

class Transcript(EmbeddedDocument):
  transcript_id = StringField(required=True)
  refseq_ids = ListField(StringField())
  hgnc_symbol = StringField()

  # Protein specific predictions
  protein_id = StringField()
  sift_prediction = StringField(choices=CONSEQUENCE)
  polyphen_prediction = StringField(choices=CONSEQUENCE)
  swiss_prot = StringField()
  pfam_domain = StringField()
  prosite_profile = StringField()
  smart_domain = StringField()

  biotype = StringField()
  functional_annotations = ListField(StringField(choices=SO_TERMS))
  region_annotations = ListField(StringField(choices=FEATURE_TYPES))
  exon = StringField()
  intron = StringField()
  strand = StringField()
  coding_sequence_name = StringField()
  protein_sequence_name = StringField()

  @property
  def swiss_prot_link(self):
    return "http://www.uniprot.org/uniprot/{}".format(self.swiss_prot)

  @property
  def pfam_domain_link(self):
    return "http://pfam.xfam.org/family/{}".format(self.pfam_domain)

  @property
  def prosite_profile_link(self):
    return ("http://prosite.expasy.org/cgi-bin/prosite/prosite-search-ac?{}"
            .format(self.prosite_profile))

  @property
  def smart_domain_link(self):
    return ("http://smart.embl.de/smart/search.cgi?keywords={}"
            .format(self.smart_domain))

  @property
  def refseq_links(self):
    for refseq_id in self.refseq_ids:
      yield (refseq_id,
             "http://www.ncbi.nlm.nih.gov/nuccore/{}".format(refseq_id))

  @property
  def ensembl_link(self):
    return "http://www.ensembl.org/id/{}".format(self.transcript_id)

  @property
  def ensembl_protein_link(self):
    return "http://www.ensembl.org/id/{}".format(self.transcript_id)


class OmimPhenotype(EmbeddedDocument):
  omim_id = IntField(required=True)
  disease_models = ListField(StringField())

  @property
  def omim_link(self):
    """Return a OMIM phenotype link."""
    return "http://www.omim.org/entry/{}".format(self.omim_id)


class Gene(EmbeddedDocument):
  hgnc_symbol = StringField(required=True)
  ensembl_gene_id = StringField()
  transcripts = ListField(EmbeddedDocumentField(Transcript))
  functional_annotation = StringField(choices=SO_TERMS)
  region_annotation = StringField(choices=FEATURE_TYPES)
  sift_prediction = StringField(choices=CONSEQUENCE)
  polyphen_prediction = StringField(choices=CONSEQUENCE)
  omim_gene_entry = IntField()
  omim_phenotypes = ListField(EmbeddedDocumentField(OmimPhenotype))
  description = StringField()

  @property
  def reactome_link(self):
    url_template = ("http://www.reactome.org/content/query?q={}&"
                    "species=Homo+sapiens&species=Entries+without+species&"
                    "cluster=true")

    return url_template.format(self.ensembl_gene_id)

  @property
  def ensembl_link(self):
    return ("http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?""g={}"
            .format(self.ensembl_gene_id))

  @property
  def hpa_link(self):
    return ("http://www.proteinatlas.org/search/{}"
            .format(self.ensembl_gene_id))

  @property
  def string_link(self):
    return ("http://string-db.org/newstring_cgi/show_network_section."
            "pl?identifier={}".format(self.ensembl_gene_id))

  @property
  def entrez_link(self):
    return ("http://www.ncbi.nlm.nih.gov/sites/gquery/?term={}"
            .format(self.hgnc_symbol))


class Compound(EmbeddedDocument):
  # This must be the document_id for this variant
  variant = ReferenceField('Variant')
  # This is the variant id
  display_name = StringField(required=True)
  combined_score = FloatField(required=True)

  @property
  def rank_score(self):
    """Return the individual rank score for this variant."""
    return self.variant.rank_score


class GTCall(EmbeddedDocument):
  sample = StringField()
  genotype_call = StringField()
  allele_depths = ListField(IntField())
  read_depth = IntField()
  genotype_quality = IntField()

  def __unicode__(self):
    return self.sample


class Variant(Document):
  # document_id is a md5 string created by institute_genelist_caseid_variantid:
  document_id = StringField(primary_key=True)
  # variant_id is a md5 string created by variant_id
  variant_id = StringField(required=True)
  # display name in variant_id (no md5)
  display_name = StringField(required=True)
  # the variant can be either a reserchvariant or a clinical variant.
  # for research variants we display all the available information while
  # the clinical variants hae limited annotation fields.
  variant_type = StringField(required=True,
                             choices=('research', 'clinical'))
  # case_id is a string like institute_caseid
  case_id = StringField(required=True)
  chromosome = StringField(required=True)
  position = IntField(required=True)
  reference = StringField(required=True)
  alternative = StringField(required=True)
  rank_score = FloatField(required=True)
  variant_rank = IntField(required=True)
  quality = FloatField()
  filters = ListField(StringField())
  samples = ListField(EmbeddedDocumentField(GTCall))
  genetic_models = ListField(StringField(choices=GENETIC_MODELS))
  compounds = ListField(EmbeddedDocumentField(Compound))
  events = ListField(EmbeddedDocumentField(Event))
  comments = ListField(EmbeddedDocumentField(Event))
  genes = ListField(EmbeddedDocumentField(Gene))
  db_snp_ids = ListField(StringField())
  # Gene ids:
  hgnc_symbols = ListField(StringField())
  ensembl_gene_ids = ListField(StringField())
  # Frequencies:
  thousand_genomes_frequency = FloatField()
  exac_frequency = FloatField()
  local_frequency = FloatField()
  # Predicted deleteriousness:
  cadd_score = FloatField()
  # Conservation:
  phast_conservation = ListField(StringField(choices=CONSERVATION))
  gerp_conservation = ListField(StringField(choices=CONSERVATION))
  phylop_conservation = ListField(StringField(choices=CONSERVATION))
  # Database options:
  gene_lists = ListField(StringField())
  expected_inheritance = ListField(StringField())
  manual_rank = IntField(choices=[1, 2, 3, 4, 5])

  acmg_evaluation = StringField(choices=ACMG_TERMS)

  @property
  def local_requency(self):
    """Returns a float with the local freauency for this position."""
    return (Variant.objects(variant_id=self.variant_id).count /
              Case.objects.count())

  @property
  def expected_inheritance_genes(self):
    """Returns a list with expected inheritance model(s)."""
    expected_inheritance = set([])
    for gene in self.genes:
      for omim_phenotype in gene.omim_phenotypes:
        for gene_model in omim_phenotype.disease_models:
          expected_inheritance.add(gene_model)

    return list(expected_inheritance)

  @property
  def omim_annotations(self):
    """Returns a list with omim id(s)."""
    if len(self.genes) == 1:
      annotations = (str(gene.omim_gene_entry) for gene in self.genes
                     if gene.omim_gene_entry)
    else:
      annotations = (':'.join([gene.hgnc_symbol, str(gene.omim_gene_entry)])
                     for gene in self.genes if gene.omim_gene_entry)

    # flatten the list of list of omim ids
    return annotations

  @property
  def omim_annotation_links(self):
    """Return a list of omim id links."""
    base_url = 'http://www.omim.org/entry'
    return ((omim_id, "{base}/{id}".format(base=base_url, id=omim_id))
            for omim_id in self.omim_annotations)

  @property
  def omim_phenotypes(self):
    """Return a list of OMIM phenotypes with related gene information."""
    for gene in self.genes:
      for phenotype in gene.omim_phenotypes:
        yield gene, phenotype

  @property
  def omim_inheritance_models(self):
    """Return a list of OMIM inheritance models (phenotype based)."""
    models = ((phenotype.disease_models for phenotype in gene.omim_phenotypes)
              for gene in self.genes)

    # untangle multiple nested list of list of lists...
    return set(chain.from_iterable(chain.from_iterable(models)))

  @property
  def region_annotations(self):
    """Returns a list with region annotation(s)."""
    region_annotations = []
    if len(self.genes) == 1:
      return [gene.region_annotation for gene in self.genes]
    else:
      for gene in self.genes:
        region_annotations.append(':'.join([gene.hgnc_symbol, gene.region_annotation]))
    return region_annotations

  @property
  def sift_predictions(self):
    """Return a list with the sift prediction(s) for this variant.

    The most severe for each gene.
    """
    sift_predictions = []
    if len(self.genes) == 1:
      sift_predictions = [gene.sift_prediction for gene in self.genes]
    else:
      for gene in self.genes:
        sift_predictions.append(':'.join([gene.hgnc_symbol, gene.sift_prediction or '-']))
    return sift_predictions

  @property
  def polyphen_predictions(self):
    """Return a list with the polyphen prediction(s) for this variant.

    The most severe for each gene.
    """
    polyphen_predictions = []
    if len(self.genes) == 1:
      polyphen_predictions = [gene.polyphen_prediction for gene in self.genes]
    else:
      for gene in self.genes:
        polyphen_predictions.append(':'.join([gene.hgnc_symbol, gene.polyphen_prediction or '-']))
    return polyphen_predictions

  @property
  def is_matching_inheritance(self):
    """Match expected (OMIM) with annotated inheritance models."""
    omim_models = self.omim_inheritance_models

    for model in self.genetic_models:
      for omim_model in omim_models:
        if (model == omim_model) or (omim_model in model):
          return True

    return False

  @property
  def functional_annotations(self):
    """Return a list with the functional annotation(s) for this variant. The most severe for each gene."""
    functional_annotations = []
    if len(self.genes) == 1:
      functional_annotations = [gene.functional_annotation for gene in self.genes]
    else:
      for gene in self.genes:
        functional_annotations.append(':'.join([gene.hgnc_symbol, gene.functional_annotation or '']))
    return functional_annotations

  @property
  def transcripts(self):
    """Yield all transcripts as a flat iterator.

    For each transcript both the parent gene object as well as the
    transcript is yielded.

    Yields:
      class, class: Gene and Transcript ODM
    """
    # loop over each gene in order
    for gene in self.genes:
      # loop over each child transcript for the gene
      for transcript in gene.transcripts:
        # yield the parent gene, child transcript combo
        yield transcript

  @property
  def refseq_transcripts(self):
    """Yield all transcripts with a RefSeq id."""
    for transcript in self.transcripts:
      if transcript.refseq_ids:
        yield transcript

  @property
  def end_position(self):
    # bases contained in alternative allele
    alt_bases = len(self.alternative)
    # vs. reference allele
    bases = max(len(self.reference), alt_bases)

    return self.position + (bases - 1)

  @property
  def id_string(self):
    """Compose standard ID string for a variant."""
    return ("{this.chromosome}:{this.position} "
            "{this.reference}/{this.alternative}".format(this=self))

  @property
  def frequency(self):
    """Returns a judgement on the overall frequency of the variant.

    Combines multiple metrics into a single call.
    """
    most_common_frequency = max(self.thousand_genomes_frequency,
                                self.exac_frequency)

    if most_common_frequency > .05:
      return 'common'

    elif most_common_frequency > .01:
      return 'uncommon'

    else:
      return 'rare'

  @property
  def manual_rank_level(self):
    return {1: 'low', 2: 'low',
            3: 'medium', 4: 'medium',
            5: 'high'}.get(self.manual_rank, 'unknown')

  @property
  def exac_link(self):
    """Compose link to ExAC website for a variant position."""
    url_template = ("http://exac.broadinstitute.org/variant/"
                    "{this.chromosome}-{this.position}-{this.reference}"
                    "-{this.alternative}")

    return url_template.format(this=self)

  @property
  def ucsc_link(self):
    url_template = ("http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&"
                    "position=chr{this.chromosome}:{this.position}-{this.position}&dgv=pack&knownGene=pack&omimGene=pack")

    return url_template.format(this=self)


  def __unicode__(self):
    return self.display_name
