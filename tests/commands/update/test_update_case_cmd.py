# -*- coding: utf-8 -*-
from scout.demo import clinical_snv_path, clinical_sv_path

from scout.commands import cli
from scout.server.extensions import store

def test_update_case(mock_app, case_obj):
    """Tests the CLI that updates a case"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result =  runner.invoke(cli, ['update', 'case'])

    # it should return error message
    assert 'Please specify which case to update' in result.output

    # provide a case id
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        ])
    assert 'INFO Fetching case {}'.format(case_obj['_id']) in result.output

    # provide a case id and a collaborator whis is not valid
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '-c', 'cust666'
        ])
    assert 'Institute cust666 could not be found' in result.output

    # provide a case id and a valid collaborator
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '-c', 'cust000'
        ])
    assert 'INFO Fetching case {}'.format(case_obj['_id']) in result.output

    # try first to remove collaborator from case object and to add it via the CLI
    store.case_collection.find_one_and_update(
        {'_id': case_obj['_id']},
        {'$set' : {'collaborators' : [] }}
    )
    assert store.case_collection.find({
        '_id': case_obj['_id'], 'collaborators' : []
    }).count() == 1
    # provide a case id and a valid collaborator and see that collaborator is added to case
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '-c', 'cust000'
        ])
    assert 'INFO Fetching case {}'.format(case_obj['_id']) in result.output
    assert result.exit_code == 0
    assert 'Adding collaborator' in result.output
    assert store.case_collection.find({
        '_id': case_obj['_id'], 'collaborators' : ['cust000']
    }).count() == 1


    # Test cli to update vcf
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--vcf', clinical_snv_path
        ])
    result.exit_code == 0
    assert 'INFO Case updated' in result.output
    assert store.case_collection.find({
        'vcf_files.vcf_snv' : clinical_snv_path
    }).count() == 1


    # Test cli to update vcf-sv
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--vcf-sv', clinical_snv_path
        ])
    result.exit_code == 0
    assert 'INFO Case updated' in result.output
    assert store.case_collection.find({
        'vcf_files.vcf_sv' : clinical_snv_path
    }).count() == 1


    # Test cli to update vcf-cancer
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--vcf-cancer', clinical_snv_path
        ])
    result.exit_code == 0
    assert 'INFO Case updated' in result.output
    assert store.case_collection.find({
        'vcf_files.vcf_cancer' : clinical_snv_path
    }).count() == 1


    # Test cli to update vcf-research
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--vcf-research', clinical_snv_path
        ])
    result.exit_code == 0
    assert 'INFO Case updated' in result.output
    assert store.case_collection.find({
        'vcf_files.vcf_research' : clinical_snv_path
    }).count() == 1


    # Test cli to update vcf-sv-research
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--vcf-sv-research', clinical_snv_path
        ])
    result.exit_code == 0
    assert 'INFO Case updated' in result.output
    assert store.case_collection.find({
        'vcf_files.vcf_sv_research' : clinical_snv_path
    }).count() == 1


    # Test cli to update vcf-cancer-research
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--vcf-cancer-research', clinical_snv_path
        ])
    result.exit_code == 0
    assert 'INFO Case updated' in result.output
    assert store.case_collection.find({
        'vcf_files.vcf_cancer_research' : clinical_snv_path
    }).count() == 1


    # Test cli to reupload SVs with rank threshold
    # First save right file to upload SV variants from
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--vcf-sv', clinical_sv_path
        ])
    result.exit_code == 0
    assert 'INFO Case updated' in result.output

    # then lauch the --reupload-sv command
    result =  runner.invoke(cli, ['update', 'case',
        case_obj['_id'],
        '--reupload-sv',
        '--rankscore-treshold', 10,
        '--sv-rankmodel-version', 1.5
        ])
    result.exit_code == 0
    assert '0 variants deleted' in result.output # there were no variants in variant collection
    assert store.variant_collection.find({'category':'sv'}).count() >0
    assert store.variant_collection.find({
        'category':'sv',
        'variant_rank' : {'$gt' : 10}
        }).count() == 0
    assert store.case_collection.find({'sv_rank_model_version' : 1.5}).count() >0
