from __future__ import (absolute_import)
import os
import logging
from datetime import datetime

from mongoengine import (Document, StringField, ListField, ReferenceField,
                         EmbeddedDocumentField, DateTimeField, BooleanField,
                         BinaryField, FloatField, DictField, IntField)

from . import STATUS
from .individual import Individual
from .gene_list import GenePanel
from scout.models import PhenotypeTerm

logger = logging.getLogger(__name__)


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
    rank_score_treshold = IntField(default=5)

    phenotype_terms = ListField(EmbeddedDocumentField(PhenotypeTerm))
    phenotype_groups = ListField(EmbeddedDocumentField(PhenotypeTerm))
    # madeline info is a full xml file
    madeline_info = StringField()

    vcf_files = DictField()

    diagnosis_phenotypes = ListField(IntField())
    diagnosis_genes = ListField(IntField())

    has_svvariants = BooleanField(default=False)

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
            for gene in panel.gene_objects.values():
                distinct_genes.add(gene.hgnc_gene.hgnc_id)
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

    @property
    def sorted_gene_panels(self):
        """Return clinical panels sorted by name."""
        panels = sorted(self.gene_panels,
                        key=lambda panel: panel.display_name)
        return panels

    def __repr__(self):
        return ("Case(case_id={0}, display_name={1}, owner={2})"
                .format(self.case_id, self.display_name, self.owner))

    def __unicode__(self):
        return self.display_name
