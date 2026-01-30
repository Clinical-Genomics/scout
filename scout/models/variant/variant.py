# -*- coding: utf-8 -*-
from typing import Optional

variant = dict(
    # document_id is a md5 string created by institute_genelist_caseid_variantid:
    _id=str,  # required, same as document_id
    acmg_classification=str,  # choices=ACMG_TERMS
    alternative=str,  # required
    case_id=str,  # case_id is a string like owner_caseid
    cadd_score=float,  # predicted deleteriousness
    category=str,  # choices=('sv', 'snv', 'str')
    ccv_classification=str,  # choices=CCV_TERMS
    chromosome=str,  # required
    clnsig=list,  # list of <clinsig>
    compounds=list,  # sorted list of <compound> ordering='combined_score'
    custom_images=list,  # list of custom image dictionaries
    dbsnp_id=str,
    display_name=str,  # required. no md5. chrom_pos_ref_alt_variant_type
    dismiss_variant=list,
    end=int,  # required
    exac_frequency=float,
    filters=list,  # list of strings
    freebayes=str,  # choices=VARIANT_CALL, default='Not Used'
    gatk=str,  # choices=VARIANT_CALL, default='Not Used'
    genetic_models=list,  # list of strings choices=GENETIC_MODELS
    genes=list,  # list with <gene>
    hgnc_ids=list,  # list of hgnc ids (int)
    hgnc_symbols=list,  # list of hgnc symbols (str)
    institute=str,  # institute_id, required
    length=int,  # required
    local_frequency=float,
    local_obs_cancer_germline_hom_old=int,
    local_obs_cancer_germline_old=int,
    local_obs_cancer_germline_old_freq=float,
    local_obs_cancer_somatic_hom_old=int,
    local_obs_cancer_somatic_old=int,
    local_obs_cancer_somatic_old_freq=float,
    local_obs_hom_old=int,
    local_obs_old=int,
    local_obs_old_date=str,
    local_obs_old_desc=str,
    local_obs_old_freq=float,
    local_obs_old_nr_cases=int,
    manual_rank=int,  # choices=[0, 1, 2, 3, 4, 5]
    mate_id=str,  # For SVs this identifies the other end
    max_exac_frequency=float,
    max_thousand_genomes_frequency=float,
    mei_name=str,  # MEI variant
    mei_polarity=str,  # MEI variant
    mitomap_associated_diseases=str,  # mitochondrial variants
    missing_data=bool,  # default False
    phast_conservation=list,  # list of str, choices=CONSERVATION
    phylop_conservation=list,  # list of str, choices=CONSERVATION
    position=int,  # required
    rank_score=float,  # required
    rank_score_results=list,  # List if dictionaries
    rank_score_other=Optional[dict],
    reference=str,  # required
    samtools=str,  # choices=VARIANT_CALL, default='Not Used'
    samples=list,  # list of dictionaries that are <gt_calls>
    simple_id=str,  # required. A string created by chrom_pos_ref_alt
    spidex=float,
    str_disease=str,
    str_display_ru=str,
    str_inheritance_mode=str,  # STR disease mode of inheritance "AD", "XR", "AR", "-"
    str_normal_max=int,
    str_pathologic_min=int,
    str_repid=str,
    str_ref=str,
    str_ru=str,
    str_source=dict,  # STR source dict with keys {"display": str, "type": str ("PubMed", "GeneReviews"), "id": str}
    str_swegen_mean=float,
    str_swegen_std=float,
    sub_category=str,  # choices=('snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv', 'bnd', 'str', 'mei')
    thousand_genomes_frequency=float,
    thousand_genomes_frequency_left=float,
    thousand_genomes_frequency_right=float,
    variant_id=str,  # required. A md5 string created by [ chrom, pos, ref, alt, variant_type]
    variant_rank=int,  # required
    variant_type=str,  # required, choices=('research', 'clinical')
    validation=str,  # Sanger validation, choices=('True positive', 'False positive')
)

compound = dict(
    # This must be the document_id for this variant
    variant=str,  # required=True
    # This is the variant id
    display_name=str,  # required
    combined_score=float,  # required
)

clinsig = dict(value=int, accession=str, revstat=str)

gt_call = dict(
    sample_id=str,
    display_name=str,
    genotype_call=str,
    allele_depths=list,  # int
    read_depth=int,
    alt_mc=int,
    genotype_quality=int,
    so=str,
    sdr=float,  # STRdrop case average adjusted sequencing depth ratio
    sdp=float,  # Strdrop coverage sequencing depth level probability
)

MIMVIR_SCORE = {
    "score_key": "MivmirScore",
    "score_type": float,
    "score_desc": "MivmirExplanation",  # dict
}
GICAM_SCORE = {"score_key": "GicamScore", "score_type": float}

RANK_SCORE_OTHER = {"snv": {"Mivmir": MIMVIR_SCORE, "Gicam": GICAM_SCORE}}
