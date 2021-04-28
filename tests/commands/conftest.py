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

    demo_case_keys = [
        "_id",
        "display_name",
        "owner",
        "collaborators",
        "smn_tsv",
        "individuals",
        "created_at",
        "updated_at",
        "synopsis",
        "status",
        "is_research",
        "research_requested",
        "rerun_requested",
        "lims_id",
        "analysis_date",
        "panels",
        "dynamic_gene_list",
        "genome_build",
        "rank_model_version",
        "sv_rank_model_version",
        "rank_score_threshold",
        "rank_score_threshold",
        "cohorts",
        "phenotype_terms",
        "madeline_info",
        "multiqc",
        "cnv_report",
        "coverage_qc_report",
        "gene_fusion_report",
        "gene_fusion_report_research",
        "vcf_files",
        "delivery_report",
        "has_svvariants",
        "has_strvariants",
        "is_migrated",
        "track",
        "group",
    ]
    return demo_case_keys


@pytest.fixture(scope="function")
def bam_path():
    """Return the path to a small existing bam file"""
    _path = pathlib.Path("tests/fixtures/bams/reduced_mt.bam")
    return _path
