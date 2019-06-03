# -*- coding: utf-8 -*-

from scout.commands import cli

def test_load_variants(mock_app, case_obj):
    """Testing the load variants cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI providing only case_id (required)
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id']])
    assert result.exit_code == 0
    assert "No files where specified to upload variants from" in result.output

    # Test CLI by uploading SNV variants for a case
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--snv',
        '--rank-treshold', 10
        ])
    assert result.exit_code == 0

    # Test CLI by uploading SNV research variants for a case
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--snv-research',
        '--force'
        ])
    assert result.exit_code == 0

    # Test CLI by uploading SV variants for a case
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--sv'
        ])
    assert result.exit_code == 0

    # Test CLI by uploading SV research variants for a case
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--sv-research',
        '--force'
        ])
    assert result.exit_code == 0

    # Test CLI by uploading str clinical variants for a case
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--str-clinical'
        ])
    assert result.exit_code == 0

    # Test CLI by uploading variants for a hgnc_id
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--hgnc-id', 170
        ])
    assert result.exit_code == 0

    # Test CLI by uploading variants for a gene symbol
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--hgnc-symbol', 'ACTR3'
        ])
    assert result.exit_code == 0

    # Test CLI by uploading variants for given coordinates
    result =  runner.invoke(cli, ['load', 'variants', case_obj['_id'],
        '--chrom', '3',
        '--start', 60090,
        '--end', 78000
        ])
    assert result.exit_code == 0
