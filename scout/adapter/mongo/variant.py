# -*- coding: utf-8 -*-
# stdlib modules
import logging
import pathlib
import re
import tempfile
from datetime import datetime
from pprint import pprint as pp

# Third party modules
import pymongo
from cyvcf2 import VCF
from intervaltree import IntervalTree
from pymongo.errors import BulkWriteError, DuplicateKeyError

from scout.build import build_variant
from scout.exceptions import IntegrityError
from scout.parse.variant import parse_variant

# Local modules
from scout.parse.variant.rank_score import parse_rank_score
from scout.utils.coordinates import is_par

from .variant_loader import VariantLoader

LOG = logging.getLogger(__name__)


class VariantHandler(VariantLoader):

    """Methods to handle variants in the mongo adapter"""

    def add_gene_info(self, variant_obj, gene_panels=None, build=None):
        """Add extra information about genes from gene panels

        Args:
            variant_obj(dict): A variant from the database
            gene_panels(list(dict)): List of panels from database
            build(str): chromosome build 37 or 38
        """
        gene_panels = gene_panels or []

        # Add a variable that checks if there are any refseq transcripts
        variant_obj["has_refseq"] = False
        # We need to check if there are any additional information in the gene panels

        # extra_info will hold information from gene panels
        # Collect all extra info from the panels in a dictionary with hgnc_id as keys
        extra_info = {}
        for panel_obj in gene_panels:
            for gene_info in panel_obj["genes"]:
                hgnc_id = gene_info["hgnc_id"]
                if hgnc_id not in extra_info:
                    extra_info[hgnc_id] = []

                extra_info[hgnc_id].append(gene_info)

        # Loop over the genes in the variant object to add information
        # from hgnc_genes and panel genes to the variant object
        for variant_gene in variant_obj.get("genes", []):
            hgnc_id = variant_gene["hgnc_id"]
            # Get the hgnc_gene
            hgnc_gene = self.hgnc_gene(hgnc_id, build)

            if not hgnc_gene:
                continue

            # Create a dictionary with transcripts information
            # Use ensembl transcript id as keys
            transcripts_dict = {}
            # Add transcript information from the hgnc gene
            for transcript in hgnc_gene.get("transcripts", []):
                tx_id = transcript["ensembl_transcript_id"]
                transcripts_dict[tx_id] = transcript

            # Add the transcripts to the gene object
            hgnc_gene["transcripts_dict"] = transcripts_dict

            if hgnc_gene.get("incomplete_penetrance"):
                variant_gene["omim_penetrance"] = True

            ############# PANEL SPECIFIC INFORMATION #############
            # Panels can have extra information about genes and transcripts
            panel_info = extra_info.get(hgnc_id, [])

            # Manually annotated disease associated transcripts
            disease_associated = set()
            # We need to strip the version to compare against others
            disease_associated_no_version = set()
            manual_penetrance = False
            mosaicism = False
            manual_inheritance = set()

            # We need to loop since there can be information from multiple panels
            for gene_info in panel_info:
                # Check if there are manually annotated disease transcripts
                for tx in gene_info.get("disease_associated_transcripts", []):
                    # We remove the version of transcript at this stage
                    stripped = re.sub(r"\.[0-9]", "", tx)
                    disease_associated_no_version.add(stripped)
                    disease_associated.add(tx)

                if gene_info.get("reduced_penetrance"):
                    manual_penetrance = True

                if gene_info.get("mosaicism"):
                    mosaicism = True

                manual_inheritance.update(gene_info.get("inheritance_models", []))

            variant_gene["disease_associated_transcripts"] = list(disease_associated)
            variant_gene["manual_penetrance"] = manual_penetrance
            variant_gene["mosaicism"] = mosaicism
            variant_gene["manual_inheritance"] = list(manual_inheritance)

            # Now add the information from hgnc and panels
            # to the transcripts on the variant

            # First loop over the variants transcripts
            for transcript in variant_gene.get("transcripts", []):
                tx_id = transcript["transcript_id"]
                if not tx_id in transcripts_dict:
                    continue

                # This is the common information about the transcript
                hgnc_transcript = transcripts_dict[tx_id]

                # Check in the common information if it is a primary transcript
                if hgnc_transcript.get("is_primary"):
                    transcript["is_primary"] = True
                # If the transcript has a ref seq identifier we add that
                # to the variants transcript
                if not hgnc_transcript.get("refseq_id"):
                    continue

                refseq_id = hgnc_transcript["refseq_id"]
                transcript["refseq_id"] = refseq_id
                variant_obj["has_refseq"] = True
                # Check if the refseq id are disease associated
                if refseq_id in disease_associated_no_version:
                    transcript["is_disease_associated"] = True

                # Since a ensemble transcript can have multiple refseq identifiers we add all of
                # those
                transcript["refseq_identifiers"] = hgnc_transcript.get("refseq_identifiers", [])

            variant_gene["common"] = hgnc_gene
            # Add the associated disease terms
            variant_gene["disease_terms"] = self.disease_terms(hgnc_id)

        return variant_obj

    def variants(
        self,
        case_id,
        query=None,
        variant_ids=None,
        category="snv",
        nr_of_variants=10,
        skip=0,
        sort_key="variant_rank",
        build="37",
    ):
        """Returns variants specified in question for a specific case.

        If skip not equal to 0 skip the first n variants.

        Arguments:
            case_id(str): A string that represents the case
            query(dict): A dictionary with querys for the database
            variant_ids(List[str])
            category(str): 'sv', 'str', 'snv', 'cancer' or 'cancer_sv'
            nr_of_variants(int): if -1 return all variants
            skip(int): How many variants to skip
            sort_key: ['variant_rank', 'rank_score', 'position']
            build(str): genome build
        Returns:
             pymongo.cursor
        """
        LOG.debug("Fetching variants from {0}".format(case_id))

        if variant_ids:
            nr_of_variants = len(variant_ids)

        elif nr_of_variants == -1:
            nr_of_variants = 0  # This will return all variants

        else:
            nr_of_variants = skip + nr_of_variants

        mongo_query = self.build_query(
            case_id,
            query=query,
            variant_ids=variant_ids,
            category=category,
            build=build,
        )
        sorting = []
        if sort_key == "variant_rank":
            sorting = [("variant_rank", pymongo.ASCENDING)]
        if sort_key == "rank_score":
            sorting = [("rank_score", pymongo.DESCENDING)]
        if sort_key == "position":
            sorting = [("position", pymongo.ASCENDING)]

        result = self.variant_collection.find(mongo_query, skip=skip, limit=nr_of_variants).sort(
            sorting
        )

        return result

    def count_variants(self, case_id, query, variant_ids, category):
        """Returns number of variants

        Arguments:
            case_id(str): A string that represents the case
            query(dict): A dictionary with querys for the database
            variant_ids(List[str])
            category(str): 'sv', 'str', 'snv', 'cancer' or 'cancer_sv'

        Returns:
             integer
        """

        query = self.build_query(case_id, query=query, variant_ids=variant_ids, category=category)
        return self.variant_collection.count_documents(query)

    def sanger_variants(self, institute_id=None, case_id=None):
        """Return all variants with sanger information

        Args:
            institute_id(str)
            case_id(str)

        Returns:
            res(pymongo.Cursor): A Cursor with all variants with sanger activity
        """
        query = {"validation": {"$exists": True}}
        if institute_id:
            query["institute_id"] = institute_id
        if case_id:
            query["case_id"] = case_id

        return self.variant_collection.find(query)

    def variant(
        self,
        document_id=None,
        gene_panels=None,
        case_id=None,
        simple_id=None,
        variant_type="clinical",
    ):
        """Returns the specified variant.

        Args:
            document_id : A md5 key that represents the variant or "variant_id"
            gene_panels(List[GenePanel])
            case_id (str): case id (will search with "variant_id")
            simple_id (str): a variant simple_id (example: 1_161184089_G_GTA)
            variant_type(str): 'research' or 'clinical' - default 'clinical'

        Returns:
            variant_object(Variant): A odm variant object
        """
        query = {}
        if case_id and document_id:
            # search for a variant in a case by variant_id
            query["case_id"] = case_id
            query["variant_id"] = document_id
        elif case_id and simple_id:
            # search for a variant in a case by its simple_id
            query["case_id"] = case_id
            query["simple_id"] = simple_id
            query["variant_type"] = variant_type
        else:
            # search with a unique id
            query["_id"] = document_id

        variant_obj = self.variant_collection.find_one(query)
        if not variant_obj:
            return variant_obj
        case_obj = self.case(case_id=variant_obj["case_id"])

        if case_obj:
            variant_obj = self.add_gene_info(
                variant_obj=variant_obj,
                gene_panels=gene_panels,
                build=case_obj["genome_build"],
            )
        else:
            variant_obj = self.add_gene_info(variant_obj=variant_obj, gene_panels=gene_panels)

        if variant_obj["chromosome"] in ["X", "Y"]:
            # TO DO add the build here
            variant_obj["is_par"] = is_par(variant_obj["chromosome"], variant_obj["position"])

        return variant_obj

    def overlapping_sv_variant(self, case_id, variant_obj):
        """Returns a SV for a case that is as similar as possible to a SV from another case

        Args:
            case_id (str): case id for the variant query
            variant_obj (dict): a variant dictionary from another case

        Returns:
            hit (Variant): a variant object dictionary
        """
        coordinate_query = self.sv_coordinate_query(
            {
                "chrom": variant_obj["chromosome"],
                "start": variant_obj["position"],
                "end": variant_obj["end"],
            }
        )
        query = {
            "case_id": case_id,
            "category": variant_obj["category"],  # sv
            "variant_type": variant_obj["variant_type"],  # clinical or research
            "sub_category": variant_obj["sub_category"],  # example -> "del"
            "$and": coordinate_query["$and"],  # query for overlapping SV variants
        }

        overlapping_svs = list(
            self.variant_collection.find(
                query,
            )
        )
        if not overlapping_svs:
            return None
        if len(overlapping_svs) == 1:
            return overlapping_svs[0]

        # If more than one SV is overlapping with this variant
        # return the one with most similar size
        query_size = variant_obj["length"]
        hit_lengths = [hit["length"] for hit in overlapping_svs]
        closest_length = min(hit_lengths, key=lambda x: abs(x - query_size))

        # return the variant with the closes size
        for hit in overlapping_svs:
            if hit["length"] == closest_length:
                return hit

    def gene_variants(
        self,
        query=None,
        category="snv",
        variant_type=["clinical"],
        institute_id=None,
        nr_of_variants=50,
        skip=0,
    ):
        """Return all variants seen in a given gene.

        If skip not equal to 0 skip the first n variants.

        Args:
            query(dict): A dictionary with querys for the database, including
            variant_type: 'clinical', 'research'
            category(str): 'sv', 'str', 'snv', 'cancer' or 'cancer_sv'
            institute_id: institute ID (required for similarity query)
            nr_of_variants(int): if -1 return all variants
            skip(int): How many variants to skip

        Query can contain:
            phenotype_terms,
            phenotype_groups,
            similar_case,
            cohorts
        """
        mongo_variant_query = self.build_variant_query(
            query=query,
            institute_id=institute_id,
            category=category,
            variant_type=variant_type,
        )

        sorting = [("rank_score", pymongo.DESCENDING)]

        if nr_of_variants == -1:
            nr_of_variants = 0  # This will return all variants
        else:
            nr_of_variants = skip + nr_of_variants

        result = (
            self.variant_collection.find(mongo_variant_query)
            .sort(sorting)
            .skip(skip)
            .limit(nr_of_variants)
        )

        return result

    def count_gene_variants(
        self, query=None, category="snv", variant_type=["clinical"], institute_id=None
    ):
        """Count all variants seen in a given gene.

        Args:
            query(dict): A dictionary with querys for the database, including
            variant_type: 'clinical', 'research'
            category(str): 'sv', 'str', 'snv', 'cancer' or 'cancer_sv'
            institute_id: institute ID (required for similarity query)

        Query can contain:
            phenotype_terms,
            phenotype_groups,
            similar_case,
            cohorts

        Returns:
            Number of variants for gene
        """
        mongo_variant_query = self.build_variant_query(
            query=query,
            institute_id=institute_id,
            category=category,
            variant_type=variant_type,
        )

        return self.variant_collection.count_documents(mongo_variant_query)

    def verified(self, institute_id):
        """Return all verified variants for a given institute

        Args:
            institute_id(str): institute id

        Returns:
            res(list): a list with validated variants
        """
        query = {"verb": "validate", "institute": institute_id}
        res = []
        validate_events = self.event_collection.find(query)
        for validated in list(validate_events):
            case_id = validated["case"]
            var_obj = self.variant(case_id=case_id, document_id=validated["variant_id"])
            case_obj = self.case(case_id=case_id)
            if not case_obj or not var_obj:
                continue  # Take into account that stuff might have been removed from database
            var_obj["case_obj"] = {
                "display_name": case_obj["display_name"],
                "individuals": case_obj["individuals"],
            }
            res.append(var_obj)

        return res

    def get_causatives(self, institute_id, case_id=None):
        """Return all causative variants for an institute

        Args:
            institute_id(str)
            case_id(str)

        Yields:
            str: variant document id
        """

        causatives = []

        if case_id:

            case_obj = self.case_collection.find_one({"_id": case_id})
            causatives = [causative for causative in case_obj.get("causatives", [])]

        elif institute_id:

            query = self.case_collection.aggregate(
                [
                    {
                        "$match": {
                            "collaborators": institute_id,
                            "causatives": {"$exists": True},
                        }
                    },
                    {"$unwind": "$causatives"},
                    {"$group": {"_id": "$causatives"}},
                ]
            )
            causatives = [item["_id"] for item in query]

        return causatives

    def check_managed(self, case_obj=None, institute_obj=None, limit_genes=None):
        """Check if there are any variants in case that match a managed variant.

            Given a case, limit search to affected individuals.

        Args:
            case_obj (dict): A Case object
            institute_obj (dict): check across the whole institute
            limit_genes (list): list of gene hgnc_ids to limit the search to

        Returns:
            managed_variants(iterable(Variant))
        """

        institute_id = case_obj["owner"] if case_obj else institute_obj["_id"]

        positional_variant_ids = self.get_managed_variants(institute_id)

        if len(positional_variant_ids) == 0:
            return []

        return self.match_affected_gt(case_obj, institute_obj, positional_variant_ids, limit_genes)

    def _find_affected(self, case_obj):
        """Internal method to find affected individuals.

        Assumes an affected individual has phenotype == 2

        Args:
            case_obj (dict): A Case object

        Returns:
            affected (list): a list of affected IDs.
        """

        # affected is phenotype == 2; assume
        affected_ids = []
        if case_obj:
            for subject in case_obj.get("individuals"):
                if subject.get("phenotype") == 2:
                    affected_ids.append(subject.get("individual_id"))

        return affected_ids

    def match_affected_gt(self, case_obj, institute_obj, positional_variant_ids, limit_genes):
        """Match positional_variant_ids against variants from affected individuals
        in a case, ensuring that they at least are carriers.

        Args:
            case_obj (dict): A Case object.
            institute_obj (dict): An Institute object.
            positional_variant_ids (iterable): A set of possible positional variant ids to look for
            limit_genes (list): list of gene hgnc_ids to limit the search to

        Returns:
            causatives(iterable(Variant))
        """

        if len(positional_variant_ids) == 0:
            return []

        filters = {"variant_id": {"$in": list(positional_variant_ids)}}
        if case_obj:
            affected_ids = self._find_affected(case_obj)
            if len(affected_ids) == 0:
                return []

            filters["case_id"] = case_obj["_id"]
            filters["samples"] = {
                "$elemMatch": {
                    "sample_id": {"$in": affected_ids},
                    "genotype_call": {"$regex": "1"},
                }
            }
        else:
            filters["institute"] = institute_obj["_id"]
        if limit_genes:
            filters["genes.hgnc_id"] = {"$in": limit_genes}

        LOG.debug("Attempting filtered matching causatives query: %s", filters)
        return self.variant_collection.find(filters)

    def check_causatives(self, case_obj=None, institute_obj=None, limit_genes=None):
        """Check if there are any variants that are previously marked causative

        Loop through all variants that are marked 'causative' for an
        institute and check if any of the variants are present in the
        current case.

        Args:
            case_obj (dict): A Case object
            institute_obj (dict): check across the whole institute
            limit_genes (list): list of gene hgnc_ids to limit the search to

        Returns:
            causatives(iterable(Variant))
        """
        institute_id = case_obj["owner"] if case_obj else institute_obj["_id"]
        var_causative_events = self.event_collection.find(
            {"institute": institute_id, "verb": "mark_causative", "category": "variant"}
        )
        positional_variant_ids = set()
        for var_event in var_causative_events:
            if case_obj and var_event["case"] == case_obj["_id"]:
                # exclude causatives from the same case
                continue
            other_case = self.case(var_event["case"])
            if other_case is None:
                # Other variant belongs to a case that doesn't exist any more
                continue
            other_link = var_event["link"]
            # link contains other variant ID
            other_causative_id = other_link.split("/")[-1]

            if other_causative_id in other_case.get("causatives", []):
                positional_variant_ids.add(var_event["variant_id"])

        return self.match_affected_gt(case_obj, institute_obj, positional_variant_ids, limit_genes)

    def other_causatives(self, case_obj, variant_obj):
        """Find the same variant marked causative in other cases.

        Should not yield the same variant multiple times if a variant has been marked causative multiple times, and still
        is causative for the case.

        Args:
            case_obj(dict)
            variant_obj(dict)

        Yields:
            other_causative(dict)
        """
        # variant id without "*_[variant_type]"
        variant_prefix = variant_obj["simple_id"]
        clinical_variant = "".join([variant_prefix, "_clinical"])
        research_variant = "".join([variant_prefix, "_research"])

        var_causative_events = self.event_collection.find(
            {
                "verb": "mark_causative",
                "subject": {"$in": [clinical_variant, research_variant]},
                "category": "variant",
            }
        )

        yielded_other_causative_ids = []
        for var_event in var_causative_events:
            if var_event["case"] == case_obj["_id"]:
                # This is the variant the search started from, do not collect it
                continue
            other_case = self.case(var_event["case"])
            if other_case is None:
                # Other variant belongs to a case that doesn't exist any more
                continue
            if variant_obj["institute"] not in other_case.get("collaborators"):
                # User doesn't have access to this case/variant
                continue

            other_link = var_event["link"]
            # link contains other variant ID
            other_causative_id = other_link.split("/")[-1]
            if other_causative_id in yielded_other_causative_ids:
                continue

            other_case_causatives = other_case.get("causatives", [])
            if other_causative_id in other_case_causatives:
                other_causative = {
                    "_id": other_causative_id,
                    "institute_id": other_case["owner"],
                    "case_id": other_case["_id"],
                    "case_display_name": other_case["display_name"],
                }
                yielded_other_causative_ids.append(other_causative_id)
                yield other_causative

    def delete_variants(self, case_id, variant_type, category=None):
        """Delete variants of one type for a case

        This is used when a case is reanalyzed

        Args:
            case_id(str): The case id
            variant_type(str): 'research' or 'clinical'
            category(str): 'snv', 'sv', 'cancer' or 'cancer_sv'
        """
        category = category or ""
        LOG.info(
            "Deleting old {0} {1} variants for case {2}".format(variant_type, category, case_id)
        )
        query = {"case_id": case_id, "variant_type": variant_type}
        if category:
            query["category"] = category
        result = self.variant_collection.delete_many(query)
        LOG.info("{0} variants deleted".format(result.deleted_count))

    def overlapping(self, variant_obj):
        """Return overlapping variants.

        Look at the genes that a variant overlaps to.
        Then return all variants that overlap these genes.

        If variant_obj is sv it will return the overlapping snvs and oposite
        There is a problem when SVs are huge since there are to many overlapping variants.

        Args:
            variant_obj(dict)

        Returns:
            variants(iterable(dict))
        """
        # This is the category of the variants that we want to collect
        category = "snv" if variant_obj["category"] == "sv" else "sv"
        variant_type = variant_obj.get("variant_type", "clinical")
        hgnc_ids = variant_obj["hgnc_ids"]

        query = {
            "$and": [
                {"case_id": variant_obj["case_id"]},
                {"category": category},
                {"variant_type": variant_type},
                {"hgnc_ids": {"$in": hgnc_ids}},
            ]
        }
        sort_key = [("rank_score", pymongo.DESCENDING)]
        # We collect the 30 most severe overlapping variants
        variants = self.variant_collection.find(query).sort(sort_key).limit(30)

        return variants

    def evaluated_variants(self, case_id):
        """Returns variants that have been evaluated

        Return all variants, snvs/indels and svs from case case_id
        which have a entry for 'acmg_classification', 'manual_rank', 'dismiss_variant',
        'cancer_tier' or if they are commented.

        Args:
            case_id(str)

        Returns:
            variants(iterable(Variant))
        """
        # Get all variants that have been evaluated in some way for a case
        query = {
            "$and": [
                {"case_id": case_id},
                {
                    "$or": [
                        {"acmg_classification": {"$exists": True}},
                        {"manual_rank": {"$exists": True}},
                        {"cancer_tier": {"$exists": True}},
                        {"dismiss_variant": {"$exists": True}},
                        {"mosaic_tags": {"$exists": True}},
                    ]
                },
            ]
        }

        # Collect the result in a dictionary
        variants = {}
        case_obj = self.case(case_id=case_id)  # case exists since it's used in the query above
        for var in self.variant_collection.find(query):
            variants[var["variant_id"]] = self.add_gene_info(
                variant_obj=var, build=case_obj["genome_build"]
            )

        # Collect all variant comments from the case
        event_query = {"$and": [{"case": case_id}, {"category": "variant"}, {"verb": "comment"}]}

        # Get all variantids for commented variants
        comment_variants = {
            event["variant_id"] for event in self.event_collection.find(event_query)
        }

        # Get the variant objects for commented variants, if they exist
        for var_id in comment_variants:
            # Skip if we already added the variant
            if var_id in variants:
                continue
            # Get the variant with variant_id (not _id!)
            variant_obj = self.variant(var_id, case_id=case_id)

            # There could be cases with comments that refers to non existing variants
            # if a case has been reanalysed
            if not variant_obj:
                continue

            variant_obj["is_commented"] = True
            variants[var_id] = variant_obj

        # Return a list with the variant objects
        return variants.values()

    def get_region_vcf(
        self,
        case_obj,
        chrom=None,
        start=None,
        end=None,
        gene_obj=None,
        variant_type="clinical",
        category="snv",
        rank_threshold=None,
    ):
        """Produce a reduced vcf with variants from the specified coordinates
           This is used for the alignment viewer.

        Args:
            case_obj(dict): A case from the scout database
            variant_type(str): 'clinical' or 'research'. Default: 'clinical'
            category(str): 'snv' or 'sv'. Default: 'snv'
            rank_threshold(float): Only load variants above this score. Default: 5
            chrom(str): Load variants from a certain chromosome
            start(int): Specify the start position
            end(int): Specify the end position
            gene_obj(dict): A gene object from the database

        Returns:
            file_name(str): Path to the temporary file
        """
        rank_threshold = rank_threshold or -100

        variant_file = None
        if variant_type == "clinical":
            if category == "snv":
                variant_file = case_obj["vcf_files"].get("vcf_snv")
            elif category == "sv":
                variant_file = case_obj["vcf_files"].get("vcf_sv")
            elif category == "str":
                variant_file = case_obj["vcf_files"].get("vcf_str")
            elif category == "cancer":
                variant_file = case_obj["vcf_files"].get("vcf_cancer")
        elif variant_type == "research":
            if category == "snv":
                variant_file = case_obj["vcf_files"].get("vcf_snv_research")
            elif category == "sv":
                variant_file = case_obj["vcf_files"].get("vcf_sv_research")

        if not variant_file:
            raise FileNotFoundError("VCF file does not seem to exist")

        try:
            vcf_obj = VCF(variant_file)
        except Exception:
            raise FileNotFoundError(
                "Could not access {}. The file is missing or malformed".format(variant_file)
            )

        region = ""

        if gene_obj:
            chrom = gene_obj["chromosome"]
            start = gene_obj["start"]
            end = gene_obj["end"]

        if chrom:
            if start and end:
                region = "{0}:{1}-{2}".format(chrom, start, end)
            else:
                region = "{0}".format(chrom)

        else:
            rank_threshold = rank_threshold or 5

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
            file_name = str(pathlib.Path(temp.name))
            for header_line in vcf_obj.raw_header.split("\n"):
                if len(header_line) > 3:
                    temp.write(header_line + "\n")
            try:
                for variant in vcf_obj(region):
                    temp.write(str(variant))
            except Exception:
                raise FileNotFoundError("Could not find index for {}".format(variant_file))

        return file_name

    def case_variants_count(self, case_id, institute_id, variant_type=None, force_update_case=True):
        """Returns the sum of all variants for a case by type

        Args:
            case_id(str): _id of a case
            institute_id(str): id of an institute
            variant_type(str): "clinical" or "research"
            force_update_case(bool): whether the case document should be updated with these stats

        Returns:
            variants_by_type(dict). A dictionary like this:
                {
                    "clinical": {
                        "snv": 789, (or "cancer")
                        "sv": 63 (or "cancer-sv")
                    },
                    "research":{
                        "snv": 789, (or "cancer")
                        "sv": 63 (or "cancer-sv")
                    }
                }
        """
        LOG.info(
            "Retrieving variants by category for case: {0}, institute: {1}".format(
                case_id, institute_id
            )
        )

        case_obj = self.case(case_id=case_id)
        variants_stats = case_obj.get("variants_stats") or {}

        # if case has stats and no update is needed, return variant count
        if variant_type and variant_type in variants_stats and force_update_case is False:
            return case_obj["variants_stats"]

        # Update case variant stats
        match = {"$match": {"case_id": case_id, "institute": institute_id}}
        group = {
            "$group": {
                "_id": {"type": "$variant_type", "category": "$category"},
                "total": {"$sum": 1},
            }
        }
        pipeline = [match, group]
        results = self.variant_collection.aggregate(pipeline)

        variants_by_type = {}
        for item in results:
            var_type = item["_id"]["type"]
            var_category = item["_id"]["category"]
            # classify by type (clinical or research)
            if var_type in variants_by_type:
                # classify by category (snv, sv, str, cancer, cancer-sv)
                variants_by_type[var_type][var_category] = item["total"]
            else:
                variants_by_type[var_type] = {var_category: item["total"]}

        case_obj["variants_stats"] = variants_by_type
        self.update_case(case_obj=case_obj, keep_date=True)

        return variants_by_type

    def sample_variants(self, variants, sample_name, category="snv"):
        """Given a list of variants get variant objects found in a specific patient

        Args:
            variants(list): a list of variant ids
            sample_name(str): a sample display name
            category(str): 'snv', 'sv' ..

        Returns:
            result(iterable(Variant))
        """
        LOG.info("Retrieving variants for subject : {0}".format(sample_name))
        has_allele = re.compile(
            "1|2"
        )  # a non wild-type allele is called at least once in this sample

        query = {
            "$and": [
                {"_id": {"$in": variants}},
                {"category": category},
                {
                    "samples": {
                        "$elemMatch": {
                            "display_name": sample_name,
                            "genotype_call": {"$regex": has_allele},
                        }
                    }
                },
            ]
        }

        result = self.variant_collection.find(query)
        return result
