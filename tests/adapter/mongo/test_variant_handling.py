"""Tests for variant handling"""
import logging
import os

import pytest

TRAVIS = os.getenv("TRAVIS")

LOG = logging.getLogger(__name__)


def test_variant(real_variant_database, variant_objs, case_obj):
    """Test querying a variant"""
    adapter = real_variant_database
    test_variant = list(variant_objs)[0]

    # try to collect the variant from database using its document_id:
    variant_a = adapter.variant(document_id=test_variant["_id"])
    assert variant_a

    # try to collect the variant from database using its document_id and case id:
    variant_b = adapter.variant(document_id=test_variant["variant_id"], case_id=case_obj["_id"])
    assert variant_b
    # it should be the same variant as before:
    assert variant_a == variant_b

    # try to collect the variant from database using its case id and simple_id:
    variant_c = adapter.variant(simple_id=test_variant["simple_id"], case_id=case_obj["_id"])
    assert variant_c
    # it should be the same as the other 2 variants:
    assert variant_c == variant_a


def test_query_all_gene_variants(real_variant_database):
    """ "Test querying gene variants using gene symbol."""
    adapter = real_variant_database

    ## GIVEN a populated database with variants in a certain gene
    hgnc_id = 3233
    gene_obj = adapter.hgnc_gene(hgnc_id)
    assert gene_obj
    # and a valid gene_symbol
    gene_symbol = gene_obj["hgnc_symbol"]
    assert gene_symbol

    # direct query fpr
    res = adapter.variant_collection.find(
        {
            "$and": [
                {"hgnc_symbols": gene_symbol},
                {"rank_score": {"$gte": 5}},
                {"category": "snv"},
                {"variant_type": "clinical"},
            ]
        }
    )
    nr_high_ranked_variants_in_gene = sum(1 for i in res)
    LOG.info(
        "Number of high ranked variants in %s: %s",
        gene_symbol,
        nr_high_ranked_variants_in_gene,
    )

    assert nr_high_ranked_variants_in_gene > 0

    # GIVEN a query on the correct format, corresponding to web form input
    gene_variants_query = {}
    gene_variants_query["rank_score"] = 5
    gene_variants_query["hgnc_symbols"] = [gene_symbol]

    # THEN the same number of variants should be returned by the query function
    result_cursor = adapter.gene_variants(query=gene_variants_query, nr_of_variants=-1)
    result = sum(1 for i in result_cursor)
    assert result == nr_high_ranked_variants_in_gene

    # THEN the same number of variants should be returned by 'count_documents'
    assert result == adapter.count_gene_variants(query=gene_variants_query)


def test_load_variants(real_populated_database, variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    adapter = real_populated_database
    case_id = case_obj["_id"]
    # Make sure that there are no variants in the database
    # GIVEN a populated database without any variants
    res = adapter.variants(case_id=case_id, nr_of_variants=-1)
    assert sum(1 for i in res) == 0

    # WHEN adding a number of variants
    index = 0
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    # THEN the same number of variants should have been loaded
    result = adapter.variants(case_id=case_id, nr_of_variants=-1)
    nr_variants = sum(1 for i in result)
    LOG.info("Number of variants loaded:%s", nr_variants)
    assert nr_variants == index + 1


def test_load_sv_variants(real_populated_database, sv_variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    adapter = real_populated_database
    case_id = case_obj["_id"]

    # GIVEN a populated database without any sv variants
    res = adapter.variants(case_id=case_id, nr_of_variants=-1)
    assert sum(1 for i in res) == 0

    # WHEN adding a number of sv variants
    index = 0
    for index, variant_obj in enumerate(sv_variant_objs):
        adapter.load_variant(variant_obj)

    # THEN the same number of SV variants should have been loaded
    result = adapter.variants(case_id=case_id, nr_of_variants=-1, category="sv")
    assert sum(1 for i in result) == index + 1


def test_load_all_variants(real_populated_database, case_obj):
    adapter = real_populated_database
    case_id = case_obj["_id"]

    ## GIVEN a populated database without any variants
    res = adapter.variants(case_id=case_id, nr_of_variants=-1)
    assert sum(1 for i in res) == 0

    ## WHEN loading all variants into the database
    nr_loaded = adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=None,
        chrom=None,
        start=None,
        end=None,
        gene_obj=None,
    )

    # THEN the same number of SV variants should have been loaded
    result = adapter.variants(case_id=case_id, nr_of_variants=-1, category="snv")

    assert nr_loaded == sum(1 for i in result)


def test_load_whole_gene(real_populated_database, variant_objs, case_obj):
    adapter = real_populated_database
    case_id = case_obj["_id"]

    res = adapter.variants(case_id=case_id, nr_of_variants=-1)
    assert sum(1 for i in res) == 0

    nr_loaded = adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=None,
        chrom=None,
        start=None,
        end=None,
        gene_obj=None,
    )

    ## GIVEN a populated database with variants in a certain gene
    hgnc_id = 3233
    gene_obj = adapter.hgnc_gene(hgnc_id)
    assert gene_obj
    res = adapter.variant_collection.find({"hgnc_ids": hgnc_id})
    nr_variants_in_gene = sum(1 for i in res)

    ## WHEN loading all variants for that gene
    nr_loaded = adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=None,
        chrom=None,
        start=None,
        end=None,
        gene_obj=gene_obj,
    )

    res = adapter.variant_collection.find({"hgnc_ids": hgnc_id})
    new_nr_variants_in_gene = sum(1 for i in res)

    ## Then assert that the other variants where loaded
    assert new_nr_variants_in_gene > nr_variants_in_gene


def test_load_coordinates(real_populated_database, variant_objs, case_obj):
    adapter = real_populated_database
    case_id = case_obj["_id"]

    res = adapter.variants(case_id=case_id, nr_of_variants=-1)
    assert sum(1 for i in res) == 0

    nr_loaded = adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=None,
        chrom=None,
        start=None,
        end=None,
        gene_obj=None,
    )

    ## GIVEN a populated database with variants in a certain gene
    hgnc_id = 3233
    gene_obj = adapter.hgnc_gene(hgnc_id)
    assert gene_obj
    res = adapter.variant_collection.find({"hgnc_ids": hgnc_id})
    nr_variants_in_gene = sum(1 for i in res)

    ## WHEN loading all variants for that gene
    nr_loaded = adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=None,
        chrom=gene_obj["chromosome"],
        start=gene_obj["start"],
        end=gene_obj["end"],
        gene_obj=None,
    )

    res = adapter.variant_collection.find({"hgnc_ids": hgnc_id})
    new_nr_variants_in_gene = sum(1 for i in res)

    ## Then assert that the other variants where loaded
    assert new_nr_variants_in_gene > nr_variants_in_gene


@pytest.mark.skipif(TRAVIS, reason="Tempfiles seems to be problematic on travis")
def test_get_region_vcf(populated_database, case_obj):
    adapter = populated_database
    case_id = case_obj["_id"]

    file_name = adapter.get_region_vcf(
        case_obj,
        chrom=None,
        start=None,
        end=None,
        gene_obj=None,
        variant_type="clinical",
        category="snv",
        rank_threshold=None,
    )
    ## GIVEN a populated database with variants in a certain gene
    nr_variants = 0
    with open(file_name, "r") as f:
        for line in f:
            if not line.startswith("#"):
                nr_variants += 1

    os.remove(file_name)

    assert nr_variants > 0


def test_get_region_vcf_non_existing(adapter, case_obj):
    """Test to get a region VCF when file does not exist"""
    # GIVEN a case obj without a cancer VCF
    assert case_obj["vcf_files"].get("vcf_cancer") is None

    # WHEN creating a region vcf
    with pytest.raises(FileNotFoundError):
        # THEN assert a file not found error is raised
        adapter.get_region_vcf(
            case_obj,
            chrom=None,
            start=None,
            end=None,
            gene_obj=None,
            variant_type="cancer",
            category="snv",
            rank_threshold=None,
        )


def test_get_region_vcf_missing_file(adapter, case_obj):
    """Test to get a region VCF when file does not exist"""
    # GIVEN a case obj without a cancer VCF
    case_obj["vcf_files"]["vcf_cancer"] = "afile.vcf"

    # WHEN creating a region vcf
    with pytest.raises(FileNotFoundError):
        # THEN assert a file not found error is raised
        adapter.get_region_vcf(
            case_obj,
            chrom=None,
            start=None,
            end=None,
            gene_obj=None,
            variant_type="cancer",
            category="snv",
            rank_threshold=None,
        )


def test_variant_non_existing(adapter):
    """Test to get a variant when it does not exist"""
    # GIVEN a adapter and the id of a non existing variant
    document_id = "nonexisting"

    # WHEN fetching the non existing variant
    res = adapter.variant(document_id=document_id)

    # THEN that the variant return is None
    assert res is None


def test_case_variants_count(real_populated_database, case_obj, institute_obj, variant_objs):
    """Test the functions that counts the variants by category for a case"""

    # GIVEN a database
    adapter = real_populated_database
    case_id = case_obj["_id"]
    institute_id = institute_obj["_id"]

    # Containing clinical variants
    nr_clinical = adapter.load_variants(
        case_obj=case_obj, variant_type="clinical", category="snv", rank_threshold=None
    )
    assert nr_clinical > 0

    # And research variants
    nr_research = adapter.load_variants(
        case_obj=case_obj, variant_type="research", category="sv", rank_threshold=None
    )
    assert nr_research > 0

    # WHEN the function that counts the variants by category is called
    vars_by_type = adapter.case_variants_count(case_id, institute_id)

    # THEN it should return the expected result
    assert vars_by_type["clinical"]["snv"] == nr_clinical
    assert vars_by_type["research"]["sv"] == nr_research
