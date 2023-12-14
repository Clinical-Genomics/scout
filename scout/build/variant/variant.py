# -*- coding: utf-8 -*-
import logging

from scout.utils.convert import call_safe
from scout.utils.dict_utils import remove_nonetype

from . import build_clnsig, build_compound, build_gene, build_genotype

LOG = logging.getLogger(__name__)


def build_variant(
    variant, institute_id, gene_to_panels=None, hgncid_to_gene=None, sample_info=None
):
    """Build a variant object based on parsed information

    Args:
        variant(dict)
        institute_id(str)
        gene_to_panels(dict): A dictionary with
            {<hgnc_id>: {
                'panel_names': [<panel_name>, ..],
                'disease_associated_transcripts': [<transcript_id>, ..]
                }
                .
                .
            }

        hgncid_to_gene(dict): A dictionary with
            {<hgnc_id>: <hgnc_gene info>
                .
                .
            }
        sample_info(dict): A dictionary with info about samples.
                           Strictly for cancer to tell which is tumor


    Returns:
        variant_obj(dict)

    variant = dict(
        # document_id is a md5 string created by institute_genelist_caseid_variantid:
        _id = str, # required, same as document_id
        document_id = str, # required
        # variant_id is a md5 string created by chrom_pos_ref_alt (simple_id)
        variant_id = str, # required
        # display name is variant_id (no md5)
        display_name = str, # required

        # chrom_pos_ref_alt
        simple_id = str,
        # The variant can be either research or clinical.
        # For research variants we display all the available information while
        # the clinical variants have limited annotation fields.
        variant_type = str, # required, choices=('research', 'clinical'))

        category = str, # choices=('sv', 'snv', 'str', 'fusion')
        sub_category = str, # choices=('snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv', 'bnd')
        mate_id = str, # For SVs this identifies the other end

        case_id = str, # case_id is a string like owner_caseid
        chromosome = str, # required
        position = int, # required
        end = int, # required
        length = int, # required
        reference = str, # required
        alternative = str, # required

        rank_score = float, # required
        variant_rank = int, # required
        rank_score_results = list, # List if dictionaries
        variant_rank = int, # required

        institute = str, # institute_id, required

        sanger_ordered = bool,
        validation = str, # Sanger validation, choices=('True positive', 'False positive')

        quality = float,
        filters = list, # list of strings
        samples = list, # list of dictionaries that are <gt_calls>
        genetic_models = list, # list of strings choices=GENETIC_MODELS
        compounds = list, # sorted list of <compound> ordering='combined_score'

        genes = list, # list with <gene>
        dbsnp_id = str,

        # Gene ids:
        hgnc_ids = list, # list of hgnc ids (int)
        hgnc_symbols = list, # list of hgnc symbols (str)
        panels = list, # list of panel names that the variant ovelapps

        # Frequencies:
        thousand_genomes_frequency = float,
        thousand_genomes_frequency_left = float,
        thousand_genomes_frequency_right = float,
        exac_frequency = float,
        max_thousand_genomes_frequency = float,
        max_exac_frequency = float,
        local_frequency = float,
        local_obs_old = int,
        local_obs_hom_old = int,
        local_obs_old_freq = float,
        # cancer caller (balsamic) loqusdb frequencies
        local_obs_cancer_germline_old=int, # germline counts
        local_obs_cancer_germline_hom_old=int, # germline counts for homoz
        local_obs_cancer_germline_old_freq=float, # germline frequency

        local_obs_cancer_somatic_old=int,# somatic counts
        local_obs_cancer_somatic_hom_old=int, # somatic counts for homoz
        local_obs_cancer_somatic_old_freq=float, # somatic frequency

        # Predicted deleteriousness:
        cadd_score = float,
        revel_score = float, REVEL rankscore
        revel = float, REVEL score
        clnsig = list, # list of <clinsig>
        spidex = float,

        missing_data = bool, # default False

        # STR specific information
        str_repid = str, repeat id generally corresponds to gene symbol
        str_ru = str, Repeat Unit used e g in PanelApp naming of STRs
        str_ref = int, reference copy number
        str_len = int, number of repeats found in case
        str_status = str, this indicates the severity of the expansion level
        str_normal_max = int, max number of repeats to call an STR variant normal
        str_pathologic_min = int, min number of repeats to call an STR variant pathologic
        str_disease = str, Associated disease name
        str_inheritance_mode = str, STR disease mode of inheritance "AD", "XR", "AR", "-"
        str_source = dict, STR source dict with keys {"display": str, "type": str ("PubMed", "GeneReviews"), "id": str}
        str_swegen_mean = float, STR norm pop mean
        str_swegen_std = float, STR norm pop stdev

        # MEI specific information
        mei_name = str, Mobile element name from retroseq MEINFO tag
        mei_polarity = str, Mobile element polarity from retroseq MEINFO tag

        # Callers
        gatk = str, # choices=VARIANT_CALL, default='Not Used'
        samtools = str, # choices=VARIANT_CALL, default='Not Used'
        freebayes = str, # choices=VARIANT_CALL, default='Not Used'

        # Conservation:
        phast_conservation = list, # list of str, choices=CONSERVATION
        gerp_conservation = list, # list of str, choices=CONSERVATION
        phylop_conservation = list, # list of str, choices=CONSERVATION

        # Database options:
        gene_lists = list,
        manual_rank = int, # choices=[0, 1, 2, 3, 4, 5]
        cancer_tier = str # choices=['1A', '1B', '2A', '2B', '3', '4']
        dismiss_variant = list,

        acmg_evaluation = str, # choices=ACMG_TERMS
    )
    """
    gene_to_panels = gene_to_panels or {}
    hgncid_to_gene = hgncid_to_gene or {}
    sample_info = sample_info or {}

    # LOG.debug("Building variant %s", variant['ids']['document_id'])
    variant_obj = dict(
        _id=variant["ids"]["document_id"],
        document_id=variant["ids"]["document_id"],
        variant_id=variant["ids"]["variant_id"],
        display_name=variant["ids"]["display_name"],
        variant_type=variant["variant_type"],
        case_id=variant["case_id"],
        chromosome=variant["chromosome"],
        reference=variant["reference"],
        alternative=variant["alternative"],
        institute=institute_id,
    )

    variant_obj["category"] = variant.get("category")
    variant_obj["cosmic_ids"] = variant.get("cosmic_ids")
    variant_obj["cytoband_end"] = variant.get("cytoband_end")
    variant_obj["cytoband_start"] = variant.get("cytoband_start")
    variant_obj["dbsnp_id"] = variant.get("dbsnp_id")
    variant_obj["end"] = call_safe(int, variant.get("end"))
    variant_obj["end_chrom"] = variant.get("end_chrom")
    variant_obj["filters"] = variant.get("filters")
    variant_obj["length"] = call_safe(int, variant.get("length"))
    variant_obj["mate_id"] = variant.get("mate_id")
    variant_obj["missing_data"] = False
    variant_obj["position"] = int(variant["position"])
    variant_obj["quality"] = float(variant["quality"]) if variant["quality"] else None
    variant_obj["rank_score"] = float(variant["rank_score"])
    variant_obj["simple_id"] = variant["ids"].get("simple_id")
    variant_obj["sub_category"] = variant.get("sub_category")

    ### STR variant specific
    variant_obj["str_disease"] = variant.get("str_disease")
    variant_obj["str_inheritance_mode"] = variant.get("str_inheritance_mode")
    variant_obj["str_len"] = variant.get("str_len")
    variant_obj["str_normal_max"] = variant.get("str_normal_max")
    variant_obj["str_pathologic_min"] = variant.get("str_pathologic_min")
    variant_obj["str_ref"] = variant.get("str_ref")
    variant_obj["str_repid"] = variant.get("str_repid")
    variant_obj["str_ru"] = variant.get("str_ru")
    variant_obj["str_source"] = variant.get("str_source")
    variant_obj["str_status"] = variant.get("str_status")
    variant_obj["str_swegen_mean"] = call_safe(float, variant.get("str_swegen_mean"))
    variant_obj["str_swegen_std"] = call_safe(float, variant.get("str_swegen_std"))

    ## MEI variant specific
    variant_obj["mei_name"] = variant.get("mei_name")
    variant_obj["mei_polarity"] = variant.get("mei_polarity")

    ## Fusion variant specific
    if variant_obj["category"] == "fusion":
        variant_obj["rank_score"] = variant_obj.get("fusion_score")

        FUSION_KEYS = [
            "tool_hits",
            "fusion_score",
            "orientation",
            "frame_status",
            "fusion_genes",
            "found_db",
        ]
        for key in FUSION_KEYS:
            variant_obj[key] = variant.get(key)

    ### Mitochondria Specific
    variant_obj["mitomap_associated_diseases"] = variant.get("mitomap_associated_diseases")
    variant_obj["hmtvar_variant_id"] = variant.get("hmtvar_variant_id")

    variant_obj["genetic_models"] = variant.get("genetic_models")

    set_sample(variant_obj, variant.get("samples", []), sample_info)
    add_compounds(variant_obj, variant.get("compounds", []))

    add_genes(variant_obj, variant.get("genes", []), hgncid_to_gene)

    # Make gene searches more effective
    if "hgnc_ids" in variant:
        variant_obj["hgnc_ids"] = [hgnc_id for hgnc_id in variant["hgnc_ids"] if hgnc_id]

    add_hgnc_symbols(variant_obj, variant_obj["hgnc_ids"], hgncid_to_gene)
    link_gene_panels(variant_obj, gene_to_panels)
    add_clnsig_objects(variant_obj, variant.get("clnsig", []))

    add_callers(variant_obj, variant.get("callers", {}))

    ### Add the conservation
    conservation_info = variant.get("conservation", {})
    variant_obj["phast_conservation"] = conservation_info.get("phast")
    variant_obj["gerp_conservation"] = conservation_info.get("gerp")
    variant_obj["phylop_conservation"] = conservation_info.get("phylop")

    ### Add autozygosity calls
    variant_obj["azlength"] = variant.get("azlength")
    variant_obj["azqual"] = variant.get("azqual")
    variant_obj["custom"] = variant.get("custom")
    variant_obj["somatic_score"] = variant.get("somatic_score")

    # Add the frequencies
    add_frequencies(variant_obj, variant.get("frequencies", {}))

    # Add the local observation counts from the old archive
    # SNVs and SVs
    variant_obj["local_obs_old"] = variant.get("local_obs_old")

    # SNVs
    variant_obj["local_obs_hom_old"] = variant.get("local_obs_hom_old")

    # SVs
    variant_obj["local_obs_old_freq"] = variant.get("local_obs_old_freq")
    variant_obj["local_obs_old_date"] = variant.get("local_obs_old_date")
    variant_obj["local_obs_old_desc"] = variant.get("local_obs_old_desc")
    variant_obj["local_obs_old_nr_cases"] = variant.get("local_obs_old_nr_cases")

    # local observations from cancer pipeline
    variant_obj["local_obs_cancer_germline_old"] = variant.get("local_obs_cancer_germline_old")
    variant_obj["local_obs_cancer_somatic_old"] = variant.get("local_obs_cancer_somatic_old")
    variant_obj["local_obs_cancer_germline_hom_old"] = variant.get(
        "local_obs_cancer_germline_hom_old"
    )
    variant_obj["local_obs_cancer_somatic_hom_old"] = variant.get(
        "local_obs_cancer_somatic_hom_old"
    )
    variant_obj["local_obs_cancer_germline_old_freq"] = variant.get(
        "local_obs_cancer_germline_old_freq"
    )
    variant_obj["local_obs_cancer_somatic_old_freq"] = variant.get(
        "local_obs_cancer_somatic_old_freq"
    )

    ##### Add the severity predictors #####
    variant_obj["cadd_score"] = variant.get("cadd_score")
    variant_obj["revel_score"] = variant.get("revel_score")
    variant_obj["revel"] = variant.get("revel")
    variant_obj["spidex"] = variant.get("spidex")

    add_rank_score(variant_obj, variant)

    # Cancer specific
    variant_obj["mvl_tag"] = True if variant.get("mvl_tag") else None

    return remove_nonetype(variant_obj)


def link_gene_panels(variant_obj, gene_to_panels):
    """Add link gene panels to variant_obj
    Args: variant_obj (Dict)
          gene_to_panels (List)
    Returns: None
    """
    panel_names = set()
    for hgnc_id in variant_obj["hgnc_ids"]:
        gene_panels = gene_to_panels.get(hgnc_id, set())
        panel_names = panel_names.union(gene_panels)

    if panel_names:
        variant_obj["panels"] = list(panel_names)


def add_clnsig_objects(variant_obj, clnsig_list):
    """Add clnsig objects to variant_obj
    Args: variant_obj (Dict)
          clnsig_list (List)
    Returns: None"""
    clnsig_objects = []
    for entry in clnsig_list:
        clnsig_obj = build_clnsig(entry)
        clnsig_objects.append(clnsig_obj)

    if clnsig_objects:
        variant_obj["clnsig"] = clnsig_objects


def add_callers(variant_obj, call_info):
    """Add call_info to variant_obj
    Args: variant_obj (Dict)
          call_info (List)
    Returns: None"""
    for caller in call_info:
        if call_info[caller]:
            variant_obj[caller] = call_info[caller]


def set_sample(variant_obj, sample_list, sample_info):
    """Add call_info to variant_obj
    Args: variant_obj (Dict)
          sample_list (List)
          sample_info (Dict)
    Returns: None"""
    gt_types = []
    for sample in sample_list:
        gt_call = build_genotype(sample)
        gt_types.append(gt_call)

        if sample_info:
            sample_id = sample["individual_id"]
            key = "tumor" if sample_info[sample_id] == "case" else "normal"
            variant_obj[key] = {
                "alt_depth": sample["alt_depth"],
                "ref_depth": sample["ref_depth"],
                "read_depth": sample["read_depth"],
                "alt_freq": sample["alt_frequency"],
                "ind_id": sample_id,
            }
    variant_obj["samples"] = gt_types


def add_compounds(variant_obj, compound_list):
    """Add compound list to variant_obj
    Args: variant_obj (Dict)
          compound_list (List)
    Returns: None"""
    compounds = []
    for compound in compound_list:
        compound_obj = build_compound(compound)
        compounds.append(compound_obj)

    if compounds:
        variant_obj["compounds"] = compounds


def add_genes(variant_obj, gene_list, hgncid_to_gene):
    """Add compound list to variant_obj
    Args: variant_obj (Dict)
          gene_list (list)
          hgncid_to_gene (Dict)
    Returns: None"""
    genes = []
    for index, gene in enumerate(gene_list):
        if gene.get("hgnc_id"):
            gene_obj = build_gene(gene, hgncid_to_gene)
            genes.append(gene_obj)
            if index > 30:
                # avoid uploading too much data (specifically for SV variants)
                # mark variant as missing data
                variant_obj["missing_data"] = True
                break
    if genes:
        variant_obj["genes"] = genes


def add_hgnc_symbols(variant_obj, hgnc_id_list, hgncid_to_gene):
    """Add the hgnc symbols from the database genes
    Args: variant_obj (Dict)
          hgnc_id_list (List)
          hgncid_to_gene (Dict)
    Returns: None"""
    hgnc_symbols = []
    for hgnc_id in hgnc_id_list:
        gene_obj = hgncid_to_gene.get(hgnc_id)
        if gene_obj:
            hgnc_symbols.append(gene_obj["hgnc_symbol"])
        else:
            LOG.warning("missing HGNC symbol for: %s", hgnc_id)
    variant_obj["hgnc_symbols"] = hgnc_symbols


def add_rank_score(variant_obj, variant):
    """Add the rank score results
    Args: variant_obj (Dict)
          variant (Dict)
    Returns: None"""
    rank_results = []
    for category in variant.get("rank_result", []):
        rank_result = {"category": category, "score": variant["rank_result"][category]}
        rank_results.append(rank_result)

    if rank_results:
        variant_obj["rank_score_results"] = rank_results


def add_frequencies(variant_obj, frequencies):
    """Add the rank score results
    Args: variant_obj (Dict)
          frequencies (Dict)
    Returns: None"""
    variant_obj["exac_frequency"] = call_safe(float, frequencies.get("exac"))
    variant_obj["gnomad_frequency"] = call_safe(float, frequencies.get("gnomad"))
    variant_obj["gnomad_mt_heteroplasmic_frequency"] = call_safe(
        float, frequencies.get("gnomad_mt_heteroplasmic")
    )
    variant_obj["gnomad_mt_homoplasmic_frequency"] = call_safe(
        float, frequencies.get("gnomad_mt_homoplasmic")
    )
    variant_obj["max_exac_frequency"] = call_safe(float, frequencies.get("exac_max"))
    variant_obj["max_gnomad_frequency"] = call_safe(float, frequencies.get("gnomad_max"))
    variant_obj["max_thousand_genomes_frequency"] = call_safe(
        float, frequencies.get("thousand_g_max")
    )
    variant_obj["thousand_genomes_frequency"] = call_safe(float, frequencies.get("thousand_g"))
    variant_obj["thousand_genomes_frequency_left"] = call_safe(
        float, frequencies.get("thousand_g_left")
    )
    variant_obj["thousand_genomes_frequency_right"] = call_safe(
        float, frequencies.get("thousand_g_right")
    )

    # Add the sv counts:
    variant_obj["clingen_cgh_benign"] = frequencies.get("clingen_benign")
    variant_obj["clingen_cgh_pathogenic"] = frequencies.get("clingen_pathogenic")
    variant_obj["clingen_mip"] = frequencies.get("clingen_mip")
    variant_obj["clingen_ngi"] = frequencies.get("clingen_ngi")
    variant_obj["swegen"] = frequencies.get("swegen")

    # add the mei frqs:
    for mei_freq in ["swegen_alu", "swegen_herv", "swegen_l1", "swegen_sva", "swegen_mei_max"]:
        variant_obj[mei_freq] = frequencies.get(mei_freq)

    # Decipher is never a frequency, it will ony give 1 if variant exists in decipher
    # Check if decipher exists
    variant_obj["decipher"] = frequencies.get("decipher")
