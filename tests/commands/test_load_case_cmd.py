# -*- coding: utf-8 -*-

import os
from scout.demo import load_path

from scout.commands import app_cli
from scout.server.extensions import store
from scout.load.setup import setup_scout

def test_load_case(mock_app, institute_obj, case_obj):
    #Testing the 'scout load case command

    runner = mock_app.test_cli_runner()
    assert runner

    # first load demo data (all required document for uploading a case are there)
    setup_scout(adapter=store, demo=True)

    # There is one case in database
    assert store.case_collection.find().count() == 1
    assert store.institute_collection.find({'_id':'cust000'}).count()==1

    # remove case from database using adapter
    store.delete_case(case_id=case_obj['_id'])
    assert store.case_collection.find().count() == 0
    assert store.institute_collection.find({'_id':'cust000'}).count()==1

    # Make sure the scout config file is available
    assert os.path.exists(load_path)

    # Test command to upload case using demo resources:
    result =  runner.invoke(app_cli, ['load', 'case', load_path ])
    assert result.exit_code == 0
    assert store.case_collection.find().count() == 1





# from scout.commands import cli
# from click.testing import CliRunner
"""
vcf_file = "tests/fixtures/337334.clinical.vcf"
ped_file = "tests/fixtures/337334.ped"
scout_config = "tests/fixtures/scout_config_test.ini"
"""



# def test_load_database(database_setup):
#     """docstring for test_load_database"""
#     runner = CliRunner()
#     args = open(database_setup, 'r')
#     print(args.read())
#     result = runner.invoke(cli, [
#             '-c', database_setup,
#             'load',
#             '--vcf_file', vcf_file,
#             '--ped_file', ped_file,
#             '--family_type', 'ped',
#             '--owner', 'aowner',
#         ])
#     assert result.exit_code == 0
#
# def test_load_database_config(database_setup):
#     """docstring for test_load_database"""
#     runner = CliRunner()
#     args = open(database_setup, 'r')
#     result = runner.invoke(cli, [
#             '-c', database_setup,
#             'load',
#             '--scout_config_file', scout_config,
#         ])
#     assert result.exit_code == 0
#
#
# def test_load_database_no_vcf(database_setup, variant_file):
#     """docstring for test_load_database"""
#     runner = CliRunner()
#     args = open(database_setup, 'r')
#     result = runner.invoke(cli, [
#             '-c', database_setup,
#             'load',
#         ])
#     assert result.exit_code == 1
#
# def test_load_database_no_ped(database_setup, variant_file):
#     """docstring for test_load_database"""
#     runner = CliRunner()
#     args = open(database_setup, 'r')
#     result = runner.invoke(cli, [
#             '-c', database_setup,
#             'load',
#             '--vcf_file', vcf_file,
#         ])
#     assert result.exit_code == 1
#
# def test_load_database_no_owner(database_setup):
#     """docstring for test_load_database"""
#     runner = CliRunner()
#     args = open(database_setup, 'r')
#     print(args.read())
#     result = runner.invoke(cli, [
#             '-c', database_setup,
#             'load',
#             '--vcf_file', vcf_file,
#             '--ped_file', ped_file,
#             '--family_type', 'ped',
#         ])
#     assert result.exit_code == 1
