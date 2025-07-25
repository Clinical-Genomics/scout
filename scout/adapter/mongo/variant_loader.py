# -*- coding: utf-8 -*-
# stdlib modules
import logging
import sys
from datetime import datetime
from typing import Dict, Iterable, Optional

import cyvcf2

# Third party modules
import pymongo
from click import progressbar
from cyvcf2 import VCF, Variant
from intervaltree import IntervalTree
from pymongo.errors import BulkWriteError, DuplicateKeyError

from scout.build import build_variant
from scout.constants import CHROMOSOMES, ORDERED_FILE_TYPE_MAP
from scout.exceptions import IntegrityError
from scout.parse.variant import parse_variant
from scout.parse.variant.clnsig import is_pathogenic
from scout.parse.variant.coordinates import parse_coordinates

# Local modules
from scout.parse.variant.headers import (
    parse_local_archive_header,
    parse_rank_results_header,
    parse_vep_header,
)
from scout.parse.variant.ids import parse_simple_id
from scout.parse.variant.managed_variant import parse_managed_variant_id
from scout.parse.variant.rank_score import parse_rank_score

LOG = logging.getLogger(__name__)


class VariantLoader(object):
    """Methods to handle variant loading in the mongo adapter"""

    def update_variant(self, variant_obj):
        """Update one variant document in the database.

        This means that the variant in the database will be replaced by variant_obj.

        Args:
            variant_obj(dict)

        Returns:
            new_variant(dict)
        """
        LOG.debug("Updating variant %s", variant_obj.get("simple_id"))

        new_variant = self.variant_collection.find_one_and_replace(
            {"_id": variant_obj["_id"]},
            variant_obj,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return new_variant

    def update_variant_rank(self, case_obj, variant_type="clinical", category="snv"):
        """Updates the manual rank for all variants in a case

        Add a variant rank based on the rank score
        Whenever variants are added or removed from a case we need to update the variant rank

        Args:
            case_obj(Case)
            variant_type(str)
        """
        # Get all variants sorted by rank score
        variants = self.variant_collection.find(
            {
                "case_id": case_obj["_id"],
                "category": category,
                "variant_type": variant_type,
            }
        ).sort("rank_score", pymongo.DESCENDING)

        LOG.info("Updating variant_rank for all variants")

        requests = []

        for index, var_obj in enumerate(variants):
            operation = pymongo.UpdateOne(
                {"_id": var_obj["_id"]}, {"$set": {"variant_rank": index + 1}}
            )
            requests.append(operation)

            if len(requests) < 5000:
                continue
            try:
                self.variant_collection.bulk_write(requests, ordered=False)
                requests = []
            except BulkWriteError as err:
                LOG.warning("Updating variant rank failed")
                raise err

        # Update the final bulk
        if len(requests) > 0:
            try:
                self.variant_collection.bulk_write(requests, ordered=False)
            except BulkWriteError as err:
                LOG.warning("Updating variant rank failed")
                raise err

        LOG.info("Updating variant_rank done")

    def update_variant_compounds(self, variant, variant_objs=None):
        """Update compounds for a variant.

        This will add all the necessary information of a variant on a compound object.

        Args:
            variant(scout.models.Variant)
            variant_objs(dict): A dictionary with _ids as keys and variant objs as values.

        Returns:
            compound_objs(list(dict)): A dictionary with updated compound objects.

        """
        compound_objs = []
        for compound in variant.get("compounds", []):
            not_loaded = True
            gene_objs = []
            # Check if the compound variant exists
            if variant_objs:
                variant_obj = variant_objs.get(compound["variant"])
            else:
                variant_obj = self.variant_collection.find_one({"_id": compound["variant"]})
            if variant_obj:
                # If the variant exists we try to collect as much info as possible
                not_loaded = False
                compound["rank_score"] = variant_obj["rank_score"]
                compound["is_dismissed"] = len(variant_obj.get("dismiss_variant", [])) > 0
                for gene in variant_obj.get("genes", []):
                    gene_obj = {
                        "hgnc_id": gene["hgnc_id"],
                        "hgnc_symbol": gene.get("hgnc_symbol"),
                        "region_annotation": gene.get("region_annotation"),
                        "functional_annotation": gene.get("functional_annotation"),
                    }
                    gene_objs.append(gene_obj)
                    compound["genes"] = gene_objs

            compound["not_loaded"] = not_loaded
            compound_objs.append(compound)

        return compound_objs

    def update_compounds(self, variants):
        """Update the compounds for a set of variants.

        Args:
            variants(dict): A dictionary with _ids as keys and variant objs as values

        """
        LOG.debug("Updating compound objects")

        for var_id in variants:
            variant_obj = variants[var_id]
            if not variant_obj.get("compounds"):
                continue

            updated_compounds = self.update_variant_compounds(variant_obj, variants)
            variant_obj["compounds"] = updated_compounds

        LOG.debug("Compounds updated")

        return variants

    def update_mongo_compound_variants(self, bulk):
        """Update the compound information for a bulk of variants in the database

        Args:
            bulk(dict): {'_id': scout.models.Variant}

        """
        requests = []
        for var_id in bulk:
            var_obj = bulk[var_id]
            if not var_obj.get("compounds"):
                continue
            # Add a request to update compounds
            operation = pymongo.UpdateOne(
                {"_id": var_obj["_id"]}, {"$set": {"compounds": var_obj["compounds"]}}
            )
            requests.append(operation)

        if not requests:
            return

        try:
            self.variant_collection.bulk_write(requests, ordered=False)
        except BulkWriteError as err:
            LOG.warning("Updating compounds failed")
            raise err

    def update_case_compounds(self, case_obj, build="37"):
        """Update the compounds for a case

        Loop over all coding intervals to get coordinates for all potential compound positions.
        Update all variants within a gene with a bulk operation.
        """

        case_id = case_obj["_id"]
        # Possible categories 'snv', 'sv', 'str', 'cancer', 'cancer_sv'. Sort according to load order to ensure Cancer SNVs before
        # Cancer SVs, in particular, and keep a consistent variant_id collision resolution order.
        # Possible variant types are 'clinical', 'research'.
        load_variants = {
            (
                ORDERED_FILE_TYPE_MAP[file_type]["variant_type"],
                ORDERED_FILE_TYPE_MAP[file_type]["category"],
            )
            for file_type in ORDERED_FILE_TYPE_MAP
            if case_obj.get("vcf_files", {}).get(file_type)
        }

        coding_intervals = self.get_coding_intervals(build=build)
        # Loop over all intervals
        for chrom in CHROMOSOMES:
            intervals = coding_intervals.get(chrom, IntervalTree())
            for var_type, category in load_variants:
                LOG.info(
                    "Updating compounds on chromosome:{0}, type:{1}, category:{2} for case:{3}".format(
                        chrom, var_type, category, case_id
                    )
                )
                # Fetch all variants from a chromosome
                query = {"variant_type": var_type, "chrom": chrom}

                # Get all variants from the database of the specific type
                variant_objs = self.variants(
                    case_id=case_id,
                    query=query,
                    category=category,
                    nr_of_variants=-1,
                    sort_key="position",
                )

                # Initiate a bulk
                bulk = {}
                current_region = None
                special = False

                # Loop over the variants and check if they are in a coding region
                for var_obj in variant_objs:
                    var_id = var_obj["_id"]
                    var_chrom = var_obj["chromosome"]
                    var_start = var_obj["position"]
                    var_end = var_obj["end"] + 1

                    update_bulk = True
                    new_region = None

                    # Check if the variant is in a coding region
                    genomic_regions = coding_intervals.get(var_chrom, IntervalTree()).overlap(
                        var_start, var_end
                    )

                    # If the variant is in a coding region
                    if genomic_regions:
                        # We know there is data here so get the interval id
                        new_region = genomic_regions.pop().data

                    if new_region and (new_region == current_region):
                        # If the variant is in the same region as previous
                        # we add it to the same bulk
                        update_bulk = False

                    current_region = new_region

                    # If the variant is not in a current region we update the compounds
                    # from the previous region, if any. Otherwise continue
                    if update_bulk and bulk:
                        self.update_compounds(bulk)
                        self.update_mongo_compound_variants(bulk)
                        bulk = {}

                    if new_region:
                        bulk[var_id] = var_obj

                if not bulk:
                    continue

                self.update_compounds(bulk)
                self.update_mongo_compound_variants(bulk)

        LOG.info("All compounds updated")

    def load_variant(self, variant_obj):
        """Load a variant object

        Args:
            variant_obj(dict)

        Returns:
            inserted_id
        """
        # LOG.debug("Loading variant %s", variant_obj['_id'])
        try:
            result = self.variant_collection.insert_one(variant_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Variant %s already exists in database", variant_obj["_id"])
        return result

    def upsert_variant(self, variant_obj):
        """Load a variant object, if the object already exists update compounds.

        Args:
            variant_obj(dict)

        Returns:
            result
        """
        LOG.debug("Upserting variant %s", variant_obj["_id"])
        try:
            result = self.variant_collection.insert_one(variant_obj)
        except DuplicateKeyError as err:
            LOG.warning("Variant %s already exists in database - modifying", variant_obj["_id"])
            result = self.variant_collection.find_one_and_update(
                {"_id": variant_obj["_id"]},
                {"$set": {"compounds": variant_obj.get("compounds", [])}},
            )
        return result

    def load_variant_bulk(self, variants):
        """Load a bulk of variants

        Args:
            variants(iterable(scout.models.Variant))

        Returns:
            object_ids
        """
        if len(variants) == 0:
            return

        LOG.debug("Loading variant bulk")
        try:
            result = self.variant_collection.insert_many(variants)
        except (DuplicateKeyError, BulkWriteError) as err:
            # If the bulk write is wrong there are probably some variants already existing
            # In the database. So insert each variant
            LOG.warning("Bulk insertion failed - attempting separate variant upsert for this bulk")
            for var_obj in variants:
                try:
                    self.upsert_variant(var_obj)
                except IntegrityError as err:
                    pass

        return

    def _load_variants(
        self,
        variants: Iterable[cyvcf2.Variant],
        nr_variants: int,
        variant_type: str,
        case_obj: dict,
        individual_positions: dict,
        rank_threshold: int,
        institute_id: str,
        build: Optional[str] = None,
        rank_results_header: Optional[list] = None,
        vep_header: Optional[list] = None,
        category: str = "snv",
        sample_info: Optional[dict] = None,
        custom_images: Optional[dict] = None,
        local_archive_info: Optional[dict] = None,
        gene_to_panels: Optional[Dict[str, set]] = None,
        hgncid_to_gene: Optional[Dict[int, dict]] = None,
        genomic_intervals: Optional[Dict[str, IntervalTree]] = None,
    ) -> int:
        """This is the function that loops over the variants, parses them and builds the variant
        objects so they are ready to be inserted into the database.
        All variants with rank score above rank_threshold are loaded. All MT, pathogenic, managed or variants causative in other cases are also loaded.
        individual_positions refers to the order of samples in the VCF file. sample_info contains info about samples. It is used for instance to define tumor samples in cancer cases.
        local_archive_info contains info about the local archive used for annotation.
        """
        build = build or "37"

        start_insertion = datetime.now()
        start_five_thousand = datetime.now()

        # These are the number of variants that meet the criteria and gets inserted
        nr_inserted = 0
        # This is to keep track of blocks of inserted variants
        inserted = 1

        nr_bulks = 0

        # We want to load batches of variants to reduce the number of network round trips
        bulk = {}
        current_region = None

        LOG.info(f"Number of variants present on the VCF file:{nr_variants}")
        with progressbar(
            variants, label="Loading variants", length=nr_variants, file=sys.stdout
        ) as bar:
            for idx, variant in enumerate(bar):
                # All MT variants are loaded
                mt_variant = variant.CHROM in ["M", "MT"]
                rank_score = parse_rank_score(variant.INFO.get("RankScore"), case_obj["_id"])
                pathogenic = is_pathogenic(variant)
                managed = self._is_managed(variant, category)
                causative = self._is_causative_other_cases(variant, category)

                # Check if the variant should be loaded at all
                # if rank score is None means there are no rank scores annotated, all variants will be loaded
                # Otherwise we load all variants above a rank score treshold
                # Except for MT variants where we load all variants
                if (
                    (rank_score is None)
                    or (rank_score > rank_threshold)
                    or mt_variant
                    or pathogenic
                    or causative
                    or managed
                    or category in ["str"]
                ):
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
                        local_archive_info=local_archive_info,
                    )

                    # Build the variant object
                    variant_obj = build_variant(
                        variant=parsed_variant,
                        institute_id=institute_id,
                        gene_to_panels=gene_to_panels,
                        hgncid_to_gene=hgncid_to_gene,
                        sample_info=sample_info,
                    )

                    # Check if the variant is in a genomic region
                    var_chrom = variant_obj["chromosome"]
                    var_start = variant_obj["position"]
                    # We need to make sure that the interval has a length > 0
                    var_end = variant_obj["end"] + 1
                    var_id = variant_obj["_id"]
                    # If the bulk should be loaded or not
                    load = True
                    new_region = None

                    intervals = genomic_intervals.get(var_chrom, IntervalTree())
                    genomic_regions = intervals.overlap(var_start, var_end)

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
                    # Associate variant with image
                    if custom_images:
                        images = [
                            img
                            for img in custom_images
                            if img["str_repid"] == variant_obj["str_repid"]
                        ]
                        if len(images) > 0:
                            variant_obj["custom_images"] = images

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
                    if var_id in bulk:
                        LOG.warning(
                            "Duplicated variant %s detected in same bulk. Attempting separate upsert.",
                            variant_obj.get("simple_id"),
                        )
                        try:
                            self.upsert_variant(variant_obj)
                        except IntegrityError as err:
                            pass
                    else:
                        bulk[var_id] = variant_obj

                    if nr_variants != 0 and nr_variants % 5000 == 0:
                        LOG.info("%s variants parsed", str(nr_variants))
                        LOG.info(
                            "Time to parse variants: %s",
                            (datetime.now() - start_five_thousand),
                        )
                        start_five_thousand = datetime.now()

                    if nr_inserted != 0 and (nr_inserted * inserted) % (1000 * inserted) == 0:
                        LOG.info("%s variants inserted", nr_inserted)
                        inserted += 1

        # If the variants are in a coding region we update the compounds
        if current_region:
            self.update_compounds(bulk)

        # Load the final variant bulk
        self.load_variant_bulk(list(bulk.values()))
        nr_bulks += 1
        LOG.info(
            "All variants inserted, time to insert variants: {0}".format(
                datetime.now() - start_insertion
            )
        )

        LOG.info("Nr variants parsed: %s", nr_variants)
        LOG.info("Nr variants inserted: %s", nr_inserted)
        LOG.debug("Nr bulks inserted: %s", nr_bulks)

        return nr_inserted

    def _is_causative_other_cases(
        self,
        variant: cyvcf2.Variant,
        category: str = "snv",
        build: str = "37",
    ) -> bool:
        """Check if variant is on the list of causatives from other cases, also from other institutes.
        All variants that have been marked causative will be loaded, even if the other case does not exist anymore, or has been reclassified.
        """

        coordinates = parse_coordinates(variant, category, build)

        variant_prefix = parse_simple_id(
            coordinates["chrom"],
            str(coordinates["position"]),
            coordinates["ref"],
            coordinates["alt"],
        )
        clinical_variant = "".join([variant_prefix, "_clinical"])
        research_variant = "".join([variant_prefix, "_research"])

        var_causative_events_count = len(
            list(
                self.event_collection.find(
                    {
                        "verb": {"$in": ["mark_causative", "mark_partial_causative"]},
                        "category": "variant",
                        "subject": {"$in": [clinical_variant, research_variant]},
                    }
                )
            )
        )
        return var_causative_events_count > 0

    def _is_managed(
        self,
        variant: cyvcf2.Variant,
        category: str = "snv",
        build: str = "37",
    ) -> bool:
        """Check if variant is on the managed list.
        All variants on the list will be loaded regardless of the kind of relevance.

        Returns true if variant is matched with a variant on the managed list.
        """

        coordinates = parse_coordinates(variant, category, build)

        return (
            self.find_managed_variant(
                parse_managed_variant_id(
                    coordinates["chrom"],
                    coordinates["position"],
                    coordinates["ref"],
                    coordinates["alt"],
                    category,
                    coordinates["sub_category"],
                    build,
                )
            )
            is not None
        )

    def _has_variants_in_file(self, variant_file: str) -> bool:
        """Check if variant file has any variants."""
        try:
            vcf_obj = VCF(variant_file)
            var = next(vcf_obj)
            return True
        except StopIteration as err:
            LOG.warning("Variant file %s does not include any variants", variant_file)
            return False

    def load_variants(
        self,
        case_obj: dict,
        variant_type: str = "clinical",
        category: str = "snv",
        rank_threshold: float = None,
        chrom: str = None,
        start: int = None,
        end: int = None,
        gene_obj: dict = None,
        custom_images: list = None,
        build: str = "37",
    ):
        """Load variants for a case into scout.

        Load the variants for a specific analysis type and category into scout.
        If no region is specified, load all variants above rank score threshold
        If region or gene is specified, load all variants from that region
        disregarding variant rank(if not specified)

        Args:
            case_obj(dict): A case from the scout database
            variant_type(str): 'clinical' or 'research'. Default: 'clinical'
            category(str): 'snv', 'str' or 'sv'. Default: 'snv'
            rank_threshold(float): Only load variants above this score. Default: 0
            chrom(str): Load variants from a certain chromosome
            start(int): Specify the start position
            end(int): Specify the end position
            gene_obj(dict): A gene object from the database

        Returns:
            nr_inserted(int)
        """
        institute_id = case_obj["owner"]

        nr_inserted = 0

        gene_to_panels = self.gene_to_panels(case_obj)
        genes = list(self.all_genes(build=build))
        hgncid_to_gene = self.hgncid_to_gene(genes=genes, build=build)
        genomic_intervals = self.get_coding_intervals(genes=genes, build=build)

        for vcf_file_key, vcf_dict in ORDERED_FILE_TYPE_MAP.items():
            if vcf_dict["variant_type"] != variant_type:
                continue
            if vcf_dict["category"] != category:
                continue

            variant_file = (
                case_obj["vcf_files"].get(vcf_file_key) if case_obj.get("vcf_files") else None
            )

            if variant_file:
                LOG.info(f"Loading {vcf_file_key} variants")
            else:
                continue

            if not self._has_variants_in_file(variant_file):
                LOG.warning(
                    f"File '{variant_file}' not found on disk. Please update case {case_obj['_id']} with a valid file path for the {category} variant category ."
                )
                continue

            vcf_obj = VCF(variant_file)

            # Parse the necessary headers from vcf file
            rank_results_header = parse_rank_results_header(vcf_obj)

            local_archive_info = parse_local_archive_header(vcf_obj)

            vep_header = parse_vep_header(vcf_obj)
            if vep_header:
                LOG.debug("Found VEP header %s", "|".join(vep_header))

            # This is a dictionary to tell where ind are in vcf
            individual_positions = {ind: i for i, ind in enumerate(vcf_obj.samples)}

            # Dictionary for cancer analysis
            sample_info = {}
            if category in ("cancer", "cancer_sv"):
                for ind in case_obj["individuals"]:
                    if ind["phenotype"] == 2:
                        sample_info[ind["individual_id"]] = "case"
                    else:
                        sample_info[ind["individual_id"]] = "control"

            # Check if a region should be uploaded
            region = ""
            if gene_obj:
                chrom = gene_obj["chromosome"]
                # Add same padding as VEP
                start = max(gene_obj["start"] - 5000, 0)
                end = gene_obj["end"] + 5000
            if chrom:
                # We want to load all variants in the region regardless of rank score
                rank_threshold = rank_threshold or -1000
                if not (start and end):
                    raise SyntaxError("Specify chrom start and end")
                region = "{0}:{1}-{2}".format(chrom, start, end)
            else:
                rank_threshold = rank_threshold or 0

            nr_variants = sum(1 for _ in vcf_obj(region))
            vcf_obj = VCF(variant_file)

            try:
                nr_inserted = self._load_variants(
                    variants=vcf_obj(region),
                    nr_variants=nr_variants,
                    variant_type=variant_type,
                    case_obj=case_obj,
                    individual_positions=individual_positions,
                    rank_threshold=rank_threshold,
                    institute_id=institute_id,
                    build=build,
                    rank_results_header=rank_results_header,
                    vep_header=vep_header,
                    category=category,
                    sample_info=sample_info,
                    custom_images=custom_images,
                    local_archive_info=local_archive_info,
                    gene_to_panels=gene_to_panels,
                    hgncid_to_gene=hgncid_to_gene,
                    genomic_intervals=genomic_intervals,
                )
            except Exception as error:
                LOG.exception("unexpected error")
                LOG.warning("Deleting inserted variants")
                self.delete_variants(case_obj["_id"], variant_type)
                raise error

        if nr_inserted:
            self.update_variant_rank(case_obj, variant_type, category=category)

        return nr_inserted
