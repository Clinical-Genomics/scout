from pprint import pprint as pp
from cyvcf2 import VCF


def test_update_variant_rank_no_variants(real_populated_database):
    adapter = real_populated_database
    ## GIVEN a database without any variants
    assert sum(1 for i in adapter.variant_collection.find()) == 0
    case_obj = {"_id": "test"}
    ## WHEN Trying to update variant rank for nen existing variants
    adapter.update_variant_rank(case_obj, variant_type="clinical", category="snv")
    ## THEN assert that the operation was succesfull
    assert True


def test_load_variants_high_treshold(real_populated_database, case_obj):
    ## GIVEN a populated database and a case
    adapter = real_populated_database
    ## WHEN Trying to load variants where no one are above the rank score treshold
    vcf = VCF(case_obj["vcf_files"]["vcf_sv"])
    rankscore_treshold = 1000000
    individual_positions = {"ADM1059A2": 0, "ADM1059A1": 1, "ADM1059A3": 2}
    ## THEN assert that no variants are inserted
    nr_inserted = adapter._load_variants(
        vcf, "clinical", case_obj, individual_positions, rankscore_treshold, "cut000"
    )
    assert nr_inserted == 0
