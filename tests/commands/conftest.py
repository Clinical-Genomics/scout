"""Fixtures for CLI tests"""
import pathlib

import pytest

from scout.demo.resources import demo_files
from scout.server.app import create_app

#############################################################
###################### App fixtures #########################
#############################################################
# use this app object to test CLI commands which use a test database

DATABASE = "testdb"
REAL_DATABASE = "realtestdb"


@pytest.fixture(scope="function", name="demo_files")
def fixture_demo_files():
    """Return a dictionary with paths to the demo files"""
    return demo_files


@pytest.fixture(scope="function")
def demo_case_keys():
    """Returns a list of keys expected to be saved when demo case is loaded"""

    case_keys = [
        "_id",
        "analysis_date",
        "cnv_report",
        "cohorts",
        "collaborators",
        "coverage_qc_report",
        "created_at",
        "delivery_report",
        "display_name",
        "dynamic_gene_list",
        "gene_fusion_report",
        "gene_fusion_report_research",
        "genome_build",
        "group",
        "has_strvariants",
        "has_svvariants",
        "individuals",
        "is_migrated",
        "is_research",
        "lims_id",
        "madeline_info",
        "multiqc",
        "owner",
        "panels",
        "phenotype_terms",
        "rank_model_version",
        "rank_score_threshold",
        "rank_score_threshold",
        "rerun_requested",
        "research_requested",
        "smn_tsv",
        "status",
        "sv_rank_model_version",
        "synopsis",
        "track",
        "updated_at",
        "vcf_files",
    ]
    return case_keys


@pytest.fixture(scope="function")
def demo_individual_keys():
    """Returns a list of keys expected to be saved for an individual when demo case is loaded"""

    individual_keys = [
        "analysis_type",
        "bam_file",
        "capture_kits",
        "chromograph_images",
        "confirmed_parent",
        "confirmed_sex",
        "display_name",
        "father",
        "individual_id",
        "is_sma",
        "is_sma_carrier",
        "mother",
        "mt_bam",
        "phenotype",
        "predicted_ancestry",
        "rhocall_bed",
        "rhocall_wig",
        "rna_coverage_bigwig",
        "sex",
        "smn1_cn",
        "smn2_cn",
        "smn2delta78_cn",
        "smn_27134_cn",
        "splice_junctions_bed",
        "tiddit_coverage_wig",
        "tissue_type",
        "upd_regions_bed",
        "upd_sites_bed",
        "vcf2cytosure",
    ]
    return individual_keys


@pytest.fixture(scope="function")
def bam_path():
    """Return the path to a small existing bam file"""
    _path = pathlib.Path("tests/fixtures/bams/reduced_mt.bam")
    return _path
