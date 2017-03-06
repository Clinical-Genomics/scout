# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import (division)
import itertools

from mongoengine import (Document, EmbeddedDocument, EmbeddedDocumentField,
                         FloatField, IntField, ListField, StringField,
                         ReferenceField, SortedListField, Q, BooleanField,
                         DoesNotExist, DictField)

from scout.constants import (CONSERVATION, ACMG_TERMS, GENETIC_MODELS,
                             VARIANT_CALL, CLINSIG_MAP)
from .gene import Gene
from scout.models import Event

variant = dict(
    # document_id is a md5 string created by institute_genelist_caseid_variantid:
    _id = str, # required, same as document_id
    document_id = str, # required
    # variant_id is a md5 string created by chrom_pos_ref_alt (simple_id)
    variant_id = str, # required
    # display name is variant_id (no md5)
    display_name = str, # required

    # chrom_pos_ref_alt
    simple_id = str,
    # The variant can be either research or clinical.
    # For research variants we display all the available information while
    # the clinical variants have limited annotation fields.
    variant_type = str, # required, choices=('research', 'clinical'))

    category = str, # choices=('sv', 'snv')
    sub_category = str, # choices=('snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv', 'bnd')
    mate_id = str, # For SVs this identifies the other end

    case_id = str, # case_id is a string like owner_caseid
    chromosome = str, # required
    position = int, # required
    end = int, # required
    length = int, # required
    reference = str, # required
    alternative = str, # required

    rank_score = float, # required
    variant_rank = int, # required
    rank_score_results = list, # List if dictionaries

    institute = str, # institute_id, required

    sanger_ordered = bool,
    validation = str, # Sanger validation, choices=('True positive', 'False positive')

    quality = float,
    filters = list, # list of strings
    samples = list, # list of dictionaries that are <gt_calls>
    genetic_models = list, # list of strings choices=GENETIC_MODELS
    compounds = list, # sorted list of <compound> ordering='combined_score'

    genes = list, # list with <gene>
    dbsnp_id = str,

    # Gene ids:
    hgnc_ids = list, # list of hgnc ids (int)
    hgnc_symbols = list, # list of hgnc symbols (str)
    panels = list, # list of panel names that the variant ovelapps

    # Frequencies:
    thousand_genomes_frequency = float,
    thousand_genomes_frequency_left = float,
    thousand_genomes_frequency_right = float,
    exac_frequency = float,
    max_thousand_genomes_frequency = float,
    max_exac_frequency = float,
    local_frequency = float,
    local_obs_old = int,
    local_obs_hom_old = int,
    local_obs_total_old = int, # default=638
    # Predicted deleteriousness:
    cadd_score = float,
    clnsig = list, # list of <clinsig>
    spidex = float,

    missing_data = bool, # default False

    # Callers
    gatk = str, # choices=VARIANT_CALL, default='Not Used'
    samtools = str, # choices=VARIANT_CALL, default='Not Used'
    freebayes = str, # choices=VARIANT_CALL, default='Not Used'

    # Conservation:
    phast_conservation = list, # list of str, choices=CONSERVATION
    gerp_conservation = list, # list of str, choices=CONSERVATION
    phylop_conservation = list, # list of str, choices=CONSERVATION
    # Database options:
    gene_lists = list,
    manual_rank = int, # choices=[0, 1, 2, 3, 4, 5]

    acmg_evaluation = str, # choices=ACMG_TERMS
)

compound = dict(
    # This must be the document_id for this variant
    variant = str, # required=True
    # This is the variant id
    display_name = str, # required
    combined_score = float, # required
)

clinsig = dict(
    value = int,
    accession = str,
    revstat = str
)

gt_call = dict(
    sample_id = str,
    display_name = str,
    genotype_call = str,
    allele_depths = list, # int
    read_depth = int,
    genotype_quality = int,
)

class Compound(EmbeddedDocument):
    # This must be the document_id for this variant
    variant = StringField(required=True)
    # This is the variant id
    display_name = StringField(required=True)
    combined_score = FloatField(required=True)

    _variant_obj = None

    @property
    def variant_obj(self):
        """Return the full variant object"""
        if self._variant_obj is None:
            try:
                self._variant_obj = Variant.objects.get(document_id=self.variant)
            except DoesNotExist:
                pass
        return self._variant_obj


class Clinsig(EmbeddedDocument):
    value = IntField()
    accession = StringField()
    revstat = StringField()


class GTCall(EmbeddedDocument):
    sample_id = StringField()
    display_name = StringField()
    genotype_call = StringField()
    allele_depths = ListField(IntField())
    read_depth = IntField()
    genotype_quality = IntField()

    def __unicode__(self):
        return self.display_name


class Variant(Document):

    meta = {'strict': False}

    # document_id is a md5 string created by institute_genelist_caseid_variantid:
    document_id = StringField(primary_key=True)
    # variant_id is a md5 string created by chrom_pos_ref_alt (simple_id)
    variant_id = StringField(required=True)
    # display name in variant_id (no md5)
    display_name = StringField(required=True)

    # chrom_pos_ref_alt
    simple_id = StringField()
    # The variant can be either research or clinical.
    # For research variants we display all the available information while
    # the clinical variants have limited annotation fields.
    variant_type = StringField(required=True,
                               choices=('research', 'clinical'))

    category = StringField(choices=('sv', 'snv'))
    sub_category = StringField(choices=(
                    'snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv', 'bnd'))
    mate_id = StringField()
    # case_id is a string like owner_caseid
    case_id = StringField(required=True)
    chromosome = StringField(required=True)
    position = IntField(required=True)
    end = IntField()
    length = IntField()
    reference = StringField(required=True)
    alternative = StringField(required=True)

    rank_score = FloatField(required=True)
    rank_score_results = ListField(DictField())
    variant_rank = IntField()
    institute = ReferenceField('Institute', required=True)

    sanger_ordered = BooleanField()
    validation = StringField(choices=('True positive', 'False positive'))

    quality = FloatField()
    filters = ListField(StringField())
    samples = ListField(EmbeddedDocumentField(GTCall))
    genetic_models = ListField(StringField(choices=GENETIC_MODELS))
    compounds = SortedListField(EmbeddedDocumentField(Compound),
                                ordering='combined_score', reverse=True)

    genes = ListField(EmbeddedDocumentField(Gene))
    dbsnp_id = StringField()

    # Gene ids:
    hgnc_ids = ListField(IntField())
    hgnc_symbols = ListField(StringField())
    panels = ListField(StringField())

    # Frequencies:
    thousand_genomes_frequency = FloatField()
    thousand_genomes_frequency_left = FloatField()
    thousand_genomes_frequency_right = FloatField()
    exac_frequency = FloatField()
    max_thousand_genomes_frequency = FloatField()
    max_exac_frequency = FloatField()
    local_frequency = FloatField()
    local_obs_old = IntField()
    local_obs_hom_old = IntField()
    local_obs_total_old = IntField(default=638)
    # Predicted deleteriousness:
    cadd_score = FloatField()
    clnsig = ListField(EmbeddedDocumentField(Clinsig))
    spidex = FloatField()

    missing_data = BooleanField(default=False)

    @property
    def spidex_human(self):
        """Translate SPIDEX annotation to human readable string."""
        if self.spidex is None:
            return 'not_reported'
        elif abs(self.spidex) < 1:
            return 'low'
        elif abs(self.spidex) < 2:
            return 'medium'
        else:
            return 'high'

    # Callers
    gatk = StringField(choices=VARIANT_CALL, default='Not Used')
    samtools = StringField(choices=VARIANT_CALL, default='Not Used')
    freebayes = StringField(choices=VARIANT_CALL, default='Not Used')

    # Conservation:
    phast_conservation = ListField(StringField(choices=CONSERVATION))
    gerp_conservation = ListField(StringField(choices=CONSERVATION))
    phylop_conservation = ListField(StringField(choices=CONSERVATION))
    # Database options:
    gene_lists = ListField(StringField())
    manual_rank = IntField(choices=[0, 1, 2, 3, 4, 5])

    acmg_evaluation = StringField(choices=ACMG_TERMS)

    @property
    def expected_inheritance(self):
        """Gather information from common gene information."""
        all_models = set()
        for gene in self.genes:
            for model in gene.common.expected_inheritance:
                all_models.add(model)
        return list(all_models)

    @property
    def case_displayname(self):
        """Convert case_id to family id or display name."""
        return self.case_id.split('_')[-1]

    @property
    def callers(self):
        """Return call for all callers."""
        calls = [('GATK', self.gatk), ('Samtools', self.samtools),
                 ('Freebayes', self.freebayes)]
        existing_calls = [(name, caller) for name, caller in calls if caller]
        return existing_calls

    @property
    def composite_id(self):
        """Compose variant id from components."""
        return ("{this.chromosome}_{this.position}_{this.reference}_"
                "{this.alternative}".format(this=self))

    @property
    def reduced_penetrance_genes(self):
        for gene in self.genes:
            if gene.common:
                name = gene.common.hgnc_symbol
                common_penetrance = gene.common.incomplete_penetrance
                if getattr(gene, 'panel_info', None):
                    panel_penetrance = gene.panel_info.reduced_penetrance
                else:
                    panel_penetrance = False
                yield name, common_penetrance, panel_penetrance

    def has_comments(self, case):
        """
        Return True is there are any comments for this variant in the database
        """
        events = Event.objects.filter(Q(verb='comment') &
                                      Q(variant_id=self.variant_id) &
                                      Q(institute=self.institute) &
                                      (Q(case=case) | Q(level='global')))

        return True if events else False

    @property
    def clnsig_human(self):
        for clinsig_obj in self.clnsig:
            human_str = CLINSIG_MAP.get(clinsig_obj.value, 'not provided')
            yield clinsig_obj, human_str

    @property
    def omim_annotation_links(self):
        """Return a list of OMIM id links."""
        base_url = 'http://www.omim.org/entry'

        for gene in self.genes:
            omim_link = "{base}/{id}".format(base=base_url,
                                             id=gene.omim_gene_entry)
            yield gene.hgnc_symbol, omim_link

    @property
    def disease_terms(self):
        """Return all disease terms."""
        for gene in self.genes:
            for term in gene.disease_terms:
                yield gene, term

    @property
    def omim_inheritance_models(self):
        """Return a list of OMIM inheritance models (phenotype based)."""
        models = ((phenotype.disease_models for phenotype in
                   gene.omim_phenotypes) for gene in self.genes)

        # untangle multiple nested list of list of lists...
        return set(
            itertools.chain.from_iterable(itertools.chain.from_iterable(models))
        )

    @property
    def region_annotations(self):
        """Returns a list with region annotation(s)."""
        if len(self.genes) == 1:
            return [gene.region_annotation for gene in self.genes]
        else:
            annotations = [("{gene.hgnc_symbol}:{gene.region_annotation}"
                            .format(gene=gene)) for gene in self.genes]
            return annotations

    @property
    def sift_predictions(self):
        """Return a list with the sift prediction(s) for this variant.

        The most severe for each gene.
        """
        sift_predictions = []
        if len(self.genes) == 1:
            sift_predictions = [(gene.sift_prediction or '-') for gene in self.genes]
        else:
            for gene in self.genes:
                sift_predictions.append(':'.join([
                    gene.hgnc_symbol, gene.sift_prediction or '-']))
        return sift_predictions

    @property
    def polyphen_predictions(self):
        """Return a list with the polyphen prediction(s) for this variant.

        The most severe for each gene.
        """
        polyphen_predictions = []
        if len(self.genes) == 1:
            polyphen_predictions = [(gene.polyphen_prediction or '-') for gene in self.genes]
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
                yield gene, transcript

    @property
    def refseq_transcripts(self):
        """Yield all transcripts with a RefSeq id."""
        for gene, transcript in self.transcripts:
            if getattr(transcript, 'common', None) and transcript.common.refseq_id:
                yield gene, transcript

    @property
    def protein_changes(self):
        for transcript in self.refseq_transcripts:
            yield transcript.stringify()

    @property
    def end_position(self):
        # bases contained in alternative allele
        alt_bases = len(self.alternative)
        # vs. reference allele
        bases = max(len(self.reference), alt_bases)

        return self.position + (bases - 1)

    # This is exactly the same as variant_id...
    @property
    def frequency(self):
        """Returns a judgement on the overall frequency of the variant.

        Combines multiple metrics into a single call.
        """
        most_common_frequency = max(self.thousand_genomes_frequency or 0,
                                    self.exac_frequency or 0)
        if most_common_frequency > .05:
            return 'common'
        elif most_common_frequency > .01:
            return 'uncommon'
        else:
            return 'rare'

    @property
    def sv_frequencies(self):
        """Return all SV frequencies."""
        return [
            ('1000G', self.thousand_genomes_frequency),
            ('1000G (left)', self.thousand_genomes_frequency_left),
            ('1000G (right)', self.thousand_genomes_frequency_right),
        ]

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
    def thousandg_link(self):
        """Compose link to 1000G page for detailed information."""
        if self.db_snp_ids:
            url_template = ("http://browser.1000genomes.org/Homo_sapiens/"
                            "Variation/Population?db=core;source=dbSNP;v={}")
            return url_template.format(self.db_snp_ids[0])

    @property
    def ucsc_link(self):
        url_template = ("http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&"\
                        "position=chr{this.chromosome}:{this.position}"\
                        "-{this.position}&dgv=pack&knownGene=pack&omimGene=pack")
        return url_template.format(this=self)

    meta = {
        'index_background': True,
        'indexes': [
            ('case_id', '+variant_type', '+variant_rank', 'panels', '+thousand_genomes_frequency'),
            ('case_id', 'variant_id'),
            ('case_id', 'category', 'variant_type', '-rank_score'),
            ('case_id', 'category', 'variant_type', 'panels', '+variant_rank'),
        ]
    }

    def __unicode__(self):
        return self.display_name
