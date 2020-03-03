import pytest

from scout.parse.variant import parse_variant
from scout.build import build_variant

from pprint import pprint as pp

INSTITUTE_ID = "test"


def test_build_empty():
    ## GIVEN a variant with no information
    variant = {}

    ## WHEN building a variant_obj
    ## THEN a Key Error should be raised since mandatory fields are missing
    with pytest.raises(KeyError):
        build_variant(variant, INSTITUTE_ID)


def test_build_minimal(case_obj):
    ## GIVEN a variant with minimal information
    class Cyvcf2Variant(object):
        def __init__(self):
            self.CHROM = "1"
            self.REF = "A"
            self.ALT = ["C"]
            self.POS = 10
            self.end = 11
            self.FILTER = None
            self.ID = "."
            self.QUAL = None
            self.var_type = "snp"
            self.INFO = {}

    variant = Cyvcf2Variant()

    parsed_variant = parse_variant(variant, case_obj)
    assert "ids" in parsed_variant
    variant_obj = build_variant(parsed_variant, INSTITUTE_ID)
    assert variant_obj["_id"] == parsed_variant["ids"]["document_id"]


def test_build_with_gene_info(parsed_variant):
    ## GIVEN information about a variant

    ## WHEN adding gene and transcript information and building variant
    transcript_info = {
        "functional_annotations": ["transcript_ablation"],
        "transcript_id": "ENST00000249504",
        "hgnc_id": 5134,
        "sift_prediction": "deleterious",
    }
    gene_info = {
        "transcripts": [transcript_info],
        "most_severe_transcript": transcript_info,
        "most_severe_consequence": "transcript_ablation",
        "most_severe_sift": "deleterious",
        "most_severe_polyphen": None,
        "hgnc_id": 5134,
        "region_annotation": "exonic",
    }

    parsed_variant["genes"].append(gene_info)

    variant_obj = build_variant(parsed_variant, INSTITUTE_ID)

    ## THEN assert the information is added
    assert variant_obj["institute"] == INSTITUTE_ID
    assert len(variant_obj["genes"]) == 1


def test_build_with_hgnc_info(parsed_variant):
    ## GIVEN information about a variant

    ## WHEN adding gene and transcript information and building variant
    transcript_info = {
        "functional_annotations": ["transcript_ablation"],
        "transcript_id": "ENST00000249504",
        "hgnc_id": 5134,
        "sift_prediction": "deleterious",
        "superdups_fracmatch": [0.9761, 0.9866],
    }
    gene_info = {
        "transcripts": [transcript_info],
        "most_severe_transcript": transcript_info,
        "most_severe_consequence": "transcript_ablation",
        "most_severe_sift": "deleterious",
        "most_severe_polyphen": None,
        "hgnc_id": 5134,
        "region_annotation": "exonic",
    }

    parsed_variant["genes"].append(gene_info)

    transcript_1 = {
        "ensembl_transcript_id": "ENST00000498438",
        "is_primary": False,
        "start": 176968944,
        "end": 176974482,
    }

    transcript_2 = {
        "ensembl_transcript_id": "ENST00000249504",
        "is_primary": True,
        "refseq_id": "NM_021192",
        "start": 176972014,
        "end": 176974722,
    }

    hgnc_transcripts = [transcript_1, transcript_2]

    hgnc_gene = {
        "hgnc_id": 5134,
        "hgnc_symbol": "HOXD11",
        "ensembl_id": "ENSG00000128713",
        "chromosome": "2",
        "start": 176968944,
        "end": 176974722,
        "build": 37,
        "description": "homeobox D11",
        "aliases": ["HOX4", "HOXD11", "HOX4F"],
        "entrez_id": 3237,
        "omim_ids": 142986,
        "pli_score": 0.0131898476206074,
        "primary_transcripts": ["NM_021192"],
        "ucsc_id": "uc010fqx.4",
        "uniprot_ids": ["P31277"],
        "vega_id": "OTTHUMG00000132510",
        "transcripts": hgnc_transcripts,
        "incomplete_penetrance": False,
        "inheritance_models": ["AD"],
        "transcripts_dict": {
            "ENST00000498438": transcript_1,
            "ENST00000249504": transcript_2,
        },
    }

    hgncid_to_gene = {5134: hgnc_gene}

    variant_obj = build_variant(
        parsed_variant, INSTITUTE_ID, hgncid_to_gene=hgncid_to_gene
    )

    ## THEN assert the information is added
    assert variant_obj["institute"] == INSTITUTE_ID
    assert variant_obj["genes"][0]["hgnc_id"] == 5134
    assert variant_obj["genes"][0]["hgnc_symbol"] == "HOXD11"
    assert variant_obj["genes"][0]["inheritance"] == ["AD"]


def test_build_variant(parsed_variant):
    variant_obj = build_variant(parsed_variant, INSTITUTE_ID)

    assert variant_obj["chromosome"] == parsed_variant["chromosome"]
    assert variant_obj["category"] == "snv"
    assert variant_obj["institute"] == INSTITUTE_ID


def test_build_variants(parsed_variants, institute_obj):
    for variant in parsed_variants:
        variant_obj = build_variant(variant, institute_obj)

        assert variant_obj["chromosome"] == variant["chromosome"]
        assert variant_obj["category"] == "snv"


def test_build_sv_variant(parsed_sv_variant, institute_obj):
    variant_obj = build_variant(parsed_sv_variant, institute_obj)

    assert variant_obj["chromosome"] == parsed_sv_variant["chromosome"]
    assert variant_obj["category"] == "sv"


def test_build_sv_variants(parsed_sv_variants, institute_obj):
    for variant in parsed_sv_variants:
        variant_obj = build_variant(variant, institute_obj)

        assert variant_obj["chromosome"] == variant["chromosome"]
        assert variant_obj["category"] == "sv"


def test_build_cadd_score(parsed_variants, institute_obj):
    for index, variant in enumerate(parsed_variants):
        if variant.get("cadd_score"):
            variant_obj = build_variant(variant, institute_obj)

            assert variant_obj["cadd_score"] == variant["cadd_score"]

    assert index > 0
