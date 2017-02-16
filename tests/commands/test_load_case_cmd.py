# from scout.commands import cli
# from click.testing import CliRunner

vcf_file = "tests/fixtures/337334.clinical.vcf"
ped_file = "tests/fixtures/337334.ped"
scout_config = "tests/fixtures/scout_config_test.ini"

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
