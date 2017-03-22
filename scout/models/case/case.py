from __future__ import (absolute_import)

import os
import logging
from datetime import datetime

from mongoengine import (Document, StringField, ListField, ReferenceField,
                         EmbeddedDocumentField, DateTimeField, BooleanField,
                         BinaryField, FloatField, DictField, IntField)

from . import STATUS
from .individual import Individual

from scout.models import PhenotypeTerm
from scout.models.panel import GenePanel
from scout.constants import ANALYSIS_TYPES

logger = logging.getLogger(__name__)


individual = dict(
    individual_id = str, # required
    display_name = str,
    sex = str,
    phenotype = int,
    father = str, # Individual id of father
    mother = str, # Individual id of mother
    capture_kits = list, # List of names of capture kits
    bam_file = str, # Path to bam file
    analysis_type = str, # choices=ANALYSIS_TYPES
)

case = dict(
    # This is a string with the id for the family:
    case_id = str, # required=True, unique
    # This is the string that will be shown in scout:
    display_name = str, # required
    # This internal_id for the owner of the case. E.g. 'cust000'
    owner = str, # required

    # These are the names of all the collaborators that are allowed to view the
    # case, including the owner
    collaborators = list, # List of institute_ids
    assignee = str, # _id of a user
    individuals = list, # list of dictionaries with individuals
    created_at = datetime,
    updated_at = datetime,
    suspects = list, # List of variants referred by there _id
    causatives = list, # List of variants referred by there _id

    synopsis = str, # The synopsis is a text blob
    status = str, # default='inactive', choices=STATUS
    is_research = bool, # default=False
    research_requested = bool, # default=False
    rerun_requested = bool, # default=False

    analysis_date = datetime,
    analysis_dates = list, # list of datetimes

    # default_panels specifies which panels that should be shown when
    # the case is opened
    panels = list, # list of dictionaries with panel information

    dynamic_gene_list = list, # List of genes

    genome_build = str, # This should be 37 or 38
    genome_version = float, # What version of the build

    rank_model_version = float,
    rank_score_threshold = int, # default=8

    phenotype_terms = list, # List of dictionaries with phenotype information
    phenotype_groups = list, # List of dictionaries with phenotype information

    madeline_info = str, # madeline info is a full xml file

    vcf_files = dict, # A dictionary with vcf files

    diagnosis_phenotypes = list, # List of references to diseases
    diagnosis_genes = list, # List of references to genes

    has_svvariants = bool, # default=False

    is_migrated = bool # default=False

)

class Case(Document):

    """Represents a case (family) of individuals (samples)."""

    meta = {'index_background': True, 'strict': False}

    # This is a string with the id for the family:
    case_id = StringField(primary_key=True, required=True)
    # This is the string that will be shown in scout:
    display_name = StringField(required=True)
    # This is the owner of the case. E.g. 'cust003'
    owner = StringField(required=True)
    # These are the names of all the collaborators that are allowed to view the
    # case, including the owner
    collaborators = ListField(StringField())
    assignee = ReferenceField('User')
    individuals = ListField(EmbeddedDocumentField(Individual))
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    suspects = ListField(ReferenceField('Variant'))
    causatives = ListField(ReferenceField('Variant'))

    # The synopsis is a text blob
    synopsis = StringField(default='')
    status = StringField(default='inactive', choices=STATUS)
    is_research = BooleanField(default=False)
    research_requested = BooleanField(default=False)
    rerun_requested = BooleanField(default=False)

    analysis_date = DateTimeField()
    analysis_dates = ListField(DateTimeField())

    # default_panels specifies which gene lists that should be shown when
    # the case is opened
    default_panels = ListField(ReferenceField(GenePanel))
    gene_panels = ListField(ReferenceField(GenePanel))

    dynamic_gene_list = ListField(DictField())

    genome_build = StringField()
    genome_version = FloatField()

    rank_model_version = FloatField()
    rank_score_threshold = IntField(default=5)

    phenotype_terms = ListField(EmbeddedDocumentField(PhenotypeTerm))
    phenotype_groups = ListField(EmbeddedDocumentField(PhenotypeTerm))
    # madeline info is a full xml file
    madeline_info = StringField()

    vcf_files = DictField()

    diagnosis_phenotypes = ListField(IntField())
    diagnosis_genes = ListField(IntField())

    has_svvariants = BooleanField(default=False)

    is_migrated = BooleanField(default=False)

    @property
    def analysis_type(self):
        """Determine compound sequencing/analysis type."""
        types = set(sample.analysis_type for sample in self.individuals)
        if len(types) == 1:
            return types.pop()
        else:
            return 'mixed'

    @property
    def o_collaborators(self):
        """Other collaborators than the owner of the case."""
        return [collab_id for collab_id in self.collaborators if
                collab_id != self.owner]

    def default_genes(self):
        """Combine all gene ids for default gene panels."""
        distinct_genes = set()
        for panel in self.default_panels:
            distinct_genes.update(panel.gene_ids)
        return distinct_genes

    @property
    def panel_names(self):
        return [panel.name_and_version for panel in self.default_panels]

    @property
    def default_panel_ids(self):
        """Return ids for the default panels."""
        return [panel.panel_name for panel in self.default_panels]

    @property
    def is_solved(self):
        """Check if the case is marked as solved."""
        return self.status == 'solved'

    @property
    def is_archived(self):
        return self.status in ('solved', 'archived')

    @property
    def is_rerun(self):
        return len(self.analysis_dates) > 1

    @property
    def hpo_gene_ids(self):
        """Parse out all HGNC symbols form the dynamic Phenomizer query."""
        unique_ids = set(term['gene_id'] for term in self.dynamic_gene_list
                         if term['gene_id'])
        return list(unique_ids)

    @property
    def bam_files(self):
        """Aggregate all BAM files across all individuals."""
        return [individual.bam_file for individual in self.individuals
                if individual.bam_file]

    @property
    def bai_files(self):
        """Aggregate all BAM files across all individuals."""
        files = []
        for individual in self.individuals:
            if individual.bam_file:
                bai_file = individual.bam_file.replace('.bam', '.bai')
                if not os.path.exists(bai_file):
                    # try the other convention
                    bai_file = "{}.bai".format(individual.bam_file)
                files.append(bai_file)
        return files

    @property
    def sample_names(self):
        return [individual.display_name for individual in self.individuals
                if individual.bam_file]

    @property
    def sample_ids(self):
        return [individual.individual_id for individual in self.individuals]

    def __repr__(self):
        return ("Case(case_id={0}, display_name={1}, owner={2})"
                .format(self.case_id, self.display_name, self.owner))

    def __unicode__(self):
        return self.display_name
