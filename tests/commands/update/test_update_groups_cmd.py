# -*- coding: utf-8 -*-
import os

from scout.commands import cli
from scout.server.extensions import store


def test_update_groups(mock_app, tmpdir):
    """Tests the CLI that updates phenotype groups"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["update", "groups"])
    assert "Error: Missing argument" in result.output

    # Test CLI base with istitute id argument
    result = runner.invoke(cli, ["update", "groups", "cust000"])
    assert "INFO Please provide some groups" in result.output

    # add a couple of term to database
    hpo_terms = [
        {
            "_id": "HP:0000003",
            "hpo_id": "HP:0000003",
            "hpo_number": 3,
            "description": "Multicystic kidney dysplasia",
            "genes": [17582, 1151],
        },
        {
            "_id": "HP:0000331",
            "hpo_id": "HP:0000331",
            "hpo_number": 331,
            "description": "Short chin",
            "genes": [13890],
        },
    ]
    store.hpo_term_collection.insert_many(hpo_terms)

    # Test CLI with new phenotype group
    result = runner.invoke(cli, ["update", "groups", "cust000", "-p", "HP:0000003"])
    assert result.exit_code == 0
    assert "Institute updated" in result.output
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["phenotype_groups"]["HP:0000003"]["abbr"] is None

    # Test CLI with new phenotype group and abbreviation
    result = runner.invoke(cli, ["update", "groups", "cust000", "-p", "HP:0000003", "-a", "ABBR1"])
    assert result.exit_code == 0
    assert "Institute updated" in result.output
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["phenotype_groups"]["HP:0000003"]["abbr"] == "ABBR1"

    # create a mock phenotype group file
    phenotype_group_text = """#comment line\nHP:0000331\tABBR2\n"""
    p = tmpdir.mkdir("sub").join("pheno_groups.csv")
    p.write(phenotype_group_text)
    assert p.read() == phenotype_group_text

    # Pass the file to the CLI with -add flag
    result = runner.invoke(cli, ["update", "groups", "cust000", "-f", str(p), "-add"])
    assert result.exit_code == 0
    assert "Institute updated" in result.output
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["phenotype_groups"]["HP:0000003"]["abbr"] == "ABBR1"
    assert updated_institute["phenotype_groups"]["HP:0000331"]["abbr"] == "ABBR2"

    # Pass the same file to CLI with no add flag (if should replace the phenotype_groups object)
    result = runner.invoke(cli, ["update", "groups", "cust000", "-f", str(p)])
    assert result.exit_code == 0
    assert "Institute updated" in result.output
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["phenotype_groups"]["HP:0000331"]["abbr"] == "ABBR2"
    # first HPO term should not be found in phenotype groups now
    assert "HP:0000003" not in updated_institute["phenotype_groups"]
