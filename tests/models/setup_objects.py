# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scout.models import *
from scout.ext.backend.utils import generate_md5_key


def setup_institute(**kwargs):
  """
  Setup a Institute object
  """
  institute = Institute(
    internal_id = kwargs.get('internal_id', 'internal_institute'),
    display_name = kwargs.get('display_name', 'institute0'),
    sanger_recipients = kwargs.get('sanger_recipients', ['john@doe.com']),
  )
  return institute


def setup_user(**kwargs):
  """
  Setup a User object
  """
  user = User(
    email = kwargs.get('email', 'john@doe.com'),
    name = kwargs.get('name', 'John Doe'),
    location = kwargs.get('location', 'se'),
    institutes = kwargs.get('institutes', [setup_institute()]),
    roles = kwargs.get('roles', ['admin']),
  )
  return user

def setup_gene_list(**kwargs):
  """
  Setup an Phenotype term object
  """
  list_id = kwargs.get('list_id', "gene_list")
  version = kwargs.get('version', 1.0)
  date = kwargs.get('date', "20150522")
  display_name = kwargs.get('display_name', "gene_list")
  
  gene_list = GeneList(
    list_id=list_id,
    version=version,
    date=date,
    display_name=display_name
  )
  return gene_list

def setup_phenotype_term(**kwargs):
  """
  Setup an Phenotype term object
  """
  
  term = PhenotypeTerm(
    phenotype_id=kwargs.get('hpo_id', "1234"), 
    feature=kwargs.get('feature', "NOC1"),
    disease_models=kwargs.get('disease_models', ["AD"])
  )
  return term

def setup_compound(**kwargs):
  """
  Setup an Compound object object
  """
  compound = Compound(
    variant = kwargs.get('variant', setup_variant()),
    display_name = kwargs.get('display_name', '1_132_A_C'),
    combined_score = kwargs.get('combined_score', '13'),
  )

  return compound


def setup_case(**kwargs):
  """
  Setup a Case object
  """
  case = Case(
    case_id = kwargs.get('case_id', "Institute0_1"),
    display_name = kwargs.get('display_name', "1"),
    owner = kwargs.get('owner', "Institute0"),
    collaborators = kwargs.get('collaborators', ['Institute1']),
    assignee = kwargs.get('assignee', setup_user()),
    individuals = kwargs.get('individuals', [setup_individual()]),
    suspects = kwargs.get('suspects', [setup_variant()]),
    causative = kwargs.get('causative', setup_variant()),
    synopsis=kwargs.get('synopsis', "This is a synopsis"),
    status=kwargs.get('status', "inactive"),
    is_research=kwargs.get('is_research', False),
    default_gene_lists = kwargs.get('default_gene_lists', ['List_1']),
    clinical_gene_lists = kwargs.get('clinical_gene_lists', [setup_gene_list()]),
    research_gene_lists = kwargs.get('research_gene_lists', [setup_gene_list()]),
    genome_build = kwargs.get('genome_build', "GRCh"),
    genome_version = kwargs.get('genome_version', 38),
    gender_check = kwargs.get('gender_check', 'confirm'),
    phenotype_terms = kwargs.get('phenotype_terms', [setup_phenotype_term()]),
    madeline_info = kwargs.get('madeline_info', "XML text"),
    vcf_file = kwargs.get('vcf_file', "path/to/variants.vcf"),
    coverage_report = kwargs.get('coverage_report', b"coverage info")
  )
  
  return case

def setup_individual(**kwargs):
  """
  Setup an Individual object with the given parameters
  """
  individual = Individual(
    individual_id = kwargs.get('individual_id', "A"),
    display_name = kwargs.get('display_name', "A"),
    sex = kwargs.get('sex', "1"),
    phenotype = kwargs.get('display_name', 1),
    father = kwargs.get('father', "C"),
    mother = kwargs.get('mother', "B"),
    capture_kits = kwargs.get('capture_kits', ['Nimblegen']),
    bam_file = kwargs.get('bam_file', 'path/to/bam')
  )
  
  return individual

def setup_gt_call(**kwargs):
  """
  Setup an GTCall object object
  """
  gt_call = GTCall(
    sample_id = kwargs.get('sample_id', '1'),
    display_name = kwargs.get('display_name', '1'),
    genotype_call = kwargs.get('genotype_call', '0/1'),
    allele_depths = kwargs.get('allele_depths', [10,12]),
    read_depth = kwargs.get('read_depth', 22),
    genotype_quality = kwargs.get('genotype_quality', 55),
  )

  return gt_call


def setup_variant(**kwargs):
  """
  Setup a Variant object
  """
  variant_id = kwargs.get('variant_id', '1_132_A_C')
  
  variant = Variant(
    document_id = kwargs.get('document_id', 'institute_genelist_caseid_variantid'),
    variant_id = generate_md5_key(variant_id.split('_')),
    display_name = variant_id,
    variant_type = kwargs.get('document_id', 'clinical'),
    case_id = kwargs.get('case_id', 'institute1_1'),
    chromosome = kwargs.get('chromosome', '1'),
    position = kwargs.get('position', 132),
    reference = kwargs.get('reference', 'A'),
    alternative = kwargs.get('alternative', 'C'),
    rank_score = kwargs.get('rank_score', 19),
    variant_rank = kwargs.get('variant_rank', 1),
    quality = kwargs.get('quality', 88),
    filters = kwargs.get('filters', ['PASS']),
    samples = kwargs.get('samples', []),
    genetic_models = kwargs.get('genetic_models', ['AD', 'AD_dn']),
    compounds = kwargs.get('compounds', []),
    genes = kwargs.get('genes', []),
    db_snp_ids = kwargs.get('db_snp_ids', ['rs0001']),
    # Gene ids:
    hgnc_symbols = kwargs.get('hgnc_symbols', ['ADK']),
    ensembl_gene_ids = kwargs.get('ensembl_gene_ids', ['ENSG00000156110']),
    # Frequencies:
    thousand_genomes_frequency = kwargs.get('thousand_genomes_frequency', 0.001),
    exac_frequency = kwargs.get('thousand_genomes_frequency', 0.002),
    local_frequency = kwargs.get('local_frequency', None),
    # Predicted deleteriousness:
    cadd_score = kwargs.get('cadd_score', 22),
    clnsig = kwargs.get('clnsig', 1),
    phast_conservation = kwargs.get('phast_conservation', []),
    gerp_conservation = kwargs.get('gerp_conservation', []),
    phylop_conservation = kwargs.get('phylop_conservation', []),
    # Database options:
    gene_lists = kwargs.get('gene_lists', ['gene_list_1', 'gene_list_2']),
    expected_inheritance = kwargs.get('expected_inheritance', ['AR']),
    manual_rank = kwargs.get('manual_rank', 5),
    acmg_evaluation = kwargs.get('acmg_evaluation', None)
  )

  return variant

def setup_gene(**kwargs):
  """
  Setup an Gene object
  """

  gene = Gene(
    hgnc_symbol = kwargs.get('hgnc_symbol', 'NOCL1'),
    ensembl_gene_id = kwargs.get('ensembl_gene_id', 'ENSG001'),
    transcripts = kwargs.get('transcripts', [setup_transcript()]),
    functional_annotation = kwargs.get('functional_annotation', 'transcript_ablation'),
    region_annotation = kwargs.get('region_annotation', 'exonic'),
    sift_prediction = kwargs.get('sift_prediction', 'deleterious'),
    polyphen_prediction = kwargs.get('polyphen_prediction', 'deleterious'),
    omim_gene_entry = kwargs.get('omim_gene_entry', 1234),
    omim_phenotypes = kwargs.get('omim_phenotypes', [setup_phenotype_term()]),
    description = kwargs.get('description', "Description of gene")
  )
  
  return gene

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


def setup_event(**kwargs):
  """
  Setup an Event object object
  """
  event = Event(
    institute = kwargs.get('institute', setup_institute()),
    case = kwargs.get('case', setup_case()),
    link = kwargs.get('link', "an/url"),
    category = kwargs.get('category', "variant"),
    author = kwargs.get('author', setup_user()),
    subject = kwargs.get('subject', "1_2343_A_C"),
    verb = kwargs.get('verb', "pin"),
    level = kwargs.get('level', "specific"),
    variant_id = kwargs.get('variant_id', "1_2343_A_C"),
    content = kwargs.get('content', "This is a comment"),
  )

  return event


