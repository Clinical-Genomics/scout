# -*- coding: utf-8 -*-

from scout.commands import cli


def test_default_variant_evaluation_terms(mock_app, adapter):
    """Test loading default variant evaluation terms into database"""

    runner = mock_app.test_cli_runner()
    # GIVEN that the command for loading the default evaluation terms into database is executed
    result = runner.invoke(cli, ["load", "default-variant-evaluation-terms"], input="y")
    # THEN assert that the program exits without problems
    assert result.exit_code == 0
