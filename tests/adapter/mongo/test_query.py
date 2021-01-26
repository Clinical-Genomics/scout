from scout.constants import CLINSIG_MAP, TRUSTED_REVSTAT_LEVEL
import re
from pymongo import ReturnDocument


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
        query=symbol_query, institute_id=institute_obj["_id"]
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


def test_build_query_hide_dismissed(adapter, case_obj):
    """test variants query with hide_dismissed parameter"""

    # WHEN hide_dismissed = True param is provided to the query builder
    query = {"hide_dismissed": True}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)
    # Then the variant query should filter for values with non-existing or empty "dismiss_variant" field
    assert mongo_query["dismiss_variant"] == {"$in": [None, []]}


def test_gene_symbols_query(adapter, case_obj):
    """Test variants query using HGNC symbol"""

    # WHEN hgnc_symbols params is provided to the query builder
    test_gene = "POT1"
    query = {"hgnc_symbols": [test_gene], "gene_panels": []}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # THEN the query should countain the gene
    assert mongo_query == {
        "case_id": case_obj["_id"],
        "category": "snv",
        "variant_type": "clinical",
        "hgnc_symbols": {"$in": [test_gene]},
    }


def test_gene_panel_query(adapter, case_obj):
    """Test variants query using a gene panel cointaining a certain gene"""

    # GIVEN a database containing a minimal gene panel
    test_gene = "POT1"
    test_panel = dict(panel_name="POT panel", version=1, genes=[{"symbol": test_gene}])
    adapter.panel_collection.insert_one(test_panel)
    ínserted_panel = adapter.panel_collection.find_one()

    # WHEN the panel _id is provided to the query builder
    query = {"hgnc_symbols": [], "gene_panels": ["POT panel"]}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # THEN the query should countain the gene(s) of the gene panel
    assert mongo_query == {
        "case_id": case_obj["_id"],
        "category": "snv",
        "variant_type": "clinical",
        "hgnc_symbols": {"$in": [test_gene]},
    }


def test_gene_symbol_gene_panel_query(adapter, case_obj):
    """Test variants query using a gene panel cointaining a certain gene and a hgnc symbol of another gene"""

    # GIVEN a database containing a minimal gene panel
    test_gene = "POT1"
    test_panel = dict(panel_name="POT panel", version=1, genes=[{"symbol": test_gene}])
    adapter.panel_collection.insert_one(test_panel)
    ínserted_panel = adapter.panel_collection.find_one()

    # WHEN the panel _id is provided to the query builder + a gene symbol for another gene
    query = {"hgnc_symbols": ["ATM"], "gene_panels": ["POT panel"]}
    mongo_query = adapter.build_query(case_obj["_id"], query=query)

    # THEN the query should countain both genes in the hgnc_symbols list
    mongo_query_gene_list = mongo_query["hgnc_symbols"]["$in"]
    for gene in ["ATM", "POT1"]:
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


def test_build_non_existing_gnomad(adapter):
    case_id = "cust000"
    freq = "-1"
    query = {"gnomad_frequency": freq}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query["gnomad_frequency"] == {"$exists": False}


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


def test_build_clinsig_filter(real_variant_database):
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
    n_results_raw_query = sum(1 for i in res)
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
    assert sum(1 for i in res) == 0

    # Modify clnsig value of this variant to 'Pathogenic, Likely pathogenic'
    adapter.variant_collection.update_one(
        {"_id": a_variant["_id"]},
        {"$set": {"clnsig.0.value": "Pathogenic, Likely pathogenic"}},
    )

    # One variant has multiple clssig now:
    res = adapter.variant_collection.find({"clnsig.value": "Pathogenic, Likely pathogenic"})
    assert sum(1 for i in res) == 1

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
    n_results_raw_query = sum(1 for i in res)

    # Makes sure that the variant is found anyway by the query:
    n_filtered_variants = sum(
        1 for i in adapter.variants(case_id=case_id, nr_of_variants=-1, query=query)
    )
    assert n_results_raw_query == n_filtered_variants


def test_build_clinsig_always(real_variant_database):
    adapter = real_variant_database
    case_id = "cust000"
    clinsig_confident_always_returned = True
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
        "clinsig_confident_always_returned": clinsig_confident_always_returned,
        "gnomad_frequency": freq,
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
    assert sum(1 for i in res)

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
                                {"spidex": {"$gt": -2}},
                                {"spidex": {"$lt": -float("inf")}},
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


def test_build_clinsig_always_only(adapter):
    case_id = "cust000"
    clinsig_confident_always_returned = True
    trusted_revstat_lev = TRUSTED_REVSTAT_LEVEL
    clinsig_items = [4, 5]
    clinsig_mapped_items = []
    all_clinsig = []  # both numerical and human readable values
    for item in clinsig_items:
        all_clinsig.append(item)
        all_clinsig.append(CLINSIG_MAP[item])
        clinsig_mapped_items.append(CLINSIG_MAP[item])

    query = {
        "clinsig": clinsig_items,
        "clinsig_confident_always_returned": clinsig_confident_always_returned,
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

    chrom_part = {"$or": [{"chromosome": chrom}, {"end_chrom": chrom}]}
    coordinates_part = {
        "$or": [
            {"end": {"$gte": start, "$lte": end}},  # 1
            {"position": {"$lte": end, "$gte": start}},  # 2
            {"$and": [{"position": {"$gte": start}}, {"end": {"$lte": end}}]},  # 3
            {"$and": [{"position": {"$lte": start}}, {"end": {"$gte": end}}]},
        ]
    }

    assert mongo_query["$and"] == [{"$and": [chrom_part, coordinates_part]}]


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


def test_build_decipher(adapter):
    case_id = "cust000"
    count = 1
    query = {"decipher": True}

    mongo_query = adapter.build_query(case_id, query=query)
    assert mongo_query["decipher"] == {"$exists": True}


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

    # Query should return also BND variants that have end chromosome on another chromosome than chromomsome
    assert variant_obj["chromosome"] != "6"

    updated_variant = adapter.variant_collection.find_one_and_update(
        {"_id": variant_obj["_id"]},
        {"$set": {"end_chrom": "6"}},
        return_document=ReturnDocument.AFTER,
    )
    assert updated_variant["end_chrom"] == "6"

    query = {
        "chrom": "6",
        "start": variant_obj["position"] + 10,
        "end": variant_obj["end"] - 10,
    }
    # THEN using the filter in a variant query
    results = adapter.variants(case_obj["_id"], query=query, category="sv")
    # The same variant should be returned
    assert list(results)[0] == updated_variant


def test_get_overlapping_variant(real_variant_database, case_obj, variant_objs):
    """Test function that finds SVs overlapping to a given SNV"""

    ## GIVEN a database with snv variants
    adapter = real_variant_database

    # load SV variants
    adapter.load_variants(
        case_obj, variant_type="clinical", category="sv", rank_threshold=-10, build="37"
    )
    # GIVEN a SV variant from this database
    sv_variant = adapter.variant_collection.find_one({"category": "sv"})
    assert sv_variant
    sv_variant_id = sv_variant["_id"]

    # WITH a given gene from sv variant
    gene_id = sv_variant["hgnc_ids"][0]

    # Retrieve a SNV variant occurring in the same gene:
    snv_variant = adapter.variant_collection.find_one({"category": "snv"})
    # And arbitrary set its hgnc_ids to gene_id
    updated_snv_variant = adapter.variant_collection.find_one_and_update(
        {"_id": snv_variant["_id"]}, {"$set": {"hgnc_ids": [gene_id]}}
    )
    # THEN the function that finds overlapping variants to the snv_variant
    results = adapter.overlapping(updated_snv_variant)
    for res in results:
        # SHOULD return SV variant
        assert res["category"] == "sv"
        assert res["_id"] == sv_variant_id

    # The function should also work the other way around:
    # and return snv variants that overlaps with sv variants
    results = list(adapter.overlapping(sv_variant))
    assert updated_snv_variant in results
