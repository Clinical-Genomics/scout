# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_view_individuals(mock_app, case_obj):
    """Test CLI that shows all individuals from all cases in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without arguments
    result = runner.invoke(cli, ["view", "individuals"])
    assert result.exit_code == 0
    # command should return data
    assert "ADM1059A1\tNA12877\tmale\tunaffected" in result.output

    # Test CLI providing case_id
    result = runner.invoke(cli, ["view", "individuals", "-c", case_obj["_id"]])
    assert result.exit_code == 0
    # command should return data
    assert "ADM1059A1\tNA12877\tmale\tunaffected" in result.output

    # Test CLI providing case_id that is not in database
    result = runner.invoke(cli, ["view", "individuals", "-c", "unknowkn_case_id"])
    assert result.exit_code == 0
    # command should NOT return data
    assert "Could not find case unknowkn_case_id" in result.output

    # Test CLI providing institute id
    result = runner.invoke(cli, ["view", "individuals", "-i", case_obj["owner"]])
    assert result.exit_code == 0
    # command should return data
    assert "ADM1059A1\tNA12877\tmale\tunaffected" in result.output

    # Test CLI providing institute id not in database
    result = runner.invoke(cli, ["view", "individuals", "-i", "cust666"])
    assert result.exit_code == 0
    # command should NOT return data
    assert "Could not find cases that match criteria" in result.output

    # Test CLI to show individuals for cases with causative variants
    result = runner.invoke(cli, ["view", "individuals", "--causatives"])
    assert result.exit_code == 0
    # command should NOT return data
    assert "Could not find cases that match criteria" in result.output

    # register a causative for the existing case in database
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"causatives": ["causative_id"]}}
    )

    # Test CLI to show individuals for cases with causative variants
    result = runner.invoke(cli, ["view", "individuals", "--causatives"])
    assert result.exit_code == 0
    # command should return data this time
    assert "ADM1059A1\tNA12877\tmale\tunaffected" in result.output
