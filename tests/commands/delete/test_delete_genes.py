from scout.commands import cli
from scout.server.extensions import store


def test_delete_genes(empty_mock_app, gene_bulk):
    "Test the CLI command that will delete genes"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN an adapter populated with genes
    assert store.hgnc_collection.find_one() is None
    store.hgnc_collection.insert_many(gene_bulk)
    assert store.hgnc_collection.find_one()

    ## WHEN removing them with CLI command
    result = runner.invoke(cli, ["delete", "genes", "-b", "37"])

    ## THEN should print "Dropping genes" message and drop all genes for build 37
    assert result.exit_code == 0
    assert "ropping genes collection for build: 37" in result.output
    assert store.hgnc_collection.find_one() is None


def test_delete_genes_one_build(empty_mock_app, gene_bulk_all):
    "Test the CLI command that will delete genes"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN an adapter populated with genes
    assert store.hgnc_collection.find_one() is None
    store.hgnc_collection.insert_many(gene_bulk_all)
    assert store.hgnc_collection.find_one()

    ## WHEN removing them with CLI command
    result = runner.invoke(cli, ["delete", "genes", "-b", "37"])

    ## THEN should print "Dropping genes" message and drop all genes for build 37
    assert result.exit_code == 0
    assert "ropping genes collection for build: 37" in result.output
    ## THEN the genes from build 37 should be gone
    assert store.hgnc_collection.find_one({"build": "37"}) is None
    ## THEN the genes from build 38 should be left
    assert store.hgnc_collection.find_one({"build": "38"})


def test_delete_all_genes_both_builds(empty_mock_app, gene_bulk_all):
    "Test the CLI command that will delete genes"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN an adapter populated with genes
    assert store.hgnc_collection.find_one() is None
    store.hgnc_collection.insert_many(gene_bulk_all)
    assert store.hgnc_collection.find_one()

    ## WHEN removing them with CLI command
    result = runner.invoke(cli, ["delete", "genes"])

    ## THEN should print "Dropping genes" message and drop all genes for build 37
    assert result.exit_code == 0
    assert "ropping all genes" in result.output
    ## THEN the genes from build 37 should be gone
    assert store.hgnc_collection.find_one() is None


def test_delete_exons_37(empty_mock_app):
    "Test the CLI command that will delete exons"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    exon_objs = [
        {"_id": "mock_exon_1", "build": "37"},
        {"_id": "mock_exon_2", "build": "37"},
        {"_id": "mock_exon_3", "build": "38"},
    ]
    ## GIVEN a database with some exons
    store.exon_collection.insert_many(exon_objs)
    assert store.exon_collection.find_one()

    ## WHEN using the CLI to remove all exons with build == 38
    result = runner.invoke(cli, ["delete", "exons", "-b", "38"])

    ## THEN the command should exit without errors
    assert result.exit_code == 0
    ## THEN there should be no exons with build 38
    assert store.exon_collection.find_one({"build": "38"}) is None
    ## THEN there should be exons left with build 37
    assert store.exon_collection.find_one({"build": "37"})

    # Use the CLI to remove all exons regardless:
    result = runner.invoke(cli, ["delete", "exons"])

    # and all exons should be removed
    assert result.exit_code == 0
    assert sum(1 for _ in store.exon_collection.find()) == 0


def test_delete_exons(empty_mock_app):
    "Test the CLI command that will delete exons"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    exon_objs = [
        {"_id": "mock_exon_1", "build": "37"},
        {"_id": "mock_exon_2", "build": "37"},
        {"_id": "mock_exon_3", "build": "38"},
    ]
    ## GIVEN a database with some exons
    store.exon_collection.insert_many(exon_objs)
    assert store.exon_collection.find_one()

    ## WHEN using the CLI to remove all exons
    result = runner.invoke(cli, ["delete", "exons"])

    ## THEN the command should exit without errors
    assert result.exit_code == 0
    ## THEN there should be no exons left
    assert store.exon_collection.find_one() is None
