# -*- coding: utf-8 -*-

from scout.commands import app_cli
from scout.server.extensions import store

def test_export_variants(mock_app, case_obj):
    """Test the CLI command that exports causatives into vcf format"""

    runner = mock_app.test_cli_runner()
    assert runner

    # There are no variants in mock app database
    assert store.variant_collection.find().count() == 0

    # Load snv variants using the cli
    result =  runner.invoke(app_cli, ['load', 'variants', case_obj['_id'],
        '--snv',
        ])
    assert store.variant_collection.find().count() > 0

    # update case registering a causatove variant
    variant_obj = store.variant_collection.find_one()
    store.case_collection.find_one_and_update(
        {'_id' : case_obj['_id'] },
        {'$set' : {'causatives' : [variant_obj['_id']]} }
    )
    assert store.case_collection.find({'causatives':{'$exists': True}}).count() == 1

    # Test the cli by not providing any options or arguments
    result =  runner.invoke(app_cli, ['export', 'variants'])
    assert result.exit_code == 0
    assert '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO' in result.output
    # variant should be returned
    assert str(variant_obj['position']) in result.output


    # Test the cli by providing wrong collaborator
    result =  runner.invoke(app_cli, ['export', 'variants',
        '-c', 'cust666'
    ])
    assert result.exit_code == 0
    assert '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO' in result.output
    # variant should NOT be returned
    assert str(variant_obj['position']) not in result.output


    # Test the cli by providing the right collaborator
    result =  runner.invoke(app_cli, ['export', 'variants',
        '-c', case_obj['owner']
    ])
    assert result.exit_code == 0
    assert '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO' in result.output
    # variant should be returned
    assert str(variant_obj['position']) in result.output


    # Test the cli by providing the document_id of the variant
    result =  runner.invoke(app_cli, ['export', 'variants',
        '-d', variant_obj['document_id']
    ])
    assert result.exit_code == 0
    assert '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO' in result.output
    # variant should be returned
    assert str(variant_obj['position']) in result.output


    # Test the cli by providing the case_id of the variant
    result =  runner.invoke(app_cli, ['export', 'variants',
        '--case-id', case_obj['_id']
    ])
    assert result.exit_code == 0
    assert '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO' in result.output
    # variant should be returned
    assert str(variant_obj['position']) in result.output


    # Test the cli by providing the case_id of the variantand and json option
    result =  runner.invoke(app_cli, ['export', 'variants',
        '--case-id', case_obj['_id'],
        '--json'
    ])
    assert result.exit_code == 0
    assert '#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO' not in result.output
    # variant should be returned
    assert str(variant_obj['position']) in result.output
    assert '"position": {}'.format(variant_obj['position']) in result.output
