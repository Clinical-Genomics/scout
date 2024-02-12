from pprint import pprint as pp

import pytest
from cyvcf2 import VCF

from scout.build.managed_variant import build_managed_variant
from scout.constants import REV_CLINSIG_MAP
from scout.exceptions.database import IntegrityError
from scout.parse.variant import parse_variant
from scout.server.blueprints.variants.controllers import variants


def test_load_variant(real_populated_database, variant_obj):
    """Test to load a variant into a real mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find_one() is None

    # WHEN loading a variant into the database
    adapter.load_variant(variant_obj=variant_obj)
    # THEN assert the variant is loaded

    assert adapter.variant_collection.find_one()


def test_load_variant_twice(real_populated_database, variant_obj):
    """Test to load a variant into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    # WHEN loading a variant into the database twice
    adapter.load_variant(variant_obj=variant_obj)

    # THEN a IntegrityError should be raised
    with pytest.raises(IntegrityError):
        adapter.load_variant(variant_obj=variant_obj)


def test_load_vep97_parsed_variant(one_vep97_annotated_variant, real_populated_database, case_obj):
    """test first parsing and then loading a vep v97 annotated variant"""

    # GIVEN a variant annotated using the following CSQ entry fields
    csq_header = "Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|REFSEQ_MATCH|SOURCE|GIVEN_REF|USED_REF|BAM_EDIT|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|LoFtool|ExACpLI|GERP++_NR|GERP++_RS|REVEL_rankscore|phastCons100way_vertebrate|phyloP100way_vertebrate|CLINVAR|CLINVAR_CLNSIG|CLINVAR_CLNVID|CLINVAR_CLNREVSTAT|genomic_superdups_frac_match"

    header = [word.upper() for word in csq_header.split("|")]

    # WHEN parsed using
    parsed_vep97_annotated_variant = parse_variant(
        variant=one_vep97_annotated_variant, vep_header=header, case=case_obj
    )

    # GIVEN a database without any variants
    adapter = real_populated_database
    assert adapter.variant_collection.find_one() is None

    # WHEN loading the variant into the database
    adapter.load_variant(variant_obj=parsed_vep97_annotated_variant)

    # THEN the variant is loaded with the fields correctly parsed
    # revel score
    variant = adapter.variant_collection.find_one()
    assert isinstance(variant["revel_score"], float)

    # conservation fields
    for key, value in variant["conservation"].items():
        assert value == ["NotConserved"]

    # clinvar fields
    assert isinstance(variant["clnsig"][0]["accession"], int)
    assert variant["clnsig"][0]["value"] in REV_CLINSIG_MAP  # can be str or int
    assert isinstance(variant["clnsig"][0]["revstat"], str)  # str


def test_load_vep104_parsed_variant(
    one_vep104_annotated_variant, real_populated_database, case_obj
):
    """test first parsing and then loading a vep v97 annotated variant"""

    # GIVEN a MIP 11 / VEP 104 variant annotated using the following CSQ entry fields
    csq_header = "Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|UNIPROT_ISOFORM|REFSEQ_MATCH|SOURCE|REFSEQ_OFFSET|GIVEN_REF|USED_REF|BAM_EDIT|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|TRANSCRIPTION_FACTORS|SpliceAI_pred_DP_AG|SpliceAI_pred_DP_AL|SpliceAI_pred_DP_DG|SpliceAI_pred_DP_DL|SpliceAI_pred_DS_AG|SpliceAI_pred_DS_AL|SpliceAI_pred_DS_DG|SpliceAI_pred_DS_DL|SpliceAI_pred_SYMBOL|LoFtool|GERP++_NR|GERP++_RS|REVEL_rankscore|REVEL_score|phastCons100way_vertebrate|phyloP100way_vertebrate|rs_dbSNP150|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|ExACpLI|CLINVAR|CLINVAR_CLNSIG|CLINVAR_CLNVID|CLINVAR_CLNREVSTAT|genomic_superdups_frac_match"

    header = [word.upper() for word in csq_header.split("|")]

    # WHEN parsed using
    parsed_vep104_annotated_variant = parse_variant(
        variant=one_vep104_annotated_variant, vep_header=header, case=case_obj
    )

    # GIVEN a database without any variants
    adapter = real_populated_database
    assert adapter.variant_collection.find_one() is None

    # WHEN loading the variant into the database
    adapter.load_variant(variant_obj=parsed_vep104_annotated_variant)

    # THEN the variant is loaded with the fields correctly parsed
    # revel score
    variant = adapter.variant_collection.find_one()
    assert isinstance(variant["revel_score"], float)

    # ClinVar fields
    assert isinstance(variant["clnsig"][0]["accession"], int)
    assert variant["clnsig"][0]["value"] in REV_CLINSIG_MAP  # can be str or int
    assert isinstance(variant["clnsig"][0]["revstat"], str)  # str

    # dbSNP
    assert isinstance(variant["dbsnp_id"], str)
    assert "rs" in variant["dbsnp_id"]


def test_load_cancer_SV_variant(
    one_cancer_manta_SV_variant, real_populated_database, cancer_case_obj
):
    """Test loading a cancer SV variant into a mongo database"""

    # GIVEN a database containing one cancer case
    adapter = real_populated_database
    adapter.case_collection.insert_one(cancer_case_obj)
    assert sum(1 for i in adapter.case_collection.find({"track": "cancer"})) == 1

    # AND no variants
    assert adapter.variant_collection.find_one() is None

    # WHEN parsing a SV variant
    parsed_cancer_SV_variant = parse_variant(
        variant=one_cancer_manta_SV_variant, case=cancer_case_obj
    )

    # WHEN loading the variant into the database
    adapter.load_variant(variant_obj=parsed_cancer_SV_variant)

    # THEN the variant should have been parsed correctly
    variant = adapter.variant_collection.find_one()
    assert variant["variant_type"] == "clinical"
    assert variant["chromosome"]
    assert variant["position"]
    assert variant["end"]
    assert isinstance(variant["somatic_score"], int)


def test_load_variants(real_populated_database, case_obj, variant_clinical_file):
    """Test to load a variant into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    # WHEN loading a variant into the database
    rank_threshold = 0
    adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=rank_threshold,
    )
    # THEN assert the variant is loaded

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    pathogenic_categories = set(
        [
            "pathogenic",
            "likely_pathogenic",
            "conflicting_interpretations_of_pathogenecity",
            4,
            5,
        ]
    )
    for variant in adapter.variant_collection.find():
        pathogenic = False
        for annotation in variant.get("clnsig", []):
            if annotation["value"] in pathogenic_categories:
                pathogenic = True
        if variant["chromosome"] == "MT":
            continue
        if pathogenic:
            continue
        assert variant["rank_score"] >= rank_threshold
        assert variant["category"] == "snv"
        assert variant["variant_rank"]


def test_load_variants_includes_managed(real_populated_database, case_obj, variant_clinical_file):
    """Test that loading variants will include variants on the managed variants list"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    # GIVEN a managed variant info dict for a variant in the file,
    # but which has a rank score less than loading threshold (-2)
    managed_variant_info = {
        "chromosome": "1",
        "position": "36031420",
        "reference": "C",
        "alternative": "T",
        "build": "37",
    }

    # WHEN building a managed variant object
    managed_variant_obj = build_managed_variant(managed_variant_info)

    # WHEN loading a managed variant into the managed variant table
    adapter.load_managed_variant(managed_variant_obj)

    # WHEN loading variants into the database
    rank_threshold = 100
    adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=rank_threshold,
    )

    # THEN assert any variant is loaded
    assert sum(1 for i in adapter.variant_collection.find()) > 0

    ## THEN assert that the variant has been loaded
    query = adapter.build_query(
        case_id=case_obj["_id"],
        query={
            "variant_type": "clinical",
            "chrom": managed_variant_info["chromosome"],
            "start": managed_variant_info["position"],
            "end": managed_variant_info["position"],
        },
        category="snv",
    )
    print("Query: {}".format(query))
    assert sum(1 for i in adapter.variant_collection.find(query)) == 1


def test_load_sv_variants(real_populated_database, case_obj, sv_clinical_file):
    """Test to load a variant into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    # WHEN loading a variant into the database
    rank_threshold = 0
    adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="sv",
        rank_threshold=rank_threshold,
    )
    # THEN assert the variant is loaded

    assert sum(1 for i in adapter.variant_collection.find()) > 0

    for variant in adapter.variant_collection.find():
        assert variant["rank_score"] >= rank_threshold
        assert variant["category"] == "sv"
        assert variant["variant_rank"]


def test_load_region(real_populated_database, case_obj, variant_clinical_file):
    """Test to load variants from a region into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    # WHEN loading a variant into the database
    chrom = "1"
    start = 7847367
    end = 156126553
    adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        chrom=chrom,
        start=start,
        end=end,
    )
    # THEN assert all variants loaded are in the given region

    assert sum(1 for i in adapter.variant_collection.find()) > 0

    for variant in adapter.variant_collection.find():
        assert variant["chromosome"] == chrom
        assert variant["position"] <= end
        assert variant["end"] >= start


def test_load_mitochondrial(real_populated_database, case_obj, variant_clinical_file):
    """Test that all variants from mt are loaded"""
    adapter = real_populated_database
    rank_threshold = 3

    # Check how many MT variants there are in file
    vcf_obj = VCF(variant_clinical_file)
    mt_variants = 0
    for variant in vcf_obj:
        if variant.CHROM == "MT":
            mt_variants += 1

    # Make sure there are some MT variants
    assert mt_variants

    # GIVEN a database without any variants
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    # WHEN loading a variant into the database

    adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=rank_threshold,
    )
    # THEN assert all MT variants is loaded

    mt_variants_found = 0
    for variant in adapter.variant_collection.find():
        if variant["chromosome"] == "MT":
            mt_variants_found += 1

    assert mt_variants == mt_variants_found


def test_compounds_region(real_populated_database, case_obj):
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
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    ## WHEN loading a variant into the database
    adapter.load_variants(
        case_obj=case_obj,
        variant_type=variant_type,
        category=category,
        rank_threshold=-10,
    )

    adapter.load_indexes()
    institute_obj = adapter.institute_collection.find_one()
    case_obj = adapter.case_collection.find_one()

    chrom = "1"
    start = 156112157
    end = 156152543

    query = adapter.build_query(
        case_id=case_obj["_id"],
        query={
            "variant_type": variant_type,
            "chrom": chrom,
            "start": start,
            "end": end,
        },
        category=category,
    )
    ## THEN assert that there are variants with compounds without information
    variants_query = adapter.variant_collection.find(query)
    nr_comps = 0
    nr_variants = 0
    nr_not_loaded = 0
    genomic_regions = adapter.get_coding_intervals()
    for nr_variants, variant in enumerate(variants_query):
        for comp in variant.get("compounds", []):
            nr_comps += 1
            if comp["not_loaded"]:
                nr_not_loaded += 1

    assert nr_not_loaded > 0
    assert nr_variants > 0
    assert nr_comps > 0

    ## THEN when loading all variants in the region, assert that ALL the compounds are updated

    adapter.load_variants(
        case_obj=case_obj,
        variant_type=variant_type,
        category=category,
        chrom=chrom,
        start=start,
        end=end,
    )

    variants_query = adapter.variant_collection.find(query)
    nr_comps = 0
    nr_variants = 0
    for nr_variants, variant in enumerate(variants_query):
        for comp in variant.get("compounds", []):
            nr_comps += 1
            # We know that all ar updated and loaded if this flag is set
            assert comp["not_loaded"] is False

    assert nr_variants > 0
    assert nr_comps > 0


def test_updated_panel(real_variant_database, case_obj):
    """Test if the annotated panels are correct on variant level when a gene is removed
    from the panel. Ref #754

    In this test we need to update a gene panel by removing some genes and check that when loading
      variants they should not be annotated with the panel.

    """
    adapter = real_variant_database

    ## GIVEN an adapter with variants case and everything

    # Collect the hgnc_ids for all genes in the panel
    panel_hgnc_ids = set()
    # Get the panel object
    panel_name = case_obj["panels"][0]["panel_name"]
    panel_obj = adapter.gene_panel(panel_name)
    for gene_obj in panel_obj["genes"]:
        # Add the existing hgnc ids to the panel
        panel_hgnc_ids.add(gene_obj["hgnc_id"])

    # Loop over the variants and check that there are variants in
    # the genes from the panel
    variants = adapter.variants(case_id=case_obj["_id"])

    # Collect all present hgnc ids from the variants
    variant_hgnc_ids = set()
    for variant in variants:
        # print(variant['hgnc_ids'])
        if variant.get("hgnc_ids"):
            for hgnc_id in variant["hgnc_ids"]:
                if hgnc_id in panel_hgnc_ids:
                    # assert that the panel is annotated on the variant
                    assert panel_name in variant["panels"]
                variant_hgnc_ids.add(hgnc_id)

    # Assert that there are data
    assert panel_hgnc_ids
    assert variant_hgnc_ids

    intersecting_ids = panel_hgnc_ids.intersection(variant_hgnc_ids)
    assert intersecting_ids

    # Create a new case and a new gene panel

    # Create and insert a new gene panel without the intersecting genes
    old_panel_genes = panel_obj["genes"]
    panel_obj["genes"] = []
    for gene in old_panel_genes:
        if gene["hgnc_id"] not in intersecting_ids:
            panel_obj["genes"].append(gene)

    new_version = panel_obj["version"] + 1
    panel_obj["version"] = new_version
    panel_obj.pop("_id")

    adapter.panel_collection.insert_one(panel_obj)

    new_panel = adapter.panel_collection.find_one(
        {"panel_name": panel_obj["panel_name"], "version": new_version}
    )
    new_panel_ids = set()

    for gene in new_panel["genes"]:
        hgnc_id = gene["hgnc_id"]
        new_panel_ids.add(hgnc_id)
        assert hgnc_id not in intersecting_ids

    # Create a new case with the new panel
    case_obj["_id"] = "second_case"
    case_obj["panels"][0]["version"] = new_panel["version"]
    case_obj["panels"][0]["panel_id"] = new_panel["_id"]

    # Insert the new case and the variants
    adapter._add_case(case_obj)

    new_caseobj = adapter.case_collection.find_one({"_id": "second_case"})

    adapter.load_variants(
        new_caseobj,
        variant_type="clinical",
        category="snv",
        rank_threshold=-10,
        build="37",
    )

    # These are the new variants
    new_variants = adapter.variant_collection.find({"case_id": case_obj["_id"]})

    nr_variants = 0
    for variant in new_variants:
        if variant.get("hgnc_ids"):
            for hgnc_id in variant["hgnc_ids"]:
                if hgnc_id in intersecting_ids:
                    # assert that the panel is NOT annotated on the variant
                    # We removed the gener from the new panel
                    assert panel_name not in variant.get("panels", [])
                    nr_variants += 1
    assert nr_variants > 0
