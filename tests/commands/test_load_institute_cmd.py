# from scout.commands import cli
# from click.testing import CliRunner
# import scout.adapter
# import pytest
#
# def test_load_database(database_name):
#
#     runner = CliRunner()
#     result = runner.invoke(cli, [
#             '-db', database_name,
#             '--loglevel', 'DEBUG',
#             'load',
#             'institute',
#             '--internal_id', 'cust000',
#             '--display_name', 'test',
#         ])
#     assert result.exit_code == 0
