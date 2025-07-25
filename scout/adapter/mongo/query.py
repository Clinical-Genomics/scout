import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional, Union

from scout.constants import (
    CLINSIG_MAP,
    FUNDAMENTAL_CRITERIA,
    PRIMARY_CRITERIA,
    SECONDARY_CRITERIA,
    SPIDEX_HUMAN,
    TRUSTED_REVSTAT_LEVEL,
)

CLNSIG_NOT_EXISTS = {"clnsig": {"$exists": False}}
CLNSIG_ONC_NOT_EXISTS = {"clnsig_onc": {"$exists": False}}
CLNSIG_NULL = {"clnsig": {"$eq": None}}
CLNSIG_ONC_NULL = {"clnsig_onc": {"$eq": None}}
CRITERION_EXCLUDE_OPERATOR = {False: "$in", True: "$nin"}
EXISTS = {"$exists": True}
NOT_EXISTS = {"$exists": False}
EXISTS_NOT_NULL = {"$exists": True, "$ne": None}

LOG = logging.getLogger(__name__)


class QueryHandler(object):
    def build_case_query(
        self,
        case_ids: Optional[List[str]],
        institute_id: Optional[List[str]],
        status: Optional[List[str]],
        older_than: Optional[int],
        analysis_type: Optional[List[str]],
    ) -> dict:
        """Build case query based on case id, status and analysis date."""
        case_query = {}
        if case_ids:
            case_query["_id"] = {"$in": case_ids}
        if institute_id:
            case_query["owner"] = institute_id
        if analysis_type:
            case_query["individuals.analysis_type"] = {"$in": analysis_type}
        if older_than:
            older_than_date = datetime.now() - timedelta(weeks=older_than * 4)  # 4 weeks in a month
            case_query["analysis_date"] = {"$lt": older_than_date}
        if status:
            case_query["status"] = {"$in": list(status)}

        return case_query

    def delete_variants_query(
        self,
        case_id: str,
        variants_to_keep: List[str] = [],
        min_rank_threshold: Optional[int] = None,
        keep_ctg: List[str] = [],
    ) -> dict:
        """Build a query to delete variants from a case (variant collection).

        Removes variants with rank lower than `min_rank_threshold`.
        Retains variants in categories `keep_ctg` by excluding them from deletion - eg `["cancer", "cancer_sv"]`.
        """
        variants_query = {}
        case_subquery = {"case_id": case_id}

        # Create query to delete all variants that shouldn't be kept or with rank higher than min_rank_threshold
        if variants_to_keep or min_rank_threshold or keep_ctg:
            variants_query["$and"] = [case_subquery]
            if variants_to_keep:
                variants_query["$and"].append({"_id": {"$nin": variants_to_keep}})
            if keep_ctg:
                variants_query["$and"].append({"category": {"$nin": keep_ctg}})
            if min_rank_threshold:
                variants_query["$and"].append({"rank_score": {"$lt": min_rank_threshold}})
        else:
            variants_query = case_subquery

        return variants_query

    def build_variant_query(
        self,
        query: Optional[dict] = None,
        institute_ids: Optional[list] = [],
        category: Optional[Union[str, list]] = "snv",
        variant_type: Optional[list] = ["clinical"],
    ):
        """Build a mongo query across multiple cases.
        Translate query options from a form into a complete mongo query dictionary.

        Beware that unindexed queries against a large variant collection will
        be extremely slow.

        Currently indexed query options:
            hgnc_symbols
            rank_score
            variant_type
            category

        Args:
            query(dict): A query dictionary for the database, from a query form.
            institute_ids: a list of institute _ids
            category(str): 'snv', 'sv', 'str' 'cancer_sv' or 'cancer' OR a LIST(str) of the same
            variant_type(str): 'clinical' or 'research'

        Possible query dict keys:
            phenotype_terms
            phenotype_groups
            cohorts

        Returns:
            mongo_query : A dictionary in the mongo query format.
        """

        query = query or {}
        mongo_variant_query = {}

        LOG.debug("Building a mongo query for %s" % query)

        mongo_variant_query["hgnc_symbols"] = {"$in": query["hgnc_symbols"]}
        mongo_variant_query["variant_type"] = {"$in": variant_type}

        if not category:
            category = "snv"
        mongo_variant_query["category"] = (
            {"$in": category} if isinstance(category, list) else category
        )

        select_cases = None
        select_case_obj = None
        mongo_case_query = {}

        if query.get("phenotype_terms"):
            mongo_case_query["phenotype_terms.phenotype_id"] = {"$in": query["phenotype_terms"]}

        if query.get("phenotype_groups"):
            mongo_case_query["phenotype_groups.phenotype_id"] = {"$in": query["phenotype_groups"]}

        if query.get("cohorts"):
            mongo_case_query["cohorts"] = {"$in": query["cohorts"]}

        if mongo_case_query != {} or institute_ids:
            mongo_case_query["collaborators"] = {"$in": institute_ids}
            LOG.debug("Search cases for selection set, using query {0}".format(mongo_case_query))
            select_case_objs = self.case_collection.find(mongo_case_query)
            select_cases = [case_id.get("_id") for case_id in select_case_objs]

        if query.get("similar_case"):
            select_cases = self._get_similar_cases(query, institute_ids)

        if (
            select_cases is not None
        ):  # Could be an empty list, and in that case the search would not return variants
            mongo_variant_query["case_id"] = {"$in": select_cases}

        rank_score = query.get("rank_score") or 15
        mongo_variant_query["rank_score"] = {"$gte": rank_score}

        LOG.debug("Querying %s" % mongo_variant_query)

        return mongo_variant_query

    def _get_similar_cases(self, query, institute_ids):
        """Get a list of cases similar to the given one
        Args:
            query(dict): A query dictionary for the database, from a query form.
            institute_ids: a list of institute _ids

        Returns:
            select_cases(list): a list of case dictionaries
        """
        select_cases = []
        similar_case_display_name = query["similar_case"][0]
        for institute_id in institute_ids:
            case_obj = self.case(display_name=similar_case_display_name, institute_id=institute_id)
            if case_obj is None:
                continue
            LOG.debug("Search for cases similar to %s", case_obj.get("display_name"))

            hpo_terms = []
            for term in case_obj.get("phenotype_terms", []):
                hpo_terms.append(term.get("phenotype_id"))

            similar_cases = (
                self.cases_by_phenotype(hpo_terms, case_obj["owner"], case_obj["_id"]) or []
            )
            LOG.debug("Similar cases: %s", similar_cases)
            select_cases += [similar[0] for similar in similar_cases]
        return select_cases

    def build_query(
        self,
        case_id: str,
        query: Optional[dict] = None,
        variant_ids: Optional[List[str]] = None,
        category: str = "snv",
        build: str = "37",
    ) -> dict:
        """Build a mongo query"""
        query = query or {}
        mongo_query = {}
        coordinate_query = None

        ##### Base query params

        # set up the fundamental query params: case_id, category, type and
        # restrict to list of variants (if var list is provided)
        for criterion in FUNDAMENTAL_CRITERIA:
            if criterion == "case_id":
                LOG.debug("Building a mongo query for %s" % case_id)
                mongo_query["case_id"] = case_id
                continue

            if criterion == "variant_ids" and variant_ids:
                LOG.debug("Adding variant_ids %s to query" % ", ".join(variant_ids))
                mongo_query["variant_id"] = {"$in": variant_ids}
                continue

            if criterion == "category":
                LOG.debug("Querying category %s" % category)
                mongo_query["category"] = category
                continue

            if criterion == "variant_type":
                mongo_query["variant_type"] = query.get("variant_type", "clinical")
                LOG.debug("Set variant type to %s", mongo_query["variant_type"])
                continue

            # Requests to filter based on gene panels, hgnc_symbols or
            # coordinate ranges must always be honored. They are always added to
            # query as top level, implicit '$and'. When hgnc_symbols or gene panels
            # are used, addition of relative gene symbols is delayed until after
            # the rest of the query content is clear.

            if criterion in ["hgnc_symbols", "gene_panels"]:
                gene_query = self.gene_filter(query, build=build)
                if len(gene_query) > 0 or "hpo" in query.get("gene_panels", []):
                    mongo_query["hgnc_ids"] = {
                        CRITERION_EXCLUDE_OPERATOR[
                            bool(query.get("gene_panels_exclude"))
                        ]: gene_query
                    }
                continue

            if criterion == "chrom" and query.get("chrom"):  # filter by coordinates
                query_chrom = query.get("chrom")
                if isinstance(query_chrom, list):
                    if "" in query_chrom or query_chrom == []:
                        LOG.debug(f"Query chrom {query_chrom} has All selected")
                        continue
                    if len(query_chrom) == 1:
                        query["chrom"] = query_chrom[0]
                    else:
                        mongo_query["chromosome"] = {"$in": query_chrom}
                        continue
                coordinate_query = None
                if category in ["snv", "cancer"]:
                    mongo_query["chromosome"] = query.get("chrom")
                    if query.get("start") and query.get("end"):
                        self.coordinate_filter(query, mongo_query)
                else:  # sv
                    coordinate_query = [self.sv_coordinate_query(query)]
                continue

            if criterion == "variant_ids" and variant_ids:
                LOG.debug("Adding variant_ids %s to query" % ", ".join(variant_ids))
                mongo_query["variant_id"] = {"$in": variant_ids}
                continue

            # Do not retrieve dismissed variants if hide_dismissed checkbox is checked in filter form
            if criterion == "hide_dismissed" and query.get(criterion) is True:
                mongo_query["dismiss_variant"] = {"$in": [None, []]}

            gt_query = _get_query_genotype(query)
            if criterion == "show_unaffected" and query.get(criterion) is False:
                self.affected_inds_query(mongo_query, case_id, gt_query)

            if criterion == "show_soft_filtered" and query.get(criterion) is False:
                self.soft_filters_query(query=query, mongo_query=mongo_query)

            ##### end of fundamental query params

        ##### start of the custom query params
        # there is only 'clinsig' criterion among the primary terms right now
        primary_terms = False

        # gnomad_frequency, local_obs, local_obs_freq, clingen_ngi, swegen, swegen_freq, spidex_human, cadd_score, genetic_models, mvl_tag, clinvar_tag, cosmic_tag
        # functional_annotations, region_annotations, size, svtype, decipher, depth, alt_count, somatic_score, control_frequency, tumor_frequency
        secondary_terms = False

        # check if any of the primary criteria was specified in the query
        for term in PRIMARY_CRITERIA:
            if query.get(term):
                primary_terms = True
                break

        # check if any of the secondary criteria was specified in the query:
        for term in SECONDARY_CRITERIA:
            if query.get(term):
                secondary_terms = True
                break

        if primary_terms is True:
            clinsign_filter: dict = self.set_and_get_clinsig_query(query, mongo_query)

        # Secondary, excluding filter criteria will hide variants in general,
        # but can be overridden by an including, major filter criteria
        # such as a Pathogenic ClinSig.

        if secondary_terms is True:
            secondary_filter = self.secondary_query(query, mongo_query)
            # If there are no primary criteria given, all secondary criteria are added as a
            # top level '$and' to the query.
            if secondary_filter and primary_terms is False:
                mongo_query["$and"] = secondary_filter

            # if prioritise_clinvar checkbox is checked, then clinical_filter will be applied in alternative to the secondary_filter ("$or")
            # This will happen when the search for ClinVar annotated variants is supposed to be more relaxed compared to other filter constraints, for instance when applying the clinical filter
            if primary_terms is True:
                if query.get("prioritise_clinvar") is True:
                    mongo_query["$or"] = [
                        {"$and": secondary_filter},
                        clinsign_filter,
                    ]
                else:  # clinical_filter will be applied at the same level as the other secondary filters ("$and")
                    if query.get("clinsig_exclude"):
                        clinsign_filter = {
                            "$or": [
                                clinsign_filter,
                                CLNSIG_NOT_EXISTS,
                                CLNSIG_NULL,
                            ]
                        }
                    secondary_filter.append(clinsign_filter)
                    mongo_query["$and"] = secondary_filter

        elif primary_terms is True:  # clisig is provided without secondary terms query
            if query.get("clinsig_exclude"):
                mongo_query["$or"] = [
                    clinsign_filter,
                    CLNSIG_NOT_EXISTS,
                    CLNSIG_NULL,
                ]
            else:
                mongo_query["clnsig"] = clinsign_filter["clnsig"]

        # if chromosome coordinates exist in query, add them as first element of the mongo_query['$and']
        if coordinate_query:
            if mongo_query.get("$and"):
                mongo_query["$and"] = coordinate_query + mongo_query["$and"]
            else:
                mongo_query["$and"] = coordinate_query

        return mongo_query

    def soft_filters_query(self, query: dict, mongo_query: dict):
        """Adds info to variants query to exclude variants flagged by specific filters."""
        if query.get("institute_soft_filters"):
            mongo_query["filters"] = {"$nin": query["institute_soft_filters"].split(",")}

    def affected_inds_query(self, mongo_query, case_id, gt_query):
        """Add info to variants query to filter out variants which are only in unaffected individuals

        Accepts:
            mongo_query(dict): a dictionary containing a query key/values
            case_id(str): _id of a case
            gt_selected(dict or None): dict if user specified a genotype value in genotypes form field, else None
        """
        CASE_AFFECTED_INDS_PROJECTION = {"individuals": 1}
        case_obj = self.case(case_id=case_id, projection=CASE_AFFECTED_INDS_PROJECTION)
        case_inds = case_obj.get("individuals", [])

        gt_query = gt_query or {"$nin": ["0/0", "./.", "./0", "0/."]}

        if len(case_inds) == 1:  # No point in adding this filter
            return

        affected_query = {
            "$elemMatch": {
                "$or": []
            }  # At least one of the affected individuals should harbor the variant
        }
        for ind in case_inds:
            if ind["phenotype"] in [1, "unaffected"]:  # 1=unaffected, 2=affected
                continue
            affected_match = {
                "sample_id": ind["individual_id"],
                "genotype_call": gt_query,
            }
            affected_query["$elemMatch"]["$or"].append(affected_match)

        if affected_query["$elemMatch"][
            "$or"
        ]:  # Consider situation where all individuals are unaffected
            mongo_query["samples"] = affected_query

    def set_and_get_clinsig_query(self, query: dict, mongo_query: dict) -> dict:
        """Add clinsig filter values to the mongo query object. if clinvar_tag esists in query then only results with ClinVar annotation are returned."""

        clnsig_query = {"clnsig": {}}

        if query.get("clinsig"):  # If any ClinVar significance was selected in the form multiselect
            rank = []
            str_rank = []
            for item in query["clinsig"]:
                rank.append(int(item))
                # search for human readable clinsig values in newer cases
                rank.append(CLINSIG_MAP[int(item)])
                str_rank.append(CLINSIG_MAP[int(item)])

            elem_match = [
                {"value": {"$in": rank}},
                {"value": re.compile("|".join(str_rank))},
            ]

            if query.get("clinsig_exclude"):
                elem_match_or = {"$nor": elem_match}
            else:
                elem_match_or = {"$or": elem_match}

            if query.get("clinvar_trusted_revstat") is True:
                clnsig_query["clnsig"] = {
                    "$elemMatch": {
                        "$and": [
                            elem_match_or,
                            {"revstat": re.compile("|".join(TRUSTED_REVSTAT_LEVEL))},
                        ]
                    }
                }
            else:
                clnsig_query["clnsig"] = {"$elemMatch": elem_match_or}

        if query.get("clinvar_tag"):
            mongo_query["clnsig"] = EXISTS_NOT_NULL  # Used when query has secondary terms
            clnsig_query["clnsig"]["$exists"] = True
            clnsig_query["clnsig"]["$ne"] = None

        return clnsig_query

    def coordinate_filter(self, query, mongo_query):
        """Adds genomic coordinated-related filters to the query object
            This method is called to build coordinate query for non-sv variants

        Args:
            query(dict): a dictionary of query filters specified by the users
            mongo_query(dict): the query that is going to be submitted to the database

        Returns:
            mongo_query(dict): returned object contains coordinate filters

        """
        start_pos = max(int(query["start"]), 1)
        end_pos = max(int(query["end"]), 1)
        mongo_query["position"] = {"$lte": end_pos}
        mongo_query["end"] = {"$gte": start_pos}

        return mongo_query

    def get_position_query(self, chrom: str, start: int, end: int) -> dict:
        """Helper function that returns a dictionary containing start and stop coordinates.

        The position query consists of 3 parts, each of them elements of the $or
        First part applies to searches when chromosome and end_chrom are the same.
        Here are the possible overlapping search scenarios:
        # Case 1
        # filter                 xxxxxxxxx
        # Variant           xxxxxxxx

        # Case 2
        # filter                 xxxxxxxxx
        # Variant                    xxxxxxxx

        # Case 3
        # filter                 xxxxxxxxx
        # Variant                   xx

        # Case 4
        # filter                 xxxxxxxxx
        # Variant             xxxxxxxxxxxxxx

        Second and third elements of the $or cover queries for variants where chromosome != end_chrom.
        In this situation there are the following scenarios:
        - Case chromosome != end_chrom, position matching 'chromosome'
        - Case chromosome != end_chrom, position matching 'end_chrom'
        """

        return {
            "$or": [
                # Case chromosome == end_chrom
                {
                    "$and": [
                        {"chromosome": chrom},
                        {"end_chrom": chrom},
                        {
                            "$or": [
                                # Overlapping cases 1-4 (chromosome == end_chrom)
                                {"end": {"$gte": start, "$lte": end}},  # Case 1
                                {"position": {"$gte": start, "$lte": end}},  # Case 2
                                {
                                    "$and": [
                                        {"position": {"$lte": start}},
                                        {"end": {"$gte": end}},
                                    ]
                                },  # Case 3
                                {
                                    "$and": [
                                        {"position": {"$gte": start}},
                                        {"end": {"$lte": end}},
                                    ]
                                },  # Case 4
                            ]
                        },
                    ]
                },
                # Case chromosome != end_chrom, position matching 'chromosome'
                {
                    "$and": [
                        {"chromosome": chrom},
                        {"end_chrom": {"$ne": chrom}},
                        {"position": {"$gte": start}},
                        {"position": {"$lte": end}},
                    ]
                },
                # Case chromosome != end_chrom, position matching 'end_chrom'
                {
                    "$and": [
                        {"chromosome": {"$ne": chrom}},
                        {"end_chrom": chrom},
                        {"end": {"$gte": start}},
                        {"end": {"$lte": end}},
                    ]
                },
            ]
        }

    def sv_coordinate_query(self, query: dict) -> dict:
        """Adds genomic coordinated-related filters to the query object
        This method is called to build coordinate query for sv variants
        """
        if (
            query.get("start") is not None and query.get("end") is not None
        ):  # query contains full coordinates
            chrom = query["chrom"]
            start = max(int(query["start"]), 1)
            end = max(int(query["end"]), 1)
            coordinate_query = self.get_position_query(chrom=chrom, start=start, end=end)
        else:  # query contains only chromosome info
            coordinate_query = {
                "$or": [{"chromosome": query["chrom"]}, {"end_chrom": query["chrom"]}]
            }
        return coordinate_query

    def gene_filter(self, query, build="37"):
        """Adds gene symbols to the query. Gene symbols query is a list of combined hgnc_symbols and genes included in the given panels

        Args:
            query(dict): a dictionary of query filters specified by the users

        Returns:
            hgnc_ids: The hgnc_ids of genes to filter by

        """
        LOG.debug("Adding panel and genes-related parameters to the query")
        hgnc_symbols = set(query.get("hgnc_symbols", []))

        hgnc_ids = set([self.hgnc_id(symbol, build=build) for symbol in hgnc_symbols])

        for panel in query.get("gene_panels", []):
            if panel == "hpo":
                continue  # HPO genes are already provided in the eventual hgnc_symbols fields
            hgnc_ids.update(self.panel_to_genes(panel_name=panel, gene_format="hgnc_id"))

        return list(hgnc_ids)

    def secondary_query(self, query, mongo_query, secondary_filter=None):
        """Creates a secondary query object based on secondary parameters specified by user

        Args:
            query(dict): a dictionary of query filters specified by the users
            mongo_query(dict): the query that is going to be submitted to the database

        Returns:
            mongo_secondary_query(list): a dictionary with secondary query parameters

        """
        LOG.debug("Creating a query object with secondary parameters")

        mongo_secondary_query = []

        # loop over secondary query criteria
        for criterion in SECONDARY_CRITERIA:
            if not query.get(criterion):
                continue

            if criterion == "gnomad_frequency":
                gnomad = query.get("gnomad_frequency")
                mongo_secondary_query.append(
                    {
                        "$or": [
                            {"gnomad_frequency": {"$lt": float(gnomad)}},
                            {"gnomad_frequency": NOT_EXISTS},
                        ]
                    }
                )

            for local_obs_old_type in [
                "local_obs_old",
                "local_obs_cancer_germline_old",
                "local_obs_cancer_somatic_old",
                "local_obs_cancer_somatic_panel_old",
            ]:
                if criterion == local_obs_old_type:
                    local_obs = query.get(local_obs_old_type)
                    mongo_secondary_query.append(
                        {
                            "$or": [
                                {local_obs_old_type: None},
                                {local_obs_old_type: {"$lt": local_obs + 1}},
                            ]
                        }
                    )

            if criterion == "local_obs_freq":
                local_obs_freq = query.get("local_obs_freq")
                mongo_secondary_query.append(
                    {
                        "$or": [
                            {"local_obs_old_freq": None},
                            {"local_obs_old_freq": {"$lt": local_obs_freq}},
                        ]
                    }
                )

            if criterion == "swegen_freq":
                swegen = query.get("swegen_freq")
                mongo_secondary_query.append(
                    {
                        "$or": [
                            {"swegen_mei_max": {"$lt": float(swegen)}},
                            {"swegen_mei_max": NOT_EXISTS},
                        ]
                    }
                )

            if criterion in ["clingen_ngi", "swegen"]:
                mongo_secondary_query.append(
                    {
                        "$or": [
                            {criterion: NOT_EXISTS},
                            {criterion: {"$lt": query[criterion] + 1}},
                        ]
                    }
                )

            if criterion == "spidex_human":
                # construct spidex query. Build the or part starting with empty SPIDEX values
                spidex_human = query["spidex_human"]

                spidex_query_or_part = []
                if "not_reported" in spidex_human:
                    spidex_query_or_part.append({"spidex": NOT_EXISTS})

                for spidex_level in SPIDEX_HUMAN:
                    if spidex_level in spidex_human:
                        spidex_query_or_part.append(
                            {
                                "$or": [
                                    {
                                        "$and": [
                                            {
                                                "spidex": {
                                                    "$gt": SPIDEX_HUMAN[spidex_level]["neg"][0]
                                                }
                                            },
                                            {
                                                "spidex": {
                                                    "$lt": SPIDEX_HUMAN[spidex_level]["neg"][1]
                                                }
                                            },
                                        ]
                                    },
                                    {
                                        "$and": [
                                            {
                                                "spidex": {
                                                    "$gt": SPIDEX_HUMAN[spidex_level]["pos"][0]
                                                }
                                            },
                                            {
                                                "spidex": {
                                                    "$lt": SPIDEX_HUMAN[spidex_level]["pos"][1]
                                                }
                                            },
                                        ]
                                    },
                                ]
                            }
                        )

                mongo_secondary_query.append({"$or": spidex_query_or_part})

            if criterion == "revel":
                revel = query["revel"]
                revel_query = {"revel": {"$gt": float(revel)}}
                revel_query = {"$or": [revel_query, {"revel": NOT_EXISTS}]}

                mongo_secondary_query.append(revel_query)

            if criterion == "rank_score":
                rank_score_query = {
                    "$or": [
                        {"rank_score": {"$gte": float(query["rank_score"])}},
                        {"rank_score": NOT_EXISTS},
                    ]
                }
                mongo_secondary_query.append(rank_score_query)

            if criterion == "cadd_score":
                cadd = query["cadd_score"]
                cadd_query = {"cadd_score": {"$gt": float(cadd)}}

                if query.get("cadd_inclusive") is True:
                    cadd_query = {"$or": [cadd_query, {"cadd_score": NOT_EXISTS}]}

                mongo_secondary_query.append(cadd_query)

            gt_query = _get_query_genotype(query)
            if gt_query and query.get("show_unaffected") is True:
                mongo_secondary_query.append({"samples.genotype_call": gt_query})

            if criterion in [
                "genetic_models",
                "functional_annotations",
                "region_annotations",
            ]:
                criterion_values = query[criterion]
                if criterion == "genetic_models":
                    mongo_secondary_query.append({criterion: {"$in": criterion_values}})
                else:
                    # filter key will be genes.[criterion (minus final char)]
                    mongo_secondary_query.append(
                        {".".join(["genes", criterion[:-1]]): {"$in": criterion_values}}
                    )

            if criterion == "size":
                size = query["size"]
                size_selector = query.get("size_selector")

                size_query = {
                    "$or": [
                        {"$expr": {size_selector: [{"$abs": "$length"}, size]}},
                        {"length": NOT_EXISTS},  # Include documents where 'length' is missing
                    ]
                }

                mongo_secondary_query.append(size_query)

            if criterion == "svtype":
                svtype = query["svtype"]
                mongo_secondary_query.append(
                    {"sub_category": {"$in": [re.compile(sub_category) for sub_category in svtype]}}
                )

            if criterion == "decipher":
                mongo_query["decipher"] = EXISTS

            if criterion == "depth":
                mongo_secondary_query.append({"tumor.read_depth": {"$gt": query.get("depth")}})

            if criterion == "alt_count":
                mongo_secondary_query.append({"tumor.alt_depth": {"$gt": query.get("alt_count")}})

            if criterion == "somatic_score":
                mongo_secondary_query.append(
                    {
                        "$or": [
                            {"somatic_score": {"$gt": query.get("somatic_score")}},
                            {"somatic_score": NOT_EXISTS},
                        ]
                    }
                )

            if criterion == "control_frequency":
                mongo_secondary_query.append(
                    {"normal.alt_freq": {"$lt": float(query.get("control_frequency"))}}
                )

            if criterion == "tumor_frequency":
                mongo_secondary_query.append(
                    {"tumor.alt_freq": {"$gt": float(query.get("tumor_frequency"))}}
                )

            if criterion == "mvl_tag":
                mongo_secondary_query.append({"mvl_tag": EXISTS})

            if criterion == "cosmic_tag":
                mongo_secondary_query.append({"cosmic_ids": EXISTS})
                mongo_secondary_query.append({"cosmic_ids": {"$ne": None}})

            if criterion == "fusion_score":
                mongo_secondary_query.append(
                    {"fusion_score": {"$gte": float(query.get("fusion_score"))}}
                )
            if criterion == "ffpm":
                mongo_secondary_query.append({"samples.0.ffpm": {"$gte": float(query.get("ffpm"))}})
            if criterion == "junction_reads":
                mongo_secondary_query.append(
                    {"samples.0.read_depth": {"$gte": int(query.get("junction_reads"))}}
                )
            if criterion == "split_reads":
                mongo_secondary_query.append(
                    {"samples.0.split_read": {"$gte": int(query.get("split_reads"))}}
                )
            if criterion == "fusion_caller":
                fusion_caller_query = []
                for caller in query.get("fusion_caller", []):
                    fusion_caller_query.append({caller: "Pass"})
                mongo_secondary_query.append({"$or": fusion_caller_query})

            if criterion == "clinsig_onc":

                elem_match = re.compile("|".join(query.get("clinsig_onc")))

                if query.get("clinsig_onc_exclude"):
                    mongo_secondary_query.append(
                        {
                            "$or": [
                                {
                                    "clnsig_onc.value": {"$not": elem_match}
                                },  # Exclude values in `elem_match`
                                CLNSIG_ONC_NOT_EXISTS,  # Field does not exist
                                CLNSIG_ONC_NULL,  # Field is null
                            ]
                        }
                    )
                else:
                    mongo_secondary_query.append({"clnsig_onc.value": elem_match})

        return mongo_secondary_query


def _get_query_genotype(query):
    """Query helper that returns the specific genotype selected by the user for a variantS query

    Args:
        query(dict): form dictionary with variantS query terms
    """
    q_value = query.get("genotypes")
    if q_value == "other":
        return {"$nin": ["0/1", "1/1", "0/0", "1/0", "./."]}
    elif q_value == "0/1 or 1/0":
        return {"$in": ["0/1", "1/0"]}
    elif q_value:
        return q_value
