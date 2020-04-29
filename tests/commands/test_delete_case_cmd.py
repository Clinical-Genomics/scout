# from scout.commands import cli
# from click.testing import CliRunner

# def test_delete_case(setup_loaded_database, database_setup):
#     #Check that a case have been added
#     case = setup_loaded_database.case(
#         institute_id='cust000',
#         case_id='337334'
#     )
#     assert case
#     case_id = case.case_id
#     nr_of_variants = 0
#     variants = setup_loaded_database.variants(
#         case_id=case_id,
#         query=None,
#         variant_ids=None,
#         nr_of_variants=10000,
#         skip=0
#     )
#     #Check that the variants are added
#     for variant in variants:
#         nr_of_variants += 1
#     assert nr_of_variants == 207
#
#     #Test to delete the case
#     runner = CliRunner()
#     args = open(database_setup, 'r')
#     result = runner.invoke(cli, [
#             '-c', database_setup,
#             'delete_case',
#             '--owner', 'cust000',
#             '--case_id', '337334',
#         ])
#     assert result.exit_code == 0
#     case = setup_loaded_database.case(
#         institute_id='cust000',
#         case_id='337334'
#     )
#     assert case is None
#
#     variants = setup_loaded_database.variants(
#         case_id=case_id,
#         query=None,
#         variant_ids=None,
#         nr_of_variants=10,
#         skip=0
#     )
#     #Check that the variants are deleted
#     nr_of_variants = 0
#     for variant in variants:
#         nr_of_variants += 1
#     assert nr_of_variants == 0
#
