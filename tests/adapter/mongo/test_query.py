import re

from pymongo import ReturnDocument

from scout.constants import CLINSIG_MAP, TRUSTED_REVSTAT_LEVEL


def test_build_gene_variant_query(adapter, case_obj, test_hpo_terms, institute_obj):
    hgnc_symbols = ["POT1"]

    # GIVEN a database containing two cases with phenotype
    case_obj["phenotype_terms"] = test_hpo_terms
    adapter.case_collection.insert_one(case_obj)
    case_obj["_id"] = "internal_id_2"
    adapter.case_collection.insert_one(case_obj)

    # AND an institute
    adapter.case_collection.insert_one(institute_obj)

    # WHEN building a query
    symbol_query = {}
    symbol_query["hgnc_symbols"] = hgnc_symbols
    symbol_query["similar_case"] = [case_obj["display_name"]]
    gene_variant_query = adapter.build_variant_query(
        query=symbol_query, institute_ids=[institute_obj["_id"]]
    )

    # THEN the query should be on the right format
    assert gene_variant_query["variant_type"] == {"$in": ["clinical"]}  # default
    assert gene_variant_query["category"] == "snv"  # default
    assert gene_variant_query["rank_score"] == {"$gte": 15}  # default
    assert gene_variant_query["hgnc_symbols"] == {"$in": hgnc_symbols}
    assert gene_variant_query["case_id"] == {"$in": ["internal_id_2"]}


def test_build_query(adapter):
    case_id = "cust000"

    # GIVEN a empty database

    # WHEN building a query
    query = adapter.build_query(case_id)

    # THEN the query should be on the right format
    assert query["case_id"] == case_id
    assert query["category"] == "snv"
    assert query["variant_type"] == "clinical"


def test_build_query_hide_not_in_affected(adapter, case_obj):
    """Test variants query build with show_unaffected parameter"""

    # GIVEN a database with a case with one affected individual
    adapter.case_collection.insert_one(case_obj)

    # WHEN show_unaffected = True param is provided to the query builder
    query = {"show_unaffected": False}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # Then the variant query should return only variants in the affected individual and in presence of the allele
    assert mongo_query["samples"] == {
        "$elemMatch": {
            "$or": [
                {
                    "sample_id": case_obj["individuals"][0]["individual_id"],
                    "genotype_call": {"$nin": ["0/0", "./.", "./0", "0/."]},
                }
            ]
        }
    }


def test_build_query_hide_dismissed(adapter, case_obj):
    """Test variants query with hide_dismissed parameter"""

    # WHEN hide_dismissed = True param is provided to the query builder
    query = {"hide_dismissed": True}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)
    # Then the variant query should filter for values with non-existing or empty "dismiss_variant" field
    assert mongo_query["dismiss_variant"] == {"$in": [None, []]}


def test_gene_symbols_query(adapter, case_obj):
    """Test variants query using HGNC symbol"""

    # WHEN hgnc_symbols params is provided to the query builder
    gene_obj = {
        "hgnc_id": 17284,
        "hgnc_symbol": "POT1",
        "build": "37",
        "aliases": ["POTTA", "POT1"],
    }
    adapter.load_hgnc_gene(gene_obj)

    query = {"hgnc_symbols": [gene_obj["hgnc_symbol"]], "gene_panels": []}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # THEN the query should countain the hgnc_id of the gene
    assert mongo_query == {
        "case_id": case_obj["_id"],
        "category": "snv",
        "variant_type": "clinical",
        "hgnc_ids": {"$in": [gene_obj["hgnc_id"]]},
    }


def test_gene_panel_query(adapter, case_obj):
    """Test variants query using a gene panel containing a certain gene"""

    # GIVEN a database containing a minimal gene panel
    test_gene = "POT1"
    test_gene_hgnc_id = 17284

    test_panel = dict(
        panel_name="POT panel",
        version=1,
        genes=[{"symbol": test_gene, "hgnc_id": test_gene_hgnc_id}],
    )
    adapter.panel_collection.insert_one(test_panel)

    # WHEN the panel _id is provided to the query builder
    query = {"hgnc_symbols": [], "gene_panels": ["POT panel"]}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # THEN the query should countain the gene(s) of the gene panel
    assert mongo_query == {
        "case_id": case_obj["_id"],
        "category": "snv",
        "variant_type": "clinical",
        "hgnc_ids": {"$in": [test_gene_hgnc_id]},
    }


def test_soft_filters_query(adapter, case_obj):
    """Test variants query by providing a form with soft filters data."""

    # GIVEN some soft filters saved at the institute level:
    institute_soft_filters = "germline_risk,in_normal"
    show_soft_filtered = False

    # WHEN user query contains this data:
    query = {
        "institute_soft_filters": institute_soft_filters,
        "show_soft_filtered": show_soft_filtered,
    }
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # THEN the MongoDB query should contain soft filters:
    assert mongo_query["filters"] == {"$nin": institute_soft_filters.split(",")}


def test_genotype_query_heterozygous(adapter, case_obj):
    """Test variants query using a 'genotypes' field in variants filter to filter for heterozygous variants"""

    # WHEN a value is provided for 'genotypes' in variants query
    query = {"genotypes": "0/1 or 1/0", "show_unaffected": True}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)
    # THEN mongo query should contain the expected value
    assert mongo_query["$and"] == [{"samples.genotype_call": {"$in": ["0/1", "1/0"]}}]


def test_genotype_query_other(adapter, case_obj):
    """Test variants query using a 'genotypes' field in variants filter form with value: other"""

    # WHEN a value is provided for 'genotypes' in variants query
    query = {"genotypes": "other", "show_unaffected": True}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)
    # THEN mongo query should contain the expected value
    assert mongo_query["$and"] == [
        {"samples.genotype_call": {"$nin": ["0/1", "1/1", "0/0", "1/0", "./."]}}
    ]


def test_gene_symbol_gene_panel_query(adapter, case_obj):
    """Test variants query using a gene panel cointaining a certain gene and a hgnc symbol of another gene"""

    # GIVEN a database containing a minimal gene panel
    test_gene = "POT1"
    test_gene_hgnc_id = 17284
    test_panel = dict(
        panel_name="POT panel",
        version=1,
        genes=[{"symbol": test_gene, "hgnc_id": test_gene_hgnc_id}],
    )
    adapter.panel_collection.insert_one(test_panel)

    other_gene = "ATM"
    other_gene_hgnc_id = 795
    other_gene_obj = {
        "hgnc_id": other_gene_hgnc_id,
        "hgnc_symbol": other_gene,
        "build": "37",
        "aliases": [test_gene],
    }
    adapter.load_hgnc_gene(other_gene_obj)

    # WHEN the panel _id is provided to the query builder + a gene symbol for another gene
    query = {"hgnc_symbols": ["ATM"], "gene_panels": ["POT panel"]}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # THEN the query should countain both genes in the hgnc_symbols list
    mongo_query_gene_list = mongo_query["hgnc_ids"]["$in"]
    for gene in [test_gene_hgnc_id, other_gene_hgnc_id]:
        assert gene in mongo_query_gene_list


def test_build_gnomad_query(adapter):
    case_id = "cust000"
    freq = 0.01
    query = {"gnomad_frequency": freq}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["case_id"] == case_id
    assert mongo_query["category"] == "snv"
    assert mongo_query["variant_type"] == "clinical"
    assert mongo_query["$and"] == [
        {
            "$or": [
                {"gnomad_frequency": {"$lt": freq}},
                {"gnomad_frequency": {"$exists": False}},
            ]
        }
    ]


def test_build_cadd_exclusive(adapter):
    case_id = "cust000"
    cadd = 10.0
    cadd_inclusive = False
    query = {"cadd_score": cadd, "cadd_inclusive": cadd_inclusive}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["$and"] == [{"cadd_score": {"$gt": cadd}}]


def test_build_cadd_inclusive(adapter):
    case_id = "cust000"
    cadd = 10.0
    cadd_inclusive = True
    query = {"cadd_score": cadd, "cadd_inclusive": cadd_inclusive}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["$and"] == [
        {"$or": [{"cadd_score": {"$gt": cadd}}, {"cadd_score": {"$exists": False}}]}
    ]


def test_build_gnomad_and_cadd(adapter):
    case_id = "cust000"
    freq = 0.01
    cadd = 10.0
    query = {"gnomad_frequency": freq, "cadd_score": cadd}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["$and"] == [
        {
            "$or": [
                {"gnomad_frequency": {"$lt": freq}},
                {"gnomad_frequency": {"$exists": False}},
            ]
        },
        {"cadd_score": {"$gt": cadd}},
    ]


def test_build_clinsig(adapter):
    case_id = "cust000"
    clinsig_items = [3, 4, 5]
    clinsig_mapped_items = []
    all_clinsig = []  # both numerical and human readable values

    for item in clinsig_items:
        all_clinsig.append(item)
        all_clinsig.append(CLINSIG_MAP[item])
        clinsig_mapped_items.append(CLINSIG_MAP[item])

    query = {"clinsig": clinsig_items}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["clnsig"] == {
        "$elemMatch": {
            "$or": [
                {"value": {"$in": all_clinsig}},
                {"value": re.compile("|".join(clinsig_mapped_items))},
            ]
        }
    }


def test_build_clinsig_filter_exclude_status(adapter):
    """Test building a variants query excluding ClinVar statuses."""

    clinsig_items = [4, 5]
    clinsig_mapped_items = []
    all_clinsig = []  # both numerical and human readable values
    for item in clinsig_items:
        all_clinsig.append(item)
        all_clinsig.append(CLINSIG_MAP[item])
        clinsig_mapped_items.append(CLINSIG_MAP[item])

    # GIVEN a query containing clinsig terms and "clinsig_exclude" = True
    query = {"clinsig": clinsig_items, "clinsig_exclude": True}
    mongo_query = adapter.build_query(case_id="cust000", query=query)

    # THEN the mongo query should contain the expected elements, either the variant has no ClinVar signififcance
    assert {"clnsig": {"$exists": False}} in mongo_query["$or"]
    assert {"clnsig": {"$eq": None}} in mongo_query["$or"]

    # OR the clinical significance doesn't contain the selected terms
    clinsig_exclude_elemmatch = [
        {"value": {"$in": all_clinsig}},
        {"value": re.compile("|".join(clinsig_mapped_items))},
    ]
    clisig_signif_exclude_query = {"clnsig": {"$elemMatch": {"$nor": clinsig_exclude_elemmatch}}}
    assert clisig_signif_exclude_query in mongo_query["$or"]


def test_build_clinsig_filter(real_variant_database):
    """Test building a variants query with ClinVar status."""
    adapter = real_variant_database
    case_id = "cust000"
    clinsig_items = [4, 5]
    clinsig_mapped_items = []
    all_clinsig = []  # both numerical and human readable values
    for item in clinsig_items:
        all_clinsig.append(item)
        all_clinsig.append(CLINSIG_MAP[item])
        clinsig_mapped_items.append(CLINSIG_MAP[item])

    region_annotation = ["exonic", "splicing"]

    query = {"region_annotations": region_annotation, "clinsig": clinsig_items}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["$and"] == [
        {"genes.region_annotation": {"$in": region_annotation}},
        {
            "clnsig": {
                "$elemMatch": {
                    "$or": [
                        {"value": {"$in": all_clinsig}},
                        {"value": re.compile("|".join(clinsig_mapped_items))},
                    ]
                }
            }
        },
    ]

    assert adapter.variant_collection.find_one()

    # Test that the query works with real data:

    case_obj = adapter.case_collection.find_one()
    case_id = case_obj["_id"]

    # Execute a raw query to collect variants that should pass the filter
    res = adapter.variant_collection.find(
        {
            "$and": [
                {"genes.region_annotation": {"$in": region_annotation}},
                {"clnsig.value": {"$in": [4, "Likely pathogenic", 5, "Pathogenic"]}},
                {"case_id": case_id},
                {"category": "snv"},
                {"variant_type": "clinical"},
            ]
        }
    )
    n_results_raw_query = sum(1 for _ in res)
    assert n_results_raw_query

    # filter real variants using query:
    filtered_variants = [
        var for var in adapter.variants(case_id=case_id, nr_of_variants=-1, query=query)
    ]

    # number of variants returned by raw query and filtered variants should be the same:
    assert len(filtered_variants) == n_results_raw_query

    # Check if query works on clnsig.value that comma separated values:
    a_variant = list(filtered_variants)[0]
    assert a_variant["_id"]

    # there should be no variant with clnsig.value=='Pathogenic, Likely pathogenic'
    res = adapter.variant_collection.find({"clnsig.value": "Pathogenic, Likely pathogenic"})
    assert sum(1 for _ in res) == 0

    # Modify clnsig value of this variant to 'Pathogenic, Likely pathogenic'
    adapter.variant_collection.update_one(
        {"_id": a_variant["_id"]},
        {"$set": {"clnsig.0.value": "Pathogenic, Likely pathogenic"}},
    )

    # One variant has multiple clinsig now:
    res = adapter.variant_collection.find({"clnsig.value": "Pathogenic, Likely pathogenic"})
    assert sum(1 for _ in res) == 1

    # Update raw query to find this variant as well
    res = adapter.variant_collection.find(
        {
            "$and": [
                {"genes.region_annotation": {"$in": region_annotation}},
                {
                    "clnsig.value": {
                        "$in": [
                            4,
                            "Likely pathogenic",
                            5,
                            "Pathogenic",
                            "Pathogenic, Likely pathogenic",
                        ]
                    }
                },
                {"case_id": case_id},
                {"category": "snv"},
                {"variant_type": "clinical"},
            ]
        }
    )
    n_results_raw_query = sum(1 for _ in res)

    # Makes sure that the variant is found anyway by the query:
    n_filtered_variants = sum(
        1 for _ in adapter.variants(case_id=case_id, nr_of_variants=-1, query=query)
    )
    assert n_results_raw_query == n_filtered_variants


def test_build_clinsig_high_confidence_plus_region_and_gnomad(real_variant_database):
    """Test building a variants query with ClinVar status and high confidence."""
    adapter = real_variant_database
    case_id = "cust000"
    clinvar_trusted_revstat = True
    trusted_revstat_lev = TRUSTED_REVSTAT_LEVEL
    clinsig_items = [4, 5]
    clinsig_mapped_items = []
    all_clinsig = []  # both numerical and human readable values
    for item in clinsig_items:
        all_clinsig.append(item)
        all_clinsig.append(CLINSIG_MAP[item])
        clinsig_mapped_items.append(CLINSIG_MAP[item])

    region_annotation = ["exonic", "splicing"]
    freq = 0.01

    query = {
        "region_annotations": region_annotation,
        "clinsig": clinsig_items,
        "clinvar_trusted_revstat": clinvar_trusted_revstat,
        "gnomad_frequency": freq,
        "prioritise_clinvar": True,
    }

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["$or"] == [
        {
            "$and": [
                {
                    "$or": [
                        {"gnomad_frequency": {"$lt": freq}},
                        {"gnomad_frequency": {"$exists": False}},
                    ]
                },
                {"genes.region_annotation": {"$in": region_annotation}},
            ]
        },
        {
            "clnsig": {
                "$elemMatch": {
                    "$and": [
                        {
                            "$or": [
                                {"value": {"$in": all_clinsig}},
                                {"value": re.compile("|".join(clinsig_mapped_items))},
                            ]
                        },
                        {"revstat": re.compile("|".join(trusted_revstat_lev))},
                    ]
                }
            }
        },
    ]

    # Test that the query works with real data
    case_obj = adapter.case_collection.find_one()
    case_id = case_obj["_id"]

    res = adapter.variants(case_id=case_id, nr_of_variants=-1)
    assert sum(1 for _ in res)

    # filter variants using query:
    filtered_variants = list(adapter.variants(case_id=case_id, nr_of_variants=-1, query=query))
    assert len(filtered_variants) > 0

    # Make sure that variants are filtered as they should:
    for var in filtered_variants:
        gnomad_filter = False
        anno_filter = False
        clisig_filter = False

        if "gnomad_frequency" in var:
            if var["gnomad_frequency"] < freq:
                gnomad_filter = True
        else:
            gnomad_filter = True

        for gene in var["genes"]:
            if gene["region_annotation"] in region_annotation:
                anno_filter = True

        if "clnsig" in var:
            for clnsig in var["clnsig"]:
                if clnsig["value"] in [4, "Likely pathogenic", 5, "Pathogenic"]:
                    clisig_filter = True

        # Assert that variant passes gnomad filter + anno_filter or has the required clinsig
        assert (gnomad_filter and anno_filter) or clisig_filter


def test_build_spidex_not_reported(adapter):
    case_id = "cust000"
    spidex_human = ["not_reported"]

    query = {"spidex_human": spidex_human}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["$and"] == [{"$or": [{"spidex": {"$exists": False}}]}]


def test_build_spidex_high(adapter):
    case_id = "cust000"
    spidex_human = ["high"]

    query = {"spidex_human": spidex_human}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["$and"] == [
        {
            "$or": [
                {
                    "$or": [
                        {
                            "$and": [
                                {"spidex": {"$gt": -float("inf")}},
                                {"spidex": {"$lt": -2}},
                            ]
                        },
                        {
                            "$and": [
                                {"spidex": {"$gt": 2}},
                                {"spidex": {"$lt": float("inf")}},
                            ]
                        },
                    ]
                }
            ]
        }
    ]


def test_build_has_clnsig(
    adapter,
    case_obj,
):
    """Test building query to retrieve all variants with ClinVar tag"""
    case_id = case_obj["_id"]
    query = {"clinvar_tag": True}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["clnsig"]["$exists"] is True
    assert mongo_query["clnsig"]["$ne"] is None


def test_build_has_cosmic_ids(
    adapter,
    case_obj,
):
    """Test building query to retrieve all variants with cosmic IDs"""
    case_id = case_obj["_id"]
    query = {"cosmic_tag": True}

    mongo_query = adapter.build_query(case_id, query=query)

    assert {"cosmic_ids": {"$exists": True}} in mongo_query["$and"]
    assert {"cosmic_ids": {"$ne": None}} in mongo_query["$and"]


def test_build_clinsig_high_confidence(adapter):
    """Test building a variants query with high confidence of ClinVar status."""
    case_id = "cust000"
    clinvar_trusted_revstat = True
    trusted_revstat_lev = TRUSTED_REVSTAT_LEVEL
    clinsig_items = [4, 5]
    clinsig_mapped_items = []
    all_clinsig = []  # both numerical and human readable values
    for item in clinsig_items:
        all_clinsig.append(item)
        all_clinsig.append(CLINSIG_MAP[item])
        clinsig_mapped_items.append(CLINSIG_MAP[item])

    # Testing with INCLUDE ClinVar terms criterion
    query = {
        "clinsig": clinsig_items,
        "clinvar_trusted_revstat": clinvar_trusted_revstat,
    }

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["clnsig"] == {
        "$elemMatch": {
            "$and": [
                {
                    "$or": [
                        {"value": {"$in": all_clinsig}},
                        {"value": re.compile("|".join(clinsig_mapped_items))},
                    ]
                },
                {"revstat": re.compile("|".join(trusted_revstat_lev))},
            ]
        }
    }


def test_build_chrom(adapter):
    case_id = "cust000"
    chrom = "1"
    query = {"chrom": chrom}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["chromosome"] == chrom


def test_build_coordinate_filter(adapter):
    case_id = "cust000"
    chrom = "1"
    start = 79000
    end = 80000
    query = {"chrom": "1", "start": start, "end": end}
    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["chromosome"] == chrom
    assert mongo_query["position"] == {"$lte": end}
    assert mongo_query["end"] == {"$gte": start}


def test_build_sv_coordinate_query(adapter):
    case_id = "cust000"
    chrom = "1"
    start = 79000
    end = 80000
    query = {"chrom": "1", "start": start, "end": end}
    mongo_query = adapter.build_query(case_id, query=query, category="sv")
    assert mongo_query["$and"] == [adapter.get_position_query(chrom, start, end)]


def test_build_ngi_sv(adapter):
    case_id = "cust000"
    count = 1
    query = {"clingen_ngi": count}

    mongo_query = adapter.build_query(case_id, query=query)
    assert mongo_query["$and"] == [
        {
            "$or": [
                {"clingen_ngi": {"$exists": False}},
                {"clingen_ngi": {"$lt": query["clingen_ngi"] + 1}},
            ]
        }
    ]


def test_build_swegen_sv(adapter):
    case_id = "cust000"
    count = 1
    query = {"swegen": count}

    mongo_query = adapter.build_query(case_id, query=query)
    assert mongo_query["$and"] == [
        {
            "$or": [
                {"swegen": {"$exists": False}},
                {"swegen": {"$lt": query["swegen"] + 1}},
            ]
        }
    ]


def test_build_local_obs(adapter):
    """Test building a query containing local archived observations (RD and cancer variants."""

    # GIVEN query parameters for local observations
    LOCAL_OLD_OBS_FIELDS = [
        "local_obs_old",
        "local_obs_cancer_somatic_old",
        "local_obs_cancer_germline_old",
    ]
    case_id = "cust000"
    count = 5
    query = {}
    for query_field in LOCAL_OLD_OBS_FIELDS:
        query[query_field] = count

    # WHEN asking adapter to build a db query
    mongo_query = adapter.build_query(case_id, query=query)

    # THEN the expected query part for local observations is returned
    for query_field in LOCAL_OLD_OBS_FIELDS:
        query_item = {
            "$or": [
                {query_field: None},
                {query_field: {"$lt": query[query_field] + 1}},
            ]
        }
        assert query_item in mongo_query["$and"]


def test_build_local_obs_freq(adapter):
    """Test building query. Given query parameters from interface, check that
    a correct db query is made. This tests local observations frequency.
    """

    # GIVEN query parameters for local observations
    case_id = "cust000"
    count = 5
    query = {"local_obs_freq": count}

    # WHEN asking adapter to build a db query
    mongo_query = adapter.build_query(case_id, query=query)

    # THEN the expected query part for local observations is returned
    assert mongo_query["$and"] == [
        {
            "$or": [
                {"local_obs_old_freq": None},
                {"local_obs_old_freq": {"$lt": query["local_obs_freq"]}},
            ]
        }
    ]


def test_build_decipher(adapter):
    case_id = "cust000"
    count = 1
    query = {"decipher": True}

    mongo_query = adapter.build_query(case_id, query=query)
    assert mongo_query["decipher"] == {"$exists": True}


def test_build_query_clnsig_oncogenicity(adapter, case_obj):
    """Test building a query for variants with oncogenicity."""
    case_id = case_obj["_id"]
    # GIVEN a user query with oncogenicity criteria
    query = {"clinsig_onc": ["oncogenic", "likely_oncogenic"]}
    # WHEN building thw query
    mongo_query = adapter.build_query(case_id, query=query)
    # THEN it should contain the expected search criteria
    assert mongo_query["$and"] == [{"clnsig_onc.value": re.compile("oncogenic|likely_oncogenic")}]


def test_build_query_exclude_clnsig_oncogenicity(adapter, case_obj):
    """Test building a query that exclude the selected oncogenicity criteria."""
    case_id = case_obj["_id"]
    # GIVEN a user query with oncogenicity criteria
    query = {"clinsig_onc": ["benign", "likely_benign"], "clinsig_onc_exclude": True}
    # WHEN building thw query
    mongo_query = adapter.build_query(case_id, query=query)
    # THEN it should contain the expected search criteria
    assert mongo_query["$and"] == [
        {
            "$or": [
                {"clnsig_onc.value": {"$not": re.compile("benign|likely_benign")}},
                {"clnsig_onc": {"$exists": False}},
                {"clnsig_onc": {"$eq": None}},
            ]
        }
    ]


def test_build_range(adapter):
    case_id = "cust000"
    chrom = "1"
    start = 10
    end = 11
    query = {"chrom": chrom, "start": start, "end": end}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["chromosome"] == chrom
    assert mongo_query["position"] == {"$lte": end}
    assert mongo_query["end"] == {"$gte": start}


def test_query_snvs_by_coordinates(real_populated_database, variant_objs, case_obj):
    """Run SNV variant query by coordinates"""
    adapter = real_populated_database

    # WHEN adding a number of variants
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    ## GIVEN a variant from the database
    variant_obj = adapter.variant_collection.find_one()

    # WHEN creating a variant filter by chromosome coordinates
    query = {
        "chrom": variant_obj["chromosome"],
        "start": variant_obj["position"],
        "end": variant_obj["end"],
    }
    # AND using the filter in a query
    results = adapter.variants(case_obj["_id"], query=query)
    # THEN the same variant should be returned
    assert list(results)[0] == variant_obj


def test_query_svs_by_coordinates(real_populated_database, sv_variant_objs, case_obj):
    """Run SV variant query by coordinates"""
    adapter = real_populated_database

    # WHEN adding a number of SV variants
    for index, variant_obj in enumerate(sv_variant_objs):
        adapter.load_variant(variant_obj)

    ## GIVEN a variant from the database
    variant_obj = adapter.variant_collection.find_one()

    # WHEN creating a variant filter by chromosome coordinates
    # Using the same coordinates as the variant
    query = {
        "chrom": variant_obj["chromosome"],
        "start": variant_obj["position"],
        "end": variant_obj["end"],
    }
    # AND using the filter in a variant query
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    # THEN the same variant should be returned
    assert list(results)[0] == variant_obj

    # When creating a variant filter by chromosome coordinates
    # In this scenario:
    # filter                 xxxxxxxxx
    # Variant           xxxxxxxx
    query = {
        "chrom": variant_obj["chromosome"],
        "start": variant_obj["position"] + 10,
        "end": variant_obj["end"] + 10,
    }
    # AND using the filter in a variant query
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    # THEN the same variant should be returned
    assert list(results)[0] == variant_obj

    # When creating a variant filter by chromosome coordinates
    # In this scenario:
    # filter                 xxxxxxxxx
    # Variant                    xxxxxxxx
    query = {
        "chrom": variant_obj["chromosome"],
        "start": variant_obj["position"] - 10,
        "end": variant_obj["end"] - 10,
    }
    # AND using the filter in a variant query
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    # THEN the same variant should be returned
    assert list(results)[0] == variant_obj

    # When creating a variant filter by chromosome coordinates
    # In this scenario:
    # filter                 xxxxxxxxx
    # Variant                   xx
    query = {
        "chrom": variant_obj["chromosome"],
        "start": variant_obj["position"] - 10,
        "end": variant_obj["end"] + 10,
    }
    # AND using the filter in a variant query
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    # THEN the same variant should be returned
    assert list(results)[0] == variant_obj

    # When creating a variant filter by chromosome coordinates
    # In this scenario:
    # filter                 xxxxxxxxx
    # Variant             xxxxxxxxxxxxxx
    query = {
        "chrom": variant_obj["chromosome"],
        "start": variant_obj["position"] + 10,
        "end": variant_obj["end"] - 10,
    }
    # AND using the filter in a variant query
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    # THEN the same variant should be returned
    assert list(results)[0] == variant_obj


def test_query_svs_by_coordinates_bnds(adapter, case_obj):
    """Test retrieving BND variants using variants query."""

    # WHEN adding a SV variant with chromosome != end_chrom
    variant_obj = {
        "chromosome": "2",
        "end_chrom": "7",
        "position": 65000,
        "end": 22000,
        "category": "sv",
        "sub_category": "bnd",
        "case_id": case_obj["_id"],
        "variant_type": "clinical",
    }
    adapter.load_variant(variant_obj)

    # A coordinate search using chromosome should return the variant
    query = {
        "chrom": "2",
        "start": 64000,
        "end": 66000,
    }
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    assert list(results)

    # Same should happen also when searching for coordinates matching end_chrom
    query = {
        "chrom": "7",
        "start": 21000,
        "end": 23000,
    }
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    assert list(results)


def test_get_overlapping_variant(real_variant_database, case_obj, variant_obj, sv_variant_obj):
    """Test function that finds SVs overlapping to a given SNV"""

    ## GIVEN a database with snv variants
    adapter = real_variant_database

    # load SV variants
    adapter.load_variants(
        case_obj, variant_type="clinical", category="sv", rank_threshold=-10, build="37"
    )
    # load WTS variants
    adapter.load_omics_variants(case_obj=case_obj, file_type="fraser", build="37")

    # GIVEN a SV variant in this database
    sv_variant = adapter.variant_collection.find_one({"_id": sv_variant_obj["_id"]})
    assert sv_variant

    # WITH a given gene on the SV
    gene_id = 17978
    updated_sv_variant = adapter.variant_collection.find_one_and_update(
        {"_id": sv_variant["_id"]},
        {"$set": {"hgnc_ids": [gene_id]}},
        return_document=ReturnDocument.AFTER,
    )
    # Retrieve a SNV variant occurring in the same case:
    snv_variant = adapter.variant_collection.find_one({"_id": variant_obj["_id"]})
    assert snv_variant

    # And arbitrary set its hgnc_ids to gene_id
    updated_snv_variant = adapter.variant_collection.find_one_and_update(
        {"_id": snv_variant["_id"]},
        {"$set": {"hgnc_ids": [gene_id]}},
        return_document=ReturnDocument.AFTER,
    )

    # Retrieve an OMICS variant occurring in the same case:
    omics_variant = adapter.omics_variant_collection.find_one()
    assert omics_variant
    # And arbitrarily set its hgnc_ids to gene_id
    updated_omics_variant = adapter.omics_variant_collection.find_one_and_update(
        {"_id": omics_variant["_id"]},
        {"$set": {"hgnc_ids": [gene_id]}},
        return_document=ReturnDocument.AFTER,
    )

    # THEN the function that finds overlapping variants to the snv_variant
    overlapping_dna, overlapping_wts = adapter.hgnc_overlapping(updated_snv_variant, limit=10000)
    for res in overlapping_dna:
        # SHOULD return the SV variant
        assert res["category"] == "sv"
        assert res["_id"] == sv_variant["_id"]

    for res in overlapping_wts:
        # SHOULD return the omics variant
        assert res["category"] == "outlier"
        assert res["_id"] == omics_variant["_id"]

    # The function should also work the other way around:
    # and return snv variants that overlaps with sv variants
    overlapping_dna, overlapping_wts = list(
        adapter.hgnc_overlapping(updated_sv_variant, limit=10000)
    )
    result_ids = [result_var["_id"] for result_var in overlapping_dna]
    assert updated_snv_variant["_id"] in result_ids

    # and return RNA variants that overlaps with sv variants
    result_ids = [result_var["_id"] for result_var in overlapping_wts]
    assert updated_omics_variant["_id"] in result_ids
