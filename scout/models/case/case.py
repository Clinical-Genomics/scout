from __future__ import (absolute_import)
import logging
from datetime import datetime
import itertools

from mongoengine import (Document, StringField, ListField, ReferenceField,
                         EmbeddedDocumentField, DateTimeField, BooleanField,
                         BinaryField, FloatField, DictField)

from . import STATUS
from .individual import Individual
from .gene_list import GenePanel
from scout.models import PhenotypeTerm
from scout.constants import ANALYSIS_TYPES

logger = logging.getLogger(__name__)


class Case(Document):

    """Represents a case (family) of individuals (samples)."""

    meta = {'index_background': True, 'indexes': ['updated_at'],
            'strict': False}

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

    # default_panels specifies which gene lists that should be shown when
    # the case is opened
    default_panels = ListField(StringField())
    clinical_panels = ListField(ReferenceField(GenePanel))
    research_panels = ListField(ReferenceField(GenePanel))
    dynamic_gene_list = ListField(DictField())

    genome_build = StringField()
    genome_version = FloatField()

    analysis_date = StringField()
    analysis_dates = ListField(StringField())
    rank_model_version = StringField()
    analysis_type = StringField(choices=ANALYSIS_TYPES)

    gender_check = StringField(choices=['unconfirmed', 'confirm', 'deviation'],
                               default='unconfirmed')
    phenotype_terms = ListField(EmbeddedDocumentField(PhenotypeTerm))
    # madeline info is a full xml file
    madeline_info = StringField()
    vcf_file = StringField()

    # completed analysis
    analysis_checked = BooleanField()

    # The coverage report will be read as a binary blob
    coverage_report = BinaryField()

    @property
    def o_collaborators(self):
        """Other collaborators than the owner of the case."""
        return [collab_id for collab_id in self.collaborators if
                collab_id != self.owner]

    def default_panel_objs(self):
        """Match gene panels with default references."""
        for panel in self.clinical_panels:
            try:
                if panel.panel_name in self.default_panels:
                    yield panel
            except AttributeError as error:
                logger.warn(error.message)
                self.clinical_panels.remove(panel)
                self.save()

    def default_genes(self):
        """Combine all gene ids for default gene panels."""
        distinct_genes = set()
        for panel in self.default_panel_objs():
            distinct_genes.update(panel.genes)
        return distinct_genes

    @property
    def is_solved(self):
        """Check if the case is marked as solved."""
        return self.status == 'solved'

    @property
    def is_rerun(self):
        return self.analysis_dates and len(self.analysis_dates) > 1

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
        return [individual.bam_file.replace('.bam', '.bai')
                for individual in self.individuals if individual.bam_file]

    @property
    def sample_names(self):
        return [individual.display_name for individual in self.individuals
                if individual.bam_file]

    @property
    def sample_ids(self):
        return [individual.individual_id for individual in self.individuals]

    @property
    def all_panels(self):
        """Yield all gene lists (both clinical and research)."""
        return itertools.chain(self.clinical_panels,
                               self.research_panels)

    @property
    def owner_case_id(self):
        """Return an id using both owner and case."""
        return "{this.owner}-{this.display_name}".format(this=self)

    def __repr__(self):
        return ("Case(case_id={0}, display_name={1}, owner={2})"
                .format(self.case_id, self.display_name, self.owner))
