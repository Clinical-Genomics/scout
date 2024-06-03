from pprint import pprint as pp

import pytest
from cyvcf2 import VCF

from scout.build import build_variant
from scout.exceptions.database import IntegrityError
from scout.parse.variant import parse_variant
from scout.parse.variant.headers import parse_rank_results_header, parse_vep_header
from scout.parse.variant.rank_score import parse_rank_score
from scout.server.blueprints.variants.controllers import variants


def test_compounds_region(real_populated_database, case_obj, variant_clinical_file):
    """When loading the variants not all variants will be loaded, only the ones that
    have a rank score above a treshold.
    This implies that some compounds will have the status 'not_loaded'=True.
    When loading all variants for a region then all variants should
    have status 'not_loaded'=False.
    """
    adapter = real_populated_database
    variant_type = "clinical"
    category = "snv"
    ## GIVEN a database without any variants
    assert adapter.variant_collection.find_one() is None

    institute_obj = adapter.institute_collection.find_one()
    institute_id = institute_obj["_id"]

    ## WHEN loading variants into the database without updating compound information

    vcf_obj = VCF(variant_clinical_file)
    rank_results_header = parse_rank_results_header(vcf_obj)
    vep_header = parse_vep_header(vcf_obj)

    individual_positions = {}
    for i, ind in enumerate(vcf_obj.samples):
        individual_positions[ind] = i

    variants = []
    for i, variant in enumerate(vcf_obj):
        parsed_variant = parse_variant(
            variant=variant,
            case=case_obj,
            variant_type="clinical",
            rank_results_header=rank_results_header,
            vep_header=vep_header,
            individual_positions=individual_positions,
            category="snv",
        )

        variant_obj = build_variant(variant=parsed_variant, institute_id=institute_id)
        variants.append(variant_obj)

    # Load all variants
    adapter.variant_collection.insert_many(variants)

    print("Nr variants: {0}".format(len(variants)))

    ## THEN assert that the variants does not have updated compound information
    nr_compounds = 0
    for var in adapter.variant_collection.find():
        if not var.get("compounds"):
            continue
        for comp in var["compounds"]:
            if "genes" in comp:
                assert False
            if "not_loaded" in comp:
                assert False
            nr_compounds += 1

    assert nr_compounds > 0

    ## WHEN updating all compounds for a case
    adapter.update_case_compounds(case_obj)
    hgnc_ids = set([gene["hgnc_id"] for gene in adapter.all_genes()])

    nr_compounds = 0
    ## THEN assert that all compounds  (within the gene defenition) are updated
    for var in adapter.variant_collection.find():
        cont = False
        for hgnc_id in var["hgnc_ids"]:
            if hgnc_id not in hgnc_ids:
                cont = True
        if cont:
            continue
        if not var.get("compounds"):
            continue
        for comp in var["compounds"]:
            nr_compounds += 1
            if not "genes" in comp:
                # pp(var)
                assert False
            if not "not_loaded" in comp:
                assert False
    assert nr_compounds > 0
