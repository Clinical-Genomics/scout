"""Tests for server utils"""
import tempfile
from datetime import datetime
from io import BytesIO

import pytest
from bson.objectid import ObjectId
from flask import url_for

from scout.server.links import get_variant_links
from scout.server.utils import (
    append_safe,
    case_has_alignments,
    case_has_mt_alignments,
    document_generated,
    find_index,
    html_to_pdf_file,
)


def test_objectid_generated_valid_objid():
    """Test the function that returns the timestamp of a certain Mongo ObjectId for a document"""
    # GIVEN a database document  ObjectId
    objid = ObjectId("6270e450615e1675f40b5ce4")

    # THEN document_generated should return a timestamp
    assert isinstance(document_generated(objid), datetime)


def test_objectid_generated_none():
    """Test the function that returns the timestamp of a MondoDB ObjectId when the ObjectId has wrong type"""

    # GIVEN an id of different type than ObjectId
    objid = None
    # THEN document_generated should return None
    assert document_generated(objid) is None


def test_case_has_alignments(case_obj):
    """Test function that adds info on availability of autosomal alignment files for a case"""

    # GIVEN a case with no autosomal alignment files
    for ind in case_obj["individuals"]:
        assert ind["bam_file"] is None

    # THEN case_has_alignments should assign bam_files = False to a case
    assert case_obj.get("bam_files") is None
    case_has_alignments(case_obj)
    assert case_obj["bam_files"] is False


def test_case_has_mt_alignments(case_obj):
    """Test function that adds info on availability of MT alignment files for a case"""

    # GIVEN a case with MT alignment files
    for ind in case_obj["individuals"]:
        assert ind["mt_bam"]

    # THEN case_has_alignments should assign mt_bams = True to a case
    assert case_obj.get("mt_bams") is None
    case_has_mt_alignments(case_obj)
    assert case_obj["mt_bams"] is True


def test_html_to_pdf_file():
    """Test function that converts HTML file into pdf file using PDFKit"""

    test_content = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>A demo html page</title>
        </head>
        <body>
        <p>Hello world!</p>
        </body>
        </html>
    """

    # GIVEN an HTML report to be converted to PDF:
    bytes_file = html_to_pdf_file(test_content, "landscape", 300)
    assert isinstance(bytes_file, BytesIO)


def test_get_variant_links(app, institute_obj, variant_obj):
    """Test to get 1000g link"""
    # GIVEN a variant object without links
    assert "thousandg_link" not in variant_obj

    # WHEN fetching the variant links
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        links = get_variant_links(institute_obj, variant_obj)
        # THEN check that links are returned
        assert "thousandg_link" in links


def test_get_str_variant_links(app, institute_obj, str_variant_obj):
    """Test adding links to STR variant obj, in particular check source link."""
    # GIVEN a variant object without links
    assert "str_source_link" not in str_variant_obj
    # WHEN fetching the variant links
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        links = get_variant_links(institute_obj, str_variant_obj)
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
