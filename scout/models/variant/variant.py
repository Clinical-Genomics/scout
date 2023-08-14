# -*- coding: utf-8 -*-

variant = dict(
    # document_id is a md5 string created by institute_genelist_caseid_variantid:
    _id=str,  # required, same as document_id
    document_id=str,  # required. Same as _id
    variant_id=str,  # required. A md5 string created by [ chrom, pos, ref, alt, variant_type]
    display_name=str,  # required. no md5. chrom_pos_ref_alt_variant_type
    simple_id=str,  # required. A string created by chrom_pos_ref_alt
    # The variant can be either research or clinical.
    # For research variants we display all the available information while
    # the clinical variants have limited annotation fields.
    variant_type=str,  # required, choices=('research', 'clinical'))
    category=str,  # choices=('sv', 'snv', 'str')
    sub_category=str,  # choices=('snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv', 'bnd', 'str', 'mei')
    mate_id=str,  # For SVs this identifies the other end
    case_id=str,  # case_id is a string like owner_caseid
    chromosome=str,  # required
    position=int,  # required
    end=int,  # required
    length=int,  # required
    reference=str,  # required
    alternative=str,  # required
    rank_score=float,  # required
    variant_rank=int,  # required
    rank_score_results=list,  # List if dictionaries
    institute=str,  # institute_id, required
    sanger_ordered=bool,
    validation=str,  # Sanger validation, choices=('True positive', 'False positive')
    quality=float,
    filters=list,  # list of strings
    samples=list,  # list of dictionaries that are <gt_calls>
    genetic_models=list,  # list of strings choices=GENETIC_MODELS
    compounds=list,  # sorted list of <compound> ordering='combined_score'
    genes=list,  # list with <gene>
    dbsnp_id=str,
    # str variant
    str_ru=str,
    str_display_ru=str,
    str_repid=str,
    str_ref=str,
    str_disease=str,
    str_inheritance_mode=str,  # STR disease mode of inheritance "AD", "XR", "AR", "-"
    str_source=dict,  # STR source dict with keys {"display": str, "type": str ("PubMed", "GeneReviews"), "id": str}
    str_normal_max=int,
    str_pathologic_min=int,
    str_swegen_mean=float,
    str_swegen_std=float,
    custom_images=list,  # list of custom image dictionaries
    # MEI variant
    mei_name=str,
    mei_polarity=str,
    # mitochondrial variants
    mitomap_associated_diseases=str,
    # Gene ids:
    hgnc_ids=list,  # list of hgnc ids (int)
    hgnc_symbols=list,  # list of hgnc symbols (str)
    panels=list,  # list of panel names that the variant overlaps
    # Frequencies:
    thousand_genomes_frequency=float,
    thousand_genomes_frequency_left=float,
    thousand_genomes_frequency_right=float,
    exac_frequency=float,
    max_thousand_genomes_frequency=float,
    max_exac_frequency=float,
    local_frequency=float,
    local_obs_old=int,
    local_obs_hom_old=int,
    local_obs_old_freq=float,
    local_obs_old_desc=str,
    local_obs_old_nr_cases=int,
    local_obs_old_date=str,
    local_obs_cancer_germline_old=int,
    local_obs_cancer_germline_hom_old=int,
    local_obs_cancer_germline_old_freq=float,
    local_obs_cancer_somatic_old=int,
    local_obs_cancer_somatic_hom_old=int,
    local_obs_cancer_somatic_old_freq=float,
    # Predicted deleteriousness:
    cadd_score=float,
    clnsig=list,  # list of <clinsig>
    spidex=float,
    missing_data=bool,  # default False
    # Callers
    gatk=str,  # choices=VARIANT_CALL, default='Not Used'
    samtools=str,  # choices=VARIANT_CALL, default='Not Used'
    freebayes=str,  # choices=VARIANT_CALL, default='Not Used'
    # Conservation:
    phast_conservation=list,  # list of str, choices=CONSERVATION
    gerp_conservation=list,  # list of str, choices=CONSERVATION
    phylop_conservation=list,  # list of str, choices=CONSERVATION
    # Database options:
    gene_lists=list,
    manual_rank=int,  # choices=[0, 1, 2, 3, 4, 5]
    dismiss_variant=list,
    acmg_classification=str,  # choices=ACMG_TERMS
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
    genotype_quality=int,
    so=str,
)
