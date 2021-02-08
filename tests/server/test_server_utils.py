"""Tests for server utils"""
import tempfile
import pytest
from scout.server.links import get_variant_links
from scout.server.utils import append_safe, find_index, variant_case


def test_get_variant_links(variant_obj):
    """Test to get 1000g link"""
    # GIVEN a variant object without links
    assert "thousandg_link" not in variant_obj
    # WHEN fetching the variant links
    links = get_variant_links(variant_obj)
    # THEN check that links are returned
    assert "thousandg_link" in links


def test_get_str_variant_links(str_variant_obj):
    """Test adding links to STR variant obj, in particular check source link."""
    # GIVEN a variant object without links
    assert "str_source_link" not in str_variant_obj
    # WHEN fetching the variant links
    links = get_variant_links(str_variant_obj)
    # THEN check that links are returned
    assert "str_source_link" in links


def test_find_index_bai():
    """Test to find a bam index"""
    # GIVEN a case with this type of alignment files
    # bam_file.bam
    # bam_file.bai
    with tempfile.TemporaryDirectory() as tmpdirname:
        with tempfile.NamedTemporaryFile(dir=tmpdirname, suffix=".bai") as idx:

            bam_file = idx.name.replace(".bai", ".bam")
            # THEN the find_index function should return the correct index file
            index = find_index(bam_file)
            assert index.endswith("bam.bai") is False
            assert index.endswith(".bai")


def test_find_index_bam_bai():
    """Test to find a bam index"""
    # GIVEN a case with this type of alignment files
    # bam_file.bam
    # bam_file.bam.bai
    with tempfile.TemporaryDirectory() as tmpdirname:
        with tempfile.NamedTemporaryFile(dir=tmpdirname, suffix="bam.bai") as idx:

            bam_file = idx.name.replace(".bai", "")
            # THEN the find_index function should return the correct index file
            index = find_index(bam_file)
            assert index.endswith("bam.bai")


def test_find_index_crai():
    """Test to find a cram index"""
    # GIVEN a case with this type of alignment files
    # bam_file.cram
    # bam_file.crai
    with tempfile.TemporaryDirectory() as tmpdirname:
        with tempfile.NamedTemporaryFile(dir=tmpdirname, suffix=".crai") as idx:

            cram_file = idx.name.replace(".crai", ".cram")
            # THEN the find_index function should return the correct index file
            index = find_index(cram_file)
            assert index.endswith("cram.crai") is False
            assert index.endswith(".crai")


def test_find_index_cram_crai():
    """Test to find a cram index"""
    # GIVEN a case with this type of alignment files
    # bam_file.cram
    # bam_file.cram.crai
    with tempfile.TemporaryDirectory() as tmpdirname:
        with tempfile.NamedTemporaryFile(dir=tmpdirname, suffix="cram.crai") as idx:

            cram_file = idx.name.replace(".crai", "")
            # THEN the find_index function should return the correct index file
            index = find_index(cram_file)
            assert index.endswith("cram.crai")


def test_append_safe_no_except():
    """Test to append_safe"""
    # GIVEN a simple dict with list
    a_dict = {"a": [1]}

    # WHEN calling append_safe
    append_safe(a_dict, "a", 2)

    # THEN append_safe() will append elem at index
    assert a_dict == {"a": [1, 2]}


def test_append_safe_except():
    """Test to append_safe empty dict"""
    # GIVEN a simple dict with list
    a_dict = {}

    # WHEN calling append() on a empty dict
    # THEN KeyError exception is raised
    with pytest.raises(KeyError):
        a_dict["2"].append(2)

    # WHEN calling append_safe() on a empty
    append_safe(a_dict, "a", 2)

    # THEN list.append exception is caught in try/except and
    # program execution continues
    assert a_dict == {"a": [2]}


def test_variant_case_no_genes(adapter, case_obj, variant_obj):
    """Test to preprocess a variant"""
    # GIVEN a variant wihtout gene info
    assert variant_obj.get("genes") is None
    # GIVEN that no region vcf exists
    assert "region_vcf_file" not in case_obj
    # WHEN adding info
    variant_case(adapter, case_obj, variant_obj)
    # THEN assert no region vcf was added since there where no gene info
    assert "region_vcf_file" not in case_obj


def test_variant_case(adapter, case_obj, variant_obj):
    """Test to preprocess a variant"""
    # GIVEN a variant WITH gene info
    variant_obj["genes"] = [
        {"hgnc_id": 1},
        {"hgnc_id": 2, "common": {"chromosome": "1", "start": "10", "end": "100"}},
    ]
    # GIVEN a variant without gene info
    assert case_obj.get("region_vcf_file") is None
    variant_case(adapter, case_obj, variant_obj)
    # THEN assert that the region VCF was created
    assert case_obj.get("region_vcf_file") is not None
