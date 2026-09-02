"""Tests for OMICS variant handling"""

import logging

from scout.constants import ORDERED_OMICS_FILE_TYPE_MAP
from scout.models.omics_variant import OmicsVariantLoader

LOG = logging.getLogger(__name__)

METHBAT_SIGN_FIXTURES = [
    {
        "chrom": "chr6",
        "start": "144007487",
        "end": "144008719",
        "cpg_label": "malformattedlabel",
        "region_type": "nanoimprint",
        "hgnc_id": "9046",
        "hgnc_symbol": "PLAGL1",
        "summary_label": "AlleleSpecificMethylation",
        "compare_label": "Uncategorized",
        "sample_id": "ADM1059A2",
    },
    {
        "chrom": "chr22",
        "start": "23179509",
        "end": "23180508",
        "cpg_label": "malformatted_label2",
        "region_type": "promoter",
        "hgnc_id": "1014",
        "hgnc_symbol": "BCR",
        "summary_label": "Unmethylated",
        "compare_label": "HypoMethylated",
        "sample_id": "ADM1059A2",
    },
    {
        "chrom": "chr22",
        "start": "30079464",
        "end": "30080463",
        "cpg_label": "promoter_HORMAD2_HGNC:28383",
        "region_type": "",
        "hgnc_id": "",
        "hgnc_symbol": "",
        "summary_label": "Methylated",
        "compare_label": "HyperMethylated",
        "sample_id": "ADM1059A2",
    },
]


def test_omics_variant_model(case_obj):
    """Test that the omics variant model is created correctly."""

    # GIVEN a parsed tsv omics dicts info array
    omics_infos = METHBAT_SIGN_FIXTURES

    for omics_info in omics_infos:
        # GIVEN with required fields for the OmicsVariantLoader model
        for key in ["category", "sub_category", "variant_type", "analysis_type"]:
            omics_info[key] = ORDERED_OMICS_FILE_TYPE_MAP["methbat"][key]

        omics_info["case_id"] = case_obj["_id"]
        omics_info["build"] = case_obj["genome_build"]
        omics_info["institute"] = case_obj["owner"]

        omics_info["file_type"] = "methbat"

        # WHEN the OmicsVariantLoader model is parsed
        omics_model = OmicsVariantLoader(**omics_info).model_dump(by_alias=True, exclude_none=True)

        assert isinstance(omics_model["hgnc_ids"], list), "hgnc_ids should be a list"


def test_omics_variant_model_with_missing_hgnc_id(case_obj):
    """Test that the omics variant model is created correctly when hgnc_id is missing."""

    # GIVEN a parsed tsv omics dicts info array with missing hgnc_id
    omics_info = {
        "chrom": "chr6",
        "start": "144007487",
        "end": "144008719",
        "cpg_label": "notreallyalabel",
        "region_type": "nanoimprint",
        "hgnc_id": "",
        "hgnc_symbol": "PLAGL1",
        "summary_label": "AlleleSpecificMethylation",
        "compare_label": "Uncategorized",
        "sample_id": "ADM1059A2",
    }

    # GIVEN with required fields for the OmicsVariantLoader model
    for key in ["category", "sub_category", "variant_type", "analysis_type"]:
        omics_info[key] = ORDERED_OMICS_FILE_TYPE_MAP["methbat"][key]

    omics_info["case_id"] = case_obj["_id"]
    omics_info["build"] = case_obj["genome_build"]
    omics_info["institute"] = case_obj["owner"]

    omics_info["file_type"] = "methbat"

    # WHEN the OmicsVariantLoader model is parsed
    omics_model = OmicsVariantLoader(**omics_info).model_dump(by_alias=True, exclude_none=True)

    assert isinstance(omics_model["hgnc_symbols"], list), "hgnc_symbols should be a list"
