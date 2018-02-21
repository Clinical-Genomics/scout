# -*- coding: utf-8 -*-
# stdlib modules
import logging
import re
import pathlib
import tempfile

from datetime import datetime
from pprint import pprint as pp

# Third party modules
import pymongo

from cyvcf2 import VCF
from intervaltree import IntervalTree

# Local modules
from scout.parse.variant.headers import (parse_rank_results_header,
                                         parse_vep_header)
from scout.parse.variant.rank_score import parse_rank_score

from scout.parse.variant import parse_variant
from scout.build import build_variant

from pymongo.errors import (DuplicateKeyError, BulkWriteError)
from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class VariantLoader(object):

    """Methods to handle variant loading in the mongo adapter"""

    def update_variant(self, variant_obj):
        """Update one variant document in the database.

        Args:
            variant_obj(dict)

        Returns:
            new_variant(dict)
        """
        new_variant = self.variant_collection.find_one_and_replace(
            {'_id': variant_obj['_id']},
            variant_obj,
            return_document=pymongo.ReturnDocument.AFTER
        )
        return new_variant

    def update_variants(self, case_obj, variant_type='clinical', category='snv'):
        """Adds extra information on variants.

        Add a variant rank based on the rank score
        Add extra information on compounds

            Args:
                case_obj(Case)
                variant_type(str)
        """
        # Get all variants sorted by rank score
        variants = self.variant_collection.find({
            'case_id': case_obj['_id'],
            'category': category,
            'variant_type': variant_type,
        }).sort('rank_score', pymongo.DESCENDING)

        LOG.info("Updating variant_rank for all variants")

        # Update the information on all compounds
        for index, variant in enumerate(variants):
            # This is a list with the updated compound documents
            # compound_objs = self.update_compounds(variant)
            self.variant_collection.find_one_and_update(
                {'_id': variant['_id']},
                {
                    '$set': {
                        'variant_rank': index + 1,
                        # 'compounds': compound_objs,
                    }
                }
            )

        LOG.info("Updating variant_rank done")

    def update_variant_compounds(self, variant, variant_objs = None):
        """Update compounds for a variant.
        
        This will add all the necessary information of a variant on a compound object.
        
        Args:
            variant(scout.models.Variant)
            variant_objs(dict): A dictionary with _ids as keys and variant objs as values.
        
        Returns:
            compound_objs(list(dict)): A dictionary with updated compound objects.
        
        """
        compound_objs = []
        for compound in variant.get('compounds', []):
            not_loaded = True
            gene_objs = []
            # Check if the compound variant exists
            if variant_objs:
                variant_obj = variant_objs.get(compound['variant'])
            else:
                variant_obj = self.variant_collection.find_one({'_id': compound['variant']})
            if variant_obj:
                # If the variant exosts we try to collect as much info as possible
                not_loaded = False
                compound['rank_score'] = variant_obj['rank_score']
                for gene in variant_obj.get('genes', []):
                    gene_obj = {
                        'hgnc_id': gene['hgnc_id'],
                        'hgnc_symbol': gene.get('hgnc_symbol'),
                        'region_annotation': gene.get('region_annotation'),
                        'functional_annotation': gene.get('functional_annotation'),
                    }
                    gene_objs.append(gene_obj)
                    compound['genes'] = gene_objs

            compound['not_loaded'] = not_loaded
            compound_objs.append(compound)
        
        return compound_objs

    def update_compounds(self, variants):
        """Update the compounds for a set of variants.
        
        Args:
            variants(dict): A dictionary with _ids as keys and variant objs as values

        """
        LOG.debug("Updating compound objects")
        for variant_obj in variants.values():
            if not variant_obj.get('compounds'):
                continue
            var_id = variant_obj['simple_id']
            updated_compounds = self.updated_compounds(variant_obj, variants)

            variants[var_id]['compounds'] = updated_compounds

        LOG.debug("Compounds updated")

        return 

    def update_case_compounds(self, case_id, build='37', variant_type='clinical'):
        """Update the compounds for a case

        Loop over all coding intervals to get coordinates for all potential compound positions.
        Update all variants within a gene with a bulk operation.
        """
        categories = ['snv', 'sv', 'cancer']

        coding_intervals = self.get_coding_intervals(build=build)

        for chrom in coding_intervals:
            for iv in coding_intervals[chrom]:
                for category in categories:
                    query  = {
                        'variant_type': variant_type,
                        'chrom': chrom,
                        'start': iv.begin,
                        'end': iv.end,
                    }
                    variant_objs = self.variants(
                        case_id=case_id, 
                        query=query, 
                        category='category',
                        nr_of_variants=-1
                    )
    

    def add_variant_rank(self, case_obj, variant_type='clinical', category='snv'):
        """Add the variant rank for all inserted variants.

            Args:
                case_obj(Case)
                variant_type(str)
        """
        variants = self.variant_collection.find(
            {
                'case_id': case_obj['_id'],
                'category': category,
                'variant_type': variant_type,
            },
            {'_id':1}
        ).sort('rank_score', pymongo.DESCENDING)

        LOG.info("Updating variant_rank for all variants")
        for index, variant in enumerate(variants):
            self.variant_collection.find_one_and_update(
                {'_id': variant['_id']},
                {'$set': {'variant_rank': index + 1}}
            )
        LOG.info("Updating variant_rank done")

    def other_causatives(self, case_obj, variant_obj):
        """Find the same variant in other cases marked causative."""
        # variant id without "*_[variant_type]"
        variant_id = variant_obj['display_name'].rsplit('_', 1)[0]

        institute_causatives = self.get_causatives(variant_obj['institute'])
        for causative_id in institute_causatives:
            other_variant = self.variant(causative_id)
            not_same_case = other_variant['case_id'] != case_obj['_id']
            same_variant = other_variant['display_name'].startswith(variant_id)
            if not_same_case and same_variant:
                yield other_variant

    def load_variant(self, variant_obj):
        """Load a variant object

        Args:
            variant_obj(dict)

        Returns:
            inserted_id
        """
        LOG.debug("Loading variant %s", variant_obj['_id'])
        try:
            result = self.variant_collection.insert_one(variant_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Variant %s already exists in database", variant_obj['_id'])
        return 

    def load_variant_bulk(self, variants):
        """Load a bulk of variants

        Args:
            variants(iterable(scout.models.Variant))

        Returns:
            object_ids
        """
        if not len(variants) > 0:
            return
        LOG.debug("Loading variant batch")
        try:
            result = self.variant_collection.insert_many(variants)
        except DuplicateKeyError as err:
            # If the bulk write is wrong there are probably some variants already existing
            # In the database. So insert each variant 
            for var_obj in variants:
                try:
                    self.load_variant(var_obj)
                except IntegrityError as err:
                    pass

        return

    def _load_variants(self, variants, variant_type, case_obj, individual_positions, rank_threshold,
                       institute_id, build=None, rank_results_header=None, vep_header=None, 
                       category='snv', sample_info = None):
        """Perform the loading of variants
            
        This is the function that loops over the variants, parse them and build the variant 
        objects so they are ready to be inserted into the database.
                       
        """
        build = build or '37'
        genes = self.all_genes(build=build)
        gene_to_panels = self.gene_to_panels()
        hgncid_to_gene = self.hgncid_to_gene(genes=genes)
        genomic_intervals = self.get_coding_intervals(genes=genes)
        
        LOG.info("Start inserting variants into database")
        start_insertion = datetime.now()
        start_five_thousand = datetime.now()
        # These are the number of parsed varaints
        nr_variants = 0
        # These are the number of variants that meet the criteria and gets inserted
        nr_inserted = 0
        # This is to keep track of blocks of inserted variants
        inserted = 1
        
        nr_bulks = 0
        
        # We want to load batches of variants to reduce the number of network round trips
        bulk = {}
        current_region = None
        
        for nr_variants, variant in enumerate(variants):
            # All MT variants are loaded
            mt_variant = 'MT' in variant.CHROM
            rank_score = parse_rank_score(variant.INFO.get('RankScore'), case_obj['_id'])
            
            # Check if the variant should be loaded at all
            # if rank score is None means there are no rank scores annotated, all variants will be loaded
            # Otherwise we load all variants above a rank score treshold
            # Except for MT variants where we load all variants
            if (rank_score is None) or (rank_score > rank_threshold) or mt_variant:
                nr_inserted += 1
                # Parse the vcf variant
                parsed_variant = parse_variant(
                    variant=variant,
                    case=case_obj,
                    variant_type=variant_type,
                    rank_results_header=rank_results_header,
                    vep_header=vep_header,
                    individual_positions=individual_positions,
                    category=category,
                )

                # Build the variant object
                variant_obj = build_variant(
                    variant=parsed_variant,
                    institute_id=institute_id,
                    gene_to_panels=gene_to_panels,
                    hgncid_to_gene=hgncid_to_gene,
                    sample_info=sample_info
                )

                # Check if the variant is in a genomic region
                var_chrom = variant_obj['chromosome']
                var_start = variant_obj['position']
                var_end = variant_obj['end']
                var_id = variant_obj['simple_id']
                # If the bulk should be loaded or not
                load = True
                new_region = None

                genomic_regions = genomic_intervals.get(var_chrom, IntervalTree()).search(var_start, var_end)

                # If the variant is in a coding region
                if genomic_regions:
                    # We know there is data here so get the interval id
                    new_region = genomic_regions.pop().data
                    # If the variant is in the same region as previous
                    # we add it to the same bulk
                    if new_region == current_region:
                        load = False
                
                # This is the case where the variant is intergenic
                else:
                    # If the previous variant was also intergenic we add the variant to the bulk
                    if not current_region:
                        load = False
                    # We need to have a max size of the bulk
                    if len(bulk) > 10000:
                        load = True

                # Load the variant object
                if load:
                    # If the variant bulk contains coding variants we want to update the compounds
                    if current_region:
                        self.update_compounds(bulk)
                    try:
                        # Load the variants
                        self.load_variant_bulk(list(bulk.values()))
                        nr_bulks += 1
                    except IntegrityError as error:
                        pass
                    bulk = {}
                
                current_region = new_region
                bulk[var_id] = variant_obj
                
                if (nr_variants != 0 and nr_variants % 5000 == 0):
                    LOG.info("%s variants parsed", str(nr_variants))
                    LOG.info("Time to parse variants: %s",
                                (datetime.now() - start_five_thousand))
                    start_five_thousand = datetime.now()

                if (nr_inserted != 0 and (nr_inserted * inserted) % (1000 * inserted) == 0):
                    LOG.info("%s variants inserted", nr_inserted)
                    inserted += 1
        
        # Load the final variant bulk
        self.load_variant_bulk(list(bulk.values()))
        nr_bulks += 1

        LOG.info("All variants inserted, time to insert variants: {0}".format(
            datetime.now() - start_insertion))
        LOG.info("Nr variants inserted: %s", nr_inserted)
        LOG.debug("Nr bulks inserted: %s", nr_bulks)

        return nr_inserted

    def load_variants(self, case_obj, variant_type='clinical', category='snv',
                      rank_threshold=None, chrom=None, start=None, end=None,
                      gene_obj=None, build='37'):
        """Load variants for a case into scout.

        Load the variants for a specific analysis type and category into scout.
        If no region is specified, load all variants above rank score threshold
        If region or gene is specified, load all variants from that region
        disregarding variant rank(if not specified)

        Args:
            case_obj(dict): A case from the scout database
            variant_type(str): 'clinical' or 'research'. Default: 'clinical'
            category(str): 'snv' or 'sv'. Default: 'snv'
            rank_threshold(float): Only load variants above this score. Default: 0
            chrom(str): Load variants from a certain chromosome
            start(int): Specify the start position
            end(int): Specify the end position
            gene_obj(dict): A gene object from the database

        Returns:
            nr_inserted(int)
        """
        # We need the institute object
        institute_id = self.institute(institute_id=case_obj['owner'])['_id']

        variant_file = None
        if variant_type == 'clinical':
            if category == 'snv':
                variant_file = case_obj['vcf_files'].get('vcf_snv')
            elif category == 'sv':
                variant_file = case_obj['vcf_files'].get('vcf_sv')
            elif category == 'cancer':
                # Currently this implies a paired tumor normal
                variant_file = case_obj['vcf_files'].get('vcf_cancer')
        elif variant_type == 'research':
            if category == 'snv':
                variant_file = case_obj['vcf_files'].get('vcf_snv_research')
            elif category == 'sv':
                variant_file = case_obj['vcf_files'].get('vcf_sv_research')
            elif category == 'cancer':
                variant_file = case_obj['vcf_files'].get('vcf_cancer_research')

        if not variant_file:
            raise SyntaxError("Vcf file does not seem to exist")

        vcf_obj = VCF(variant_file)

        # Parse the neccessary headers from vcf file
        rank_results_header = parse_rank_results_header(vcf_obj)
        vep_header = parse_vep_header(vcf_obj)

        # This is a dictionary to tell where ind are in vcf
        individual_positions = {}
        for i, ind in enumerate(vcf_obj.samples):
            individual_positions[ind] = i

        # Dictionary for cancer analysis
        sample_info = {}
        if category == 'cancer':
            for ind in case_obj['individuals']:
                if ind['phenotype'] == 2:
                    sample_info[ind['individual_id']] = 'case'
                else:
                    sample_info[ind['individual_id']] = 'control'

        # Check if a region scould be uploaded
        region = ""
        if gene_obj:
            chrom = gene_obj['chromosome']
            # Add same padding as VEP
            start = max(gene_obj['start'] - 5000, 0)
            end = gene_obj['end'] + 5000
        if chrom:
            # We want to load all variants in the region regardless of rank score
            rank_threshold = rank_threshold or -1000
            if not (start and end):
                raise SyntaxError("Specify chrom start and end")
            region = "{0}:{1}-{2}".format(chrom, start, end)
        else:
            rank_threshold = rank_threshold or 0

        variants = vcf_obj(region)
        
        try:
            nr_inserted = self._load_variants(
                variants=variants, 
                variant_type=variant_type, 
                case_obj=case_obj, 
                individual_positions=individual_positions, 
                rank_threshold=rank_threshold,
                institute_id=institute_id, 
                build=build, 
                rank_results_header=rank_results_header, 
                vep_header=vep_header, 
                category=category, 
                sample_info = sample_info
            )
        except Exception as error:
            LOG.exception('unexpected error')
            LOG.warning("Deleting inserted variants")
            self.delete_variants(case_obj['_id'], variant_type)
            raise error

        self.update_variants(case_obj, variant_type, category=category)
        
        ## If all variants of a region are loaded we need to update the compounds of that region
        if region:
            LOG.info("Updating compound information for all variants in region")
            # Get all variants in a region
            query = self.build_query(
                        case_id=case_obj['_id'],
                        query={
                            'variant_type': variant_type,
                            'chrom': chrom,
                            'start': start,
                            'end': end,
                        },
                        category=category
                    )
            res = self.variant_collection.find(query)
            # Store them in a dictionary for faster access
            # This should not be dangerous since we know there is a limited number of variants for
            # a region
            variants = {var['_id']: var for var in res}
            # Get a iterable with variant objs. This is to avoid to iterate over a dictionary that
            # will be updated during iteration
            variant_objs = variants.values()
            
            # Now update the compound information for all variants in the region
            for variant_obj in variant_objs:
                if not variant_obj.get('compounds'):
                    continue

                # get a list with updated compounds
                new_compounds = self.update_compounds(variant_obj, variants)
                # Update the variant
                variant_obj['compounds'] = new_compounds

                # sort compounds on combined rank score
                variant_obj['compounds'] = sorted(variant_obj['compounds'],
                                              key=lambda compound: -compound['combined_score'])
                # Store the information in the database
                self.update_variant(variant_obj)


        return nr_inserted
