# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import (division)
import itertools

from mongoengine import (Document, EmbeddedDocument, EmbeddedDocumentField,
                         FloatField, IntField, ListField, StringField,
                         ReferenceField, SortedListField, Q, BooleanField)

from . import (CONSERVATION, ACMG_TERMS, GENETIC_MODELS)
from .gene import Gene
from scout._compat import zip
from scout.models import Event

######## These are defined terms for different categories ########


class Compound(EmbeddedDocument):
    # This must be the document_id for this variant
    variant = ReferenceField('Variant')
    # This is the variant id
    display_name = StringField(required=True)
    combined_score = FloatField(required=True)


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
    # variant_id is a md5 string created by variant_id
    variant_id = StringField(required=True)
    # display name in variant_id (no md5)
    display_name = StringField(required=True)
    # The variant can be either a reserch variant or a clinical variant.
    # For research variants we display all the available information while
    # the clinical variants hae limited annotation fields.
    variant_type = StringField(required=True,
                               choices=('research', 'clinical'))
    # case_id is a string like owner_caseid
    case_id = StringField(required=True)
    chromosome = StringField(required=True)
    position = IntField(required=True)
    reference = StringField(required=True)
    alternative = StringField(required=True)
    rank_score = FloatField(required=True)
    variant_rank = IntField(required=True)
    institute = ReferenceField('Institute', required=True)
    sanger_ordered = BooleanField()
    quality = FloatField()
    filters = ListField(StringField())
    samples = ListField(EmbeddedDocumentField(GTCall))
    genetic_models = ListField(StringField(choices=GENETIC_MODELS))
    compounds = SortedListField(EmbeddedDocumentField(Compound),
                                ordering='combined_score', reverse=True)

    genes = ListField(EmbeddedDocumentField(Gene))
    db_snp_ids = ListField(StringField())
    # Gene ids:
    hgnc_symbols = ListField(StringField())
    ensembl_gene_ids = ListField(StringField())
    # Frequencies:
    thousand_genomes_frequency = FloatField()
    exac_frequency = FloatField()
    max_thousand_genomes_frequency = FloatField()
    max_exac_frequency = FloatField()
    local_frequency = FloatField()
    # Predicted deleteriousness:
    cadd_score = FloatField()
    clnsig = IntField()
    clnsigacc = ListField(StringField())

    @property
    def composite_id(self):
        """Compose variant id from components."""
        return ("{this.chromosome}_{this.position}_{this.reference}_"
                "{this.alternative}".format(this=self))

    @property
    def reduced_penetrance_genes(self):
        return (gene for gene in self.genes if gene.reduced_penetrance)

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
        return {
            0: 'Uncertain significance', 1: 'not provided', 2: 'Benign',
            3: 'Likely benign', 4: 'Likely pathogenic', 5: 'Pathogenic',
            6: 'drug response', 7: 'histocompatibility', 255: 'other'
        }.get(self.clnsig, 'not provided')

    # Conservation:
    phast_conservation = ListField(StringField(choices=CONSERVATION))
    gerp_conservation = ListField(StringField(choices=CONSERVATION))
    phylop_conservation = ListField(StringField(choices=CONSERVATION))
    # Database options:
    gene_lists = ListField(StringField())
    expected_inheritance = ListField(StringField())
    manual_rank = IntField(choices=[0, 1, 2, 3, 4, 5])

    acmg_evaluation = StringField(choices=ACMG_TERMS)

    @property
    def omim_annotations(self):
        """Returns a list with OMIM id(s)."""
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
        """Return a list of OMIM id links."""
        base_url = 'http://www.omim.org/entry'

        for omim_id_str in self.omim_annotations:
            # handle cases with variant overlapping multiple genes
            omim_id_parts = omim_id_str.split(':')
            if len(omim_id_parts) == 1:
                # single gene overlap
                omim_id = omim_id_parts[0]

            else:
                # multiple genes
                omim_id = omim_id_parts[1]

            yield (omim_id_str, "{base}/{id}".format(base=base_url, id=omim_id))

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
        return set(
          itertools.chain.from_iterable(itertools.chain.from_iterable(models))
        )

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
                yield transcript

    @property
    def refseq_transcripts(self):
      """Yield all transcripts with a RefSeq id."""
      for transcript in self.transcripts:
        if transcript.refseq_ids:
          yield transcript

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

    ##TODO Add indexes to document
    meta = {
        'index_background': True,
        'indexes':[
            'rank_score',
            ('case_id' ,'+variant_rank', '+variant_type', '+thousand_genomes_frequency'),
            ('hgnc_symbols', '+exac_frequency'),
            ('thousand_genomes_frequency', '+genes.functional_annotation',
            '+genes.region_annotation'),
        ]
    }

    def __unicode__(self):
        return self.display_name

