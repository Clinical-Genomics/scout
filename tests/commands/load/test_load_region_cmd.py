# -*- coding: utf-8 -*-

import pytest

from scout.commands import cli


def test_load_region(mock_app, case_obj):
    """Testing the load region cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test load region using case_id
    result = runner.invoke(cli, ["load", "region", "--case-id", case_obj["_id"]])
    assert result.exit_code == 0

    with pytest.warns(
        UserWarning
    ):  # The command will raise a UserWarning: no intervals found for b'scout/demo/643594.clinical.SV.vcf.gz' at 2:114647537-114720173
        # test load region using case_id + hgnc_id:
        result = runner.invoke(
            cli, ["load", "region", "--case-id", case_obj["_id"], "--hgnc-id", 170]
        )
        assert result.exit_code == 0

        # test load region using case_id + coordinates
        result = runner.invoke(
            cli,
            [
                "load",
                "region",
                "--case-id",
                case_obj["_id"],
                "--chromosome",
                "2",
                "--start",
                114647537,
                "--end",
                114720173,
            ],
        )
        assert result.exit_code == 0
