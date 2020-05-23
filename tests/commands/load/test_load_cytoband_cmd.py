# -*- coding: utf-8 -*-
from scout.commands import cli
from scout.server.extensions import store


def test_load_cytoband_no_build(mock_app):
    """Tests the function that load cytobands with no parameters"""

    # given a database not containing any cytobands
    assert store.cytoband_collection.find_one() is None

    runner = mock_app.test_cli_runner()

    # Running the command to upload cytobands
    result = runner.invoke(cli, ["load", "cytobands"])

    # Should not return error
    assert result.exit_code == 0

    # And cytobands should be uploaded in database
    # Both with build 37
    cytob_37 = store.cytoband_collection.find_one({"build": "37"})
    assert cytob_37 is not None
    # And build 38
    cytob_38 = store.cytoband_collection.find_one({"build": "38"})
    assert cytob_38 is not None


def test_load_cytoband_specific_build(mock_app):
    """Tests the function that load cytobands with build parameter"""

    # given a database not containing any cytobands
    assert store.cytoband_collection.find_one() is None

    runner = mock_app.test_cli_runner()

    # Running the command to upload cytobands
    result = runner.invoke(cli, ["load", "cytobands", "--build", "38"])

    # Should not return error
    assert result.exit_code == 0

    # Cytobands with build 38 should be in database
    cytob_38 = store.cytoband_collection.find_one({"build": "38"})
    assert cytob_38 is not None

    # But NOT cytobands with build 37
    cytob_37 = store.cytoband_collection.find_one({"build": "37"})
    assert cytob_37 is None
