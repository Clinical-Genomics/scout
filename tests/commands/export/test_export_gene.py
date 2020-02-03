# -*- coding: utf-8 -*-

import json

from scout.commands import cli
from scout.server.extensions import store


def test_export_genes(mock_app):
    """Test the CLI command that exports a HGNC gene"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test the export panel cli without passing any data to get all genes (build 37)
    result = runner.invoke(cli, ["export", "genes"])
    # assert that genes are returned
    assert result.exit_code == 0
    assert "Y\t14813160\t14972764\t12633\tUSP9Y\n" in result.output

    # insert a gene in build 38 into database
    gene_info_38 = {
        "hgnc_id": 29609,
        "hgnc_symbol": "ACP6",
        "ensembl_id": "ENSG00000162836",
        "chromosome": "1",
        "start": 147629652,
        "end": 147670496,
        "build": "38",
    }
    store.hgnc_collection.insert_one(gene_info_38)
    assert sum(1 for i in store.hgnc_collection.find({"build": "38"})) == 1

    # Test the export panel cli by passing build=38
    result = runner.invoke(cli, ["export", "genes", "-b", "38"])
    # assert that gene is returned
    assert result.exit_code == 0
    assert "1\t147629652\t147670496\t29609\tACP6\n" in result.output

    # Test CLI to return json-formatted genes
    result = runner.invoke(cli, ["export", "genes", "-b", "38", "--json"])
    # assert that gene is returned
    assert result.exit_code == 0
    assert 'hgnc_symbol": "ACP6", "ensembl_id": "ENSG00000162836"' in result.output

    # Test exporting a gene in genome build GRCh38
    # Test the export panel cli by passing build=GRCh38
    result = runner.invoke(cli, ["export", "genes", "-b", "GRCh38"])
    # assert that gene is returned
    assert result.exit_code == 0
    assert "1\t147629652\t147670496\t29609\tACP6\n" in result.output

    # Test CLI to return json-formatted genes
    result = runner.invoke(cli, ["export", "genes", "-b", "GRCh38", "--json"])
    assert result.exit_code == 0
    assert 'hgnc_symbol": "ACP6", "ensembl_id": "ENSG00000162836"' in result.output
