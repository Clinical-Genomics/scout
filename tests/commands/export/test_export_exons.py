# -*- coding: utf-8 -*-
from scout.commands import cli
from scout.server.extensions import store

test_exon = {
    "exon_id": "1-1167658-1168649",
    "chrom": "1",
    "start": 1167658,
    "end": 1168649,
    "transcript": "ENST00000379198",
    "hgnc_id": 17978,
    "rank": 1,
    "strand": 1,
    "build": "37",
}

test_transcript = {
    "ensembl_transcript_id": "ENST00000379198",
    "hgnc_id": 17978,
    "chrom": "1",
    "start": 1167629,
    "end": 1170421,
    "is_primary": True,
    "refseq_id": "NM_080605",
    "refseq_identifiers": ["NM_080605"],
    "build": "37",
    "length": 2792,
}


def test_export_exons_one_gene(mock_app, gene_obj):
    """Test the CLI command that exports the exons of one gene"""

    runner = mock_app.test_cli_runner()

    # GIVEN a database with a gene
    assert store.hgnc_collection.insert_one(gene_obj)

    # with at least one exon:
    assert store.exon_collection.insert_one(test_exon)

    # WHEN the command to export exons from test gene is invoked
    result = runner.invoke(cli, ["export", "exons", "-b", "37", "-hgnc", gene_obj["hgnc_id"]])
    # it should return the exon
    assert result.exit_code == 0
    assert test_exon["exon_id"] in result.output


def test_export_exons(mock_app, gene_obj):
    """Test the CLI command that exports all exons for a given genome build"""

    runner = mock_app.test_cli_runner()

    # GIVEN a database with a gene
    assert store.hgnc_collection.insert_one(gene_obj)

    # HAVING a transcript
    assert store.transcript_collection.insert_one(test_transcript)

    # AND an exon
    assert store.exon_collection.insert_one(test_exon)

    # WHEN the the command to export all exons is invoked
    result = runner.invoke(cli, ["export", "exons", "-b", "37"])

    # it should return the exon
    assert result.exit_code == 0
    assert test_exon["exon_id"] in result.output


def test_export_exons_gene_json(mock_app, gene_obj):
    """Test the CLI command that exports all exons a gene on json format"""

    runner = mock_app.test_cli_runner()

    # GIVEN a database with a gene
    assert store.hgnc_collection.insert_one(gene_obj)

    # with at least one exon:
    assert store.exon_collection.insert_one(test_exon)

    # WHEN the command to json-export exons from test gene is invoked
    result = runner.invoke(cli, ["export", "exons", "-hgnc", gene_obj["hgnc_id"], "--json"])
    assert result.exit_code == 0
    # THEN it should return a document
    assert "$oid" in result.output
    # With test exon
    assert test_exon["exon_id"] in result.output


def test_export_exons_json(mock_app, gene_obj):
    """Test the CLI command that exports all exons in json format"""

    runner = mock_app.test_cli_runner()

    # GIVEN a database with a gene
    assert store.hgnc_collection.insert_one(gene_obj)

    # HAVING a transcript
    assert store.transcript_collection.insert_one(test_transcript)

    # AND an exon
    assert store.exon_collection.insert_one(test_exon)

    # WHEN the the command to json-export all exons is invoked
    result = runner.invoke(cli, ["export", "exons", "-b", "37", "--json"])
    assert result.exit_code == 0

    # THEN it should return a document
    assert "$oid" in result.output
    # With test exon
    assert test_exon["exon_id"] in result.output
