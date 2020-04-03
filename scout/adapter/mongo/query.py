import logging
import re
from scout.constants import (
    FUNDAMENTAL_CRITERIA,
    PRIMARY_CRITERIA,
    SECONDARY_CRITERIA,
    TRUSTED_REVSTAT_LEVEL,
)

LOG = logging.getLogger(__name__)

from scout.constants import SPIDEX_HUMAN, CLINSIG_MAP


class QueryHandler(object):
    def build_variant_query(
        self, query=None, institute_id=None, category="snv", variant_type=["clinical"]
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
            category(str): 'snv', 'sv', 'str' 'cancer_sv' or 'cancer'
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

        if query.get("hgnc_symbols"):
            mongo_variant_query["hgnc_symbols"] = {"$in": query["hgnc_symbols"]}

        mongo_variant_query["variant_type"] = {"$in": variant_type}

        mongo_variant_query["category"] = category

        select_cases = None
        select_case_obj = None
        mongo_case_query = {}

        if query.get("phenotype_terms"):
            mongo_case_query["phenotype_terms.phenotype_id"] = {
                "$in": query["phenotype_terms"]
            }

        if query.get("phenotype_groups"):
            mongo_case_query["phenotype_groups.phenotype_id"] = {
                "$in": query["phenotype_groups"]
            }

        if query.get("cohorts"):
            mongo_case_query["cohorts"] = {"$in": query["cohorts"]}

        if mongo_case_query != {}:
            mongo_case_query["owner"] = institute_id
            LOG.debug(
                "Search cases for selection set, using query {0}".format(
                    select_case_obj
                )
            )
            select_case_obj = self.case_collection.find(mongo_case_query)
            select_cases = [case_id.get("display_name") for case_id in select_case_obj]

        if query.get("similar_case"):
            similar_case_display_name = query["similar_case"][0]
            case_obj = self.case(
                display_name=similar_case_display_name, institute_id=institute_id
            )
            if case_obj:
                LOG.debug(
                    "Search for cases similar to %s", case_obj.get("display_name")
                )
                similar_cases = self.get_similar_cases(case_obj)
                LOG.debug("Similar cases: %s", similar_cases)
                select_cases = [similar[0] for similar in similar_cases]
            else:
                LOG.debug("Case %s not found.", similar_case_display_name)

        if select_cases:
            mongo_variant_query["case_id"] = {"$in": select_cases}

        rank_score = query.get("rank_score") or 15
        mongo_variant_query["rank_score"] = {"$gte": rank_score}

        LOG.debug("Querying %s" % mongo_variant_query)

        return mongo_variant_query

    def build_query(self, case_id, query=None, variant_ids=None, category="snv"):
        """Build a mongo query

        These are the different query options:
            {
                'genetic_models': list,
                'chrom': str,
                'thousand_genomes_frequency': float,
                'exac_frequency': float,
                'clingen_ngi': int,
                'cadd_score': float,
                'cadd_inclusive": boolean,
                'genetic_models': list(str),
                'hgnc_symbols': list,
                'region_annotations': list,
                'functional_annotations': list,
                'clinsig': list,
                'clinsig_confident_always_returned': boolean,
                'variant_type': str(('research', 'clinical')),
                'chrom': str,
                'start': int,
                'end': int,
                'svtype': list,
                'size': int,
                'size_shorter': boolean,
                'gene_panels': list(str),
                'mvl_tag": boolean,
                'decipher": boolean,
            }

        Arguments:
            case_id(str)
            query(dict): a dictionary of query filters specified by the users
            variant_ids(list(str)): A list of md5 variant ids

        Returns:
            mongo_query : A dictionary in the mongo query format

        """
        query = query or {}
        mongo_query = {}
        gene_query = None
        coordinate_query = None

        ##### Base query params

        # set up the fundamental query params: case_id, category, type and
        # restrict to list of variants (if var list is provided)
        for criterion in FUNDAMENTAL_CRITERIA:
            if criterion == "case_id":
                LOG.debug("Building a mongo query for %s" % case_id)
                mongo_query["case_id"] = case_id

            elif criterion == "variant_ids" and variant_ids:
                LOG.debug("Adding variant_ids %s to query" % ", ".join(variant_ids))
                mongo_query["variant_id"] = {"$in": variant_ids}

            elif criterion == "category":
                LOG.debug("Querying category %s" % category)
                mongo_query["category"] = category

            elif criterion == "variant_type":
                mongo_query["variant_type"] = query.get("variant_type", "clinical")
                LOG.debug("Set variant type to %s", mongo_query["variant_type"])

            # Requests to filter based on gene panels, hgnc_symbols or
            # coordinate ranges must always be honored. They are always added to
            # query as top level, implicit '$and'. When both hgnc_symbols and a
            # panel is used, addition of this is delayed until after the rest of
            # the query content is clear.

            elif criterion in ["hgnc_symbols", "gene_panels"] and gene_query is None:
                gene_query = self.gene_filter(query, mongo_query)

            elif criterion == "chrom" and query.get("chrom"):  # filter by coordinates
                coordinate_query = None
                if category == "snv":
                    mongo_query["chromosome"] = query["chrom"]
                    if query.get("start") and query.get("end"):
                        self.coordinate_filter(query, mongo_query)
                else:  # sv
                    coordinate_query = [self.sv_coordinate_query(query)]

            elif criterion == "variant_ids" and variant_ids:
                LOG.debug("Adding variant_ids %s to query" % ", ".join(variant_ids))
                mongo_query["variant_id"] = {"$in": variant_ids}

            ##### end of fundamental query params

        ##### start of the custom query params
        # there is only 'clinsig' criterion among the primary terms right now
        primary_terms = False

        # gnomad_frequency, local_obs, clingen_ngi, swegen, spidex_human, cadd_score, genetic_models, mvl_tag
        # functional_annotations, region_annotations, size, svtype, decipher, depth, alt_count, control_frequency
        secondary_terms = False

        # check if any of the primary criteria was specified in the query
        for term in PRIMARY_CRITERIA:
            if query.get(term):
                primary_terms = True

        # check if any of the secondary criteria was specified in the query:
        for term in SECONDARY_CRITERIA:
            if query.get(term):
                secondary_terms = True

        if primary_terms is True:
            clinsign_filter = self.clinsig_query(query, mongo_query)

        # Secondary, excluding filter criteria will hide variants in general,
        # but can be overridden by an including, major filter criteria
        # such as a Pathogenic ClinSig.
        if secondary_terms is True:
            secondary_filter = self.secondary_query(query, mongo_query)

            # If there are no primary criteria given, all secondary criteria are added as a
            # top level '$and' to the query.
            if primary_terms is False:
                if gene_query:
                    mongo_query["$and"] = [
                        {"$or": gene_query},
                        {"$and": secondary_filter},
                    ]
                else:
                    mongo_query["$and"] = secondary_filter

            # If there is only one primary criterion given without any secondary, it will also be
            # added as a top level '$and'.
            # Otherwise, primary criteria are added as a high level '$or' and all secondary criteria
            # are joined together with them as a single lower level '$and'.
            if primary_terms is True:  # clinsig is specified
                # Given a request to always return confident clinical variants,
                # add the clnsig query as a major criteria, but only
                # trust clnsig entries with trusted revstat levels.
                if query.get("clinsig_confident_always_returned") == True:
                    if gene_query:
                        mongo_query["$and"] = [
                            {"$or": gene_query},
                            {"$or": [{"$and": secondary_filter}, clinsign_filter]},
                        ]
                    else:
                        mongo_query["$or"] = [
                            {"$and": secondary_filter},
                            clinsign_filter,
                        ]
                else:  # clisig terms are provided but no need for trusted revstat levels
                    secondary_filter.append(clinsign_filter)
                    if gene_query:
                        mongo_query["$and"] = [
                            {"$or": gene_query},
                            {"$and": secondary_filter},
                        ]
                    else:
                        mongo_query["$and"] = secondary_filter

        elif primary_terms is True:  # clisig is provided without secondary terms query
            # use implicit and
            mongo_query["clnsig"] = clinsign_filter["clnsig"]
            if gene_query:
                mongo_query["$and"] = [{"$or": gene_query}]

        elif gene_query:  # no primary or secondary filters provided
            mongo_query["$and"] = [{"$or": gene_query}]

        # if chromosome coordinates exist in query, add them as first element of the mongo_query['$and']
        if coordinate_query:
            if mongo_query.get("$and"):
                mongo_query["$and"] = coordinate_query + mongo_query["$and"]
            else:
                mongo_query["$and"] = coordinate_query

        LOG.info("mongo query: %s", mongo_query)
        return mongo_query

    def clinsig_query(self, query, mongo_query):
        """ Add clinsig filter values to the mongo query object

            Args:
                query(dict): a dictionary of query filters specified by the users
                mongo_query(dict): the query that is going to be submitted to the database

            Returns:
                clinsig_query(dict): a dictionary with clinsig key-values

        """
        LOG.debug("clinsig is a query parameter")
        trusted_revision_level = TRUSTED_REVSTAT_LEVEL
        rank = []
        str_rank = []
        clnsig_query = {}

        for item in query["clinsig"]:
            rank.append(int(item))
            # search for human readable clinsig values in newer cases
            rank.append(CLINSIG_MAP[int(item)])
            str_rank.append(CLINSIG_MAP[int(item)])

        if query.get("clinsig_confident_always_returned") == True:
            LOG.debug("add CLINSIG filter with trusted_revision_level")

            clnsig_query = {
                "clnsig": {
                    "$elemMatch": {
                        "$and": [
                            {
                                "$or": [
                                    {"value": {"$in": rank}},
                                    {"value": re.compile("|".join(str_rank))},
                                ]
                            },
                            {"revstat": re.compile("|".join(trusted_revision_level))},
                        ]
                    }
                }
            }
        else:
            LOG.debug(
                "add CLINSIG filter for rank: %s" % ", ".join(str(query["clinsig"]))
            )

            clnsig_query = {
                "clnsig": {
                    "$elemMatch": {
                        "$or": [
                            {"value": {"$in": rank}},
                            {"value": re.compile("|".join(str_rank))},
                        ]
                    }
                }
            }
        return clnsig_query

    def coordinate_filter(self, query, mongo_query):
        """ Adds genomic coordinated-related filters to the query object
            This method is called to buid coordinate query for non-sv variants

        Args:
            query(dict): a dictionary of query filters specified by the users
            mongo_query(dict): the query that is going to be submitted to the database

        Returns:
            mongo_query(dict): returned object contains coordinate filters

        """
        mongo_query["position"] = {"$lte": int(query["end"])}
        mongo_query["end"] = {"$gte": int(query["start"])}

        return mongo_query

    def sv_coordinate_query(self, query):
        """ Adds genomic coordinated-related filters to the query object
            This method is called to buid coordinate query for sv variants

        Args:
            query(dict): a dictionary of query filters specified by the users
            mongo_query(dict): the query that is going to be submitted to the database

        Returns:
            coordinate_query(dict): returned object contains coordinate filters for sv variant

        """
        coordinate_query = None
        chromosome_query = {
            "$or": [{"chromosome": query["chrom"]}, {"end_chrom": query["chrom"]}]
        }
        if query.get("start") and query.get("end"):
            # Query for overlapping intervals. Taking into account these cases:
            # 1
            # filter                 xxxxxxxxx
            # Variant           xxxxxxxx

            # 2
            # filter                 xxxxxxxxx
            # Variant                    xxxxxxxx

            # 3
            # filter                 xxxxxxxxx
            # Variant                   xx

            # 4
            # filter                 xxxxxxxxx
            # Variant             xxxxxxxxxxxxxx
            position_query = {
                "$or": [
                    {
                        "end": {"$gte": int(query["start"]), "$lte": int(query["end"])}
                    },  # 1
                    {
                        "position": {
                            "$lte": int(query["end"]),
                            "$gte": int(query["start"]),
                        }
                    },  # 2
                    {
                        "$and": [
                            {"position": {"$gte": int(query["start"])}},
                            {"end": {"$lte": int(query["end"])}},
                        ]
                    },  # 3
                    {
                        "$and": [
                            {"position": {"$lte": int(query["start"])}},
                            {"end": {"$gte": int(query["end"])}},
                        ]
                    },  # 4
                ]
            }
            coordinate_query = {"$and": [chromosome_query, position_query]}
        else:
            coordinate_query = chromosome_query
        return coordinate_query

    def gene_filter(self, query, mongo_query):
        """ Adds gene-related filters to the query object

        Args:
            query(dict): a dictionary of query filters specified by the users
            mongo_query(dict): the query that is going to be submitted to the database

        Returns:
            mongo_query(dict): returned object contains gene and panel-related filters

        """
        LOG.debug("Adding panel and genes-related parameters to the query")
        gene_query = []
        hgnc_symbols = query.get("hgnc_symbols")
        gene_panels = query.get("gene_panels")

        if hgnc_symbols and gene_panels:
            gene_query.append({"hgnc_symbols": {"$in": hgnc_symbols}})
            gene_query.append({"panels": {"$in": gene_panels}})
        elif hgnc_symbols:
            mongo_query["hgnc_symbols"] = {"$in": hgnc_symbols}
            LOG.debug("Adding hgnc_symbols: %s to query" % ", ".join(hgnc_symbols))
        elif gene_panels:  # gene_panels
            mongo_query["panels"] = {"$in": gene_panels}

        return gene_query

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
                if gnomad == "-1":
                    # -1 means to exclude all variants that exists in gnomad
                    mongo_query["gnomad_frequency"] = {"$exists": False}
                else:
                    # Replace comma with dot
                    mongo_secondary_query.append(
                        {
                            "$or": [
                                {"gnomad_frequency": {"$lt": float(gnomad)}},
                                {"gnomad_frequency": {"$exists": False}},
                            ]
                        }
                    )
                LOG.debug("Adding gnomad_frequency to query")

            if criterion == "local_obs":
                local_obs = query.get("local_obs")
                mongo_secondary_query.append(
                    {
                        "$or": [
                            {"local_obs_old": None},
                            {"local_obs_old": {"$lt": local_obs + 1}},
                        ]
                    }
                )

            if criterion in ["clingen_ngi", "swegen"]:
                mongo_secondary_query.append(
                    {
                        "$or": [
                            {criterion: {"$exists": False}},
                            {criterion: {"$lt": query[criterion] + 1}},
                        ]
                    }
                )

            if criterion == "spidex_human":
                # construct spidex query. Build the or part starting with empty SPIDEX values
                spidex_human = query["spidex_human"]

                spidex_query_or_part = []
                if "not_reported" in spidex_human:
                    spidex_query_or_part.append({"spidex": {"$exists": False}})

                for spidex_level in SPIDEX_HUMAN:
                    if spidex_level in spidex_human:
                        spidex_query_or_part.append(
                            {
                                "$or": [
                                    {
                                        "$and": [
                                            {
                                                "spidex": {
                                                    "$gt": SPIDEX_HUMAN[spidex_level][
                                                        "neg"
                                                    ][0]
                                                }
                                            },
                                            {
                                                "spidex": {
                                                    "$lt": SPIDEX_HUMAN[spidex_level][
                                                        "neg"
                                                    ][1]
                                                }
                                            },
                                        ]
                                    },
                                    {
                                        "$and": [
                                            {
                                                "spidex": {
                                                    "$gt": SPIDEX_HUMAN[spidex_level][
                                                        "pos"
                                                    ][0]
                                                }
                                            },
                                            {
                                                "spidex": {
                                                    "$lt": SPIDEX_HUMAN[spidex_level][
                                                        "pos"
                                                    ][1]
                                                }
                                            },
                                        ]
                                    },
                                ]
                            }
                        )

                mongo_secondary_query.append({"$or": spidex_query_or_part})

            if criterion == "cadd_score":
                cadd = query["cadd_score"]
                cadd_query = {"cadd_score": {"$gt": float(cadd)}}
                LOG.debug("Adding cadd_score: %s to query", cadd)

                if query.get("cadd_inclusive") is True:
                    cadd_query = {
                        "$or": [cadd_query, {"cadd_score": {"$exists": False}}]
                    }
                    LOG.debug("Adding cadd inclusive to query")

                mongo_secondary_query.append(cadd_query)

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

                LOG.debug(
                    "Adding {0}: {1} to query".format(
                        criterion, ", ".join(criterion_values)
                    )
                )

            if criterion == "size":
                size = query["size"]
                size_query = {"length": {"$gt": int(size)}}
                LOG.debug("Adding length: %s to query" % size)

                if query.get("size_shorter"):
                    size_query = {
                        "$or": [
                            {"length": {"$lt": int(size)}},
                            {"length": {"$exists": False}},
                        ]
                    }
                    LOG.debug("Adding size less than, undef inclusive to query.")

                mongo_secondary_query.append(size_query)

            if criterion == "svtype":
                svtype = query["svtype"]
                mongo_secondary_query.append({"sub_category": {"$in": svtype}})
                LOG.debug("Adding SV_type %s to query" % ", ".join(svtype))

            if criterion == "decipher":
                mongo_query["decipher"] = {"$exists": True}
                LOG.debug("Adding decipher to query")

            if criterion == "depth":
                LOG.debug("add depth filter")
                mongo_secondary_query.append(
                    {"tumor.read_depth": {"$gt": query.get("depth")}}
                )

            if criterion == "alt_count":
                LOG.debug("add min alt count filter")
                mongo_secondary_query.append(
                    {"tumor.alt_depth": {"$gt": query.get("alt_count")}}
                )

            if criterion == "control_frequency":
                LOG.debug("add minimum control frequency filter")
                mongo_secondary_query.append(
                    {"normal.alt_freq": {"$lt": float(query.get("control_frequency"))}}
                )

            if criterion == "mvl_tag":
                LOG.debug("add managed variant list filter")
                mongo_secondary_query.append({"mvl_tag": {"$exists": True}})

        return mongo_secondary_query
