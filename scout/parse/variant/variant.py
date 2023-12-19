import logging
from typing import Any, Dict, List, Optional

from cyvcf2 import Variant

from scout.constants import CHR_PATTERN
from scout.exceptions import VcfError
from scout.utils.convert import call_safe
from scout.utils.dict_utils import remove_nonetype

from .callers import parse_callers
from .clnsig import parse_clnsig
from .compound import parse_compounds
from .conservation import parse_conservations
from .coordinates import parse_coordinates
from .deleteriousness import parse_cadd
from .frequency import parse_frequencies, parse_mei_frequencies, parse_sv_frequencies
from .gene import parse_genes
from .genotype import parse_genotypes
from .ids import parse_ids
from .models import parse_genetic_models
from .rank_score import parse_rank_score
from .transcript import parse_transcripts

LOG = logging.getLogger(__name__)


def parse_variant(
    variant: Variant,
    case,
    variant_type="clinical",
    rank_results_header=None,
    vep_header=None,
    individual_positions=None,
    category=None,
    local_archive_info=None,
):
    """Return a parsed variant

        Get all the necessary information to build a variant object

    Args:
        variant(cyvcf2.Variant)
        case(dict)
        variant_type(str): 'clinical' or 'research'
        rank_results_header(list)
        vep_header(list)
        individual_positions(dict): Explain what position each individual has
                                    in vcf
        category(str): 'snv', 'sv', 'str', 'cancer', 'cancer_sv' or 'fusion'
        local_archive_info(dict): date and total count for local obs
    Returns:
         parsed_variant(dict): Parsed variant
    """
    # These are to display how the rank score is built
    rank_results_header = rank_results_header or []
    # Vep information
    vep_header = vep_header or []

    parsed_variant = {}
    # Create the ID for the variant
    case_id = case["_id"]
    genmod_key = get_genmod_key(case)
    chrom_match = CHR_PATTERN.match(variant.CHROM)
    chrom = chrom_match.group(2)

    # Builds a dictionary with the different ids that are used
    alt = get_variant_alternative(variant, category)

    parsed_variant["ids"] = parse_ids(
        chrom=chrom,
        pos=variant.POS,
        ref=variant.REF,
        alt=alt,
        case_id=case_id,
        variant_type=variant_type,
    )
    parsed_variant["case_id"] = case_id
    # type can be 'clinical' or 'research'
    parsed_variant["variant_type"] = variant_type

    category = get_category(category, variant, parsed_variant)
    parsed_variant["category"] = category

    ################# General information #################
    parsed_variant["reference"] = variant.REF

    ### We allways assume splitted and normalized vcfs!!!
    if len(variant.ALT) > 1:
        raise VcfError("Variants are only allowed to have one alternative")
    parsed_variant["alternative"] = alt

    # cyvcf2 will set QUAL to None if '.' in vcf
    parsed_variant["quality"] = variant.QUAL
    parsed_variant["filters"] = get_filters(variant)

    # Add the dbsnp ids
    set_dbsnp_id(parsed_variant, variant.ID)

    # This is the id of other position in translocations
    # (only for specific svs)
    parsed_variant["mate_id"] = None

    ################# Position specific #################
    parsed_variant["chromosome"] = chrom

    coordinates = parse_coordinates(variant, category, case.get("genome_build"))

    parsed_variant["cytoband_end"] = coordinates["cytoband_end"]
    parsed_variant["cytoband_start"] = coordinates["cytoband_start"]
    parsed_variant["end"] = coordinates["end"]
    parsed_variant["end_chrom"] = coordinates["end_chrom"]
    parsed_variant["length"] = coordinates["length"]
    parsed_variant["mate_id"] = coordinates["mate_id"]
    parsed_variant["position"] = coordinates["position"]
    parsed_variant["sub_category"] = coordinates["sub_category"]

    ################# Add rank score #################
    # The rank score is central for displaying variants in scout.
    # Use RankScore for somatic variations also

    rank_score = parse_rank_score(variant.INFO.get("RankScore", ""), genmod_key)
    parsed_variant["rank_score"] = rank_score or 0

    ################# Add gt calls #################
    parsed_variant["samples"] = get_samples(variant, individual_positions, case)

    ################# Add compound information #################
    compounds = parse_compounds(
        compound_info=variant.INFO.get("Compounds"),
        case_id=genmod_key,
        variant_type=variant_type,
    )

    parsed_variant["compounds"] = compounds

    ################# Add inheritance patterns #################
    parsed_variant["genetic_models"] = parse_genetic_models(
        variant.INFO.get("GeneticModels"), genmod_key
    )

    ################# Add autozygosity calls if present #################
    parsed_variant["azlength"] = call_safe(int, variant.INFO.get("AZLENGTH"))
    parsed_variant["azqual"] = call_safe(float, variant.INFO.get("AZQUAL"))

    # STR variant info
    set_str_info(variant, parsed_variant)
    # STR source dict with display string, source type and entry id
    set_str_source(parsed_variant, variant)
    parsed_variant["str_swegen_mean"] = call_safe(float, variant.INFO.get("SweGenMean"))
    parsed_variant["str_swegen_std"] = call_safe(float, variant.INFO.get("SweGenStd"))

    # MEI variant info
    set_mei_info(variant, parsed_variant)

    # Add Fusion info
    set_fusion_info(variant, parsed_variant)

    ################# Add somatic info ##################
    parsed_variant["somatic_score"] = call_safe(int, variant.INFO.get("SOMATICSCORE"))

    ################# Add mitomap info, from HmtNote #################
    set_mitomap_associated_diseases(parsed_variant, variant)

    ################# Add HmtVar variant id, from HmtNote #################
    add_hmtvar(parsed_variant, variant)

    ### Add custom info
    parsed_variant["custom"] = parse_custom_data(variant.INFO.get("SCOUT_CUSTOM"))

    ### Add gene and transcript information
    if parsed_variant.get("category") == "fusion":
        parsed_transcripts = add_gene_and_transcript_info_for_fusions(parsed_variant)
    else:
        parsed_transcripts = add_gene_and_transcript_info(parsed_variant, variant, vep_header)

    ################# Add clinsig prediction #################
    set_clnsig(parsed_variant, variant, parsed_transcripts)

    ################# Add the frequencies #################
    frequencies = parse_frequencies(variant, parsed_transcripts)

    parsed_variant["frequencies"] = frequencies

    # loqus archive frequencies

    # RD germline, for MIP and Balsamic
    # SNVs contain INFO field Obs, SVs contain clinical_genomics_loqusObs
    local_obs_old = (
        variant.INFO.get("Obs")
        or variant.INFO.get("clinical_genomics_loqusObs")
        or variant.INFO.get("clin_obs")
    )
    if local_obs_old:
        parsed_variant["local_obs_old"] = int(local_obs_old)

    # SNVs only
    parsed_variant["local_obs_hom_old"] = call_safe(int, variant.INFO.get("Hom"))

    # SVs only
    local_frq_old = variant.INFO.get("clinical_genomics_loqusFrq") or variant.INFO.get("Frq")
    parsed_variant["local_obs_old_freq"] = call_safe(float, local_frq_old)
    set_local_archive_info(parsed_variant, local_archive_info)

    # Cancer (Balsamic) Germline and Somatic loqus archives
    parsed_variant["local_obs_cancer_germline_old"] = call_safe(
        int, variant.INFO.get("Cancer_Germline_Obs")
    )
    parsed_variant["local_obs_cancer_germline_hom_old"] = call_safe(
        int, variant.INFO.get("Cancer_Germline_Hom")
    )
    parsed_variant["local_obs_cancer_germline_old_freq"] = call_safe(
        float, variant.INFO.get("Cancer_Germline_Frq")
    )

    parsed_variant["local_obs_cancer_somatic_old"] = call_safe(
        int, variant.INFO.get("Cancer_Somatic_Obs")
    )
    parsed_variant["local_obs_cancer_somatic_hom_old"] = call_safe(
        int, variant.INFO.get("Cancer_Somatic_Hom")
    )
    parsed_variant["local_obs_cancer_somatic_old_freq"] = call_safe(
        float, variant.INFO.get("Cancer_Somatic_Frq")
    )

    ###################### Add severity predictions ######################
    parsed_variant["cadd_score"] = parse_cadd(variant, parsed_transcripts)
    parsed_variant["spidex"] = call_safe(float, variant.INFO.get("SPIDEX"))

    if len(parsed_transcripts) > 0:
        parsed_variant["revel_score"] = parsed_transcripts[0].get(
            "revel_rankscore"
        )  # This is actually the value of REVEL_rankscore

        parsed_variant["revel"] = parsed_transcripts[0].get(
            "revel_raw_score"
        )  # This is actually the value of REVEL_score

    ###################### Add conservation ######################
    parsed_variant["conservation"] = parse_conservations(variant, parsed_transcripts)
    parsed_variant["callers"] = parse_callers(variant, category=category)
    set_rank_result(parsed_variant, variant, rank_results_header)

    ###################### Add SV specific annotations ######################
    sv_frequencies = parse_sv_frequencies(variant)
    for key in sv_frequencies:
        parsed_variant["frequencies"][key] = sv_frequencies[key]

    ###################### Add MEI specific annotations #####################
    mei_frequencies = parse_mei_frequencies(variant)
    for key in mei_frequencies:
        parsed_variant["frequencies"][key] = mei_frequencies[key]

    ###################### Add Cancer specific annotations ######################
    # MSK_MVL indicates if variants are in the MSK managed variant list
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5437632/
    if variant.INFO.get("MSK_MVL"):
        parsed_variant["mvl_tag"] = True

    remove_nonetype(parsed_variant)
    return parsed_variant


def get_genmod_key(case):
    """Gen genmod key

    Args:
        case(dict)
    Return:
        case._id(str) or case.display_name(str)
    """
    case_id = case["_id"]
    if "-" in case_id:
        LOG.debug("iCase ID contains '-'. Using display_name as case _id.")
        return case["display_name"]
    return case["_id"]


def get_variant_alternative(variant, category):
    """Get variant's ALT

    Args:
        variant(cyvcf2.Variant)
        category(str)
    Return:
        alternative variant: Str
    """

    if variant.ALT:
        return variant.ALT[0]
    elif not variant.ALT and category == "str":
        return "."


def set_mei_info(variant: Variant, parsed_variant: Dict[str, Any]):
    """
    ################# Add MEI info ##################
    """
    mei_info = parse_mei_info(variant.INFO.get("MEINFO"))
    if mei_info:
        parsed_variant["mei_name"] = mei_info["name"]
        parsed_variant["mei_polarity"] = mei_info["polarity"]


def parse_mei_info(mei_info: str) -> Optional[dict]:
    """Parse variants MEINFO field into a mei info dict

    <ID=MEINFO,Number=4,Type=String,Description="Mobile element info of the form NAME,START,END,POLARITY">

    Returns:
        mei info dict with keys name, start, end, polariry.
    """

    if not mei_info:
        return

    mei = mei_info.split(",")
    if len(mei) != 4:
        return

    return {
        "name": mei[0],
        "start": mei[1],
        "end": mei[2],
        "polarity": mei[3],
    }


def get_filters(variant):
    """Get variant filters

    Args:
        variant(cyvcf2.Variant)
    Return:
        variant filter()
    """
    if variant.FILTER:
        return variant.FILTER.split(";")
    return ["PASS"]


def get_samples(variant, individual_positions, case):
    """Get samples

    Args:
        variant(cyvcf2.Variant)
        individual_positions(dict):
        case(dict)
    Return:
        variant filter
    """
    if individual_positions and case["individuals"]:
        return parse_genotypes(variant, case["individuals"], individual_positions)
    return []


def get_category(category, variant, parsed_variant):
    """Get category of variant.
    Args:
        category(str)
        variant(cyvcf2.Variant)
        parsed_variant(dict)
    Return:
        category(str)
    """
    if category:
        return category

    var_type = variant.var_type
    if var_type == "indel":
        return "snv"
    if var_type == "snp":
        return "snv"
    if var_type == "mnp":
        LOG.warning("Category MNP found: {}".format(parsed_variant["ids"]["display_name"]))
        return "snv"
    return var_type


def set_dbsnp_id(parsed_variant, variant_id):
    """Set dbsnp id
    Args:
        parsed_variant(dict)
        variant_id(str)
    """
    if variant_id and "rs" in variant_id:
        parsed_variant["dbsnp_id"] = variant_id


def set_str_info(variant: Variant, parsed_variant: Dict[str, Any]):
    """
    ################ Add STR info if present ################
    """
    # repeat id generally corresponds to gene symbol
    parsed_variant["str_repid"] = call_safe(str, variant.INFO.get("REPID"))

    # repeat unit - used e g in PanelApp naming of STRs
    parsed_variant["str_ru"] = call_safe(str, variant.INFO.get("RU"))

    # repeat unit - used e g in PanelApp naming of STRs
    parsed_variant["str_display_ru"] = call_safe(str, variant.INFO.get("DisplayRU"))

    # repeat ref - reference copy number
    parsed_variant["str_ref"] = call_safe(int, variant.INFO.get("REF"))

    # repeat len - number of repeats found in case
    parsed_variant["str_len"] = call_safe(int, variant.INFO.get("RL"))

    # str status - this indicates the severity of the expansion level
    parsed_variant["str_status"] = call_safe(str, variant.INFO.get("STR_STATUS"))

    # str normal max - max number of repeats to call an STR variant normal
    parsed_variant["str_normal_max"] = call_safe(int, variant.INFO.get("STR_NORMAL_MAX"))

    # str pathological min - min number of repeats to call an STR variant pathologic
    parsed_variant["str_pathologic_min"] = call_safe(int, variant.INFO.get("STR_PATHOLOGIC_MIN"))

    # str disease - disease name annotation
    parsed_variant["str_disease"] = call_safe(str, variant.INFO.get("Disease"))

    # str disease inheritance mode string annotation
    parsed_variant["str_inheritance_mode"] = call_safe(str, variant.INFO.get("InheritanceMode"))


def set_fusion_info(variant: Variant, parsed_variant: Dict[str, Any]):
    """Add Fusion information if present."""

    def replace_nan(value: str, nan_value: str = "nan", replace_by: Any = "") -> str:
        if value == nan_value:
            return replace_by
        else:
            return value

    def set_found_db(found_db_info: Optional[str]) -> Optional[List[str]]:
        """Set the found_db value according to the value found in the VCF."""
        if found_db_info not in [None, "[]", ""]:
            return found_db_info.split(",")

    parsed_variant["gene_a"] = call_safe(str, variant.INFO.get("GENEA", ""))
    parsed_variant["gene_b"] = call_safe(str, variant.INFO.get("GENEB", ""))
    parsed_variant["tool_hits"] = call_safe(int, variant.INFO.get("TOOL_HITS", 0))
    parsed_variant["found_db"] = set_found_db(call_safe(str, variant.INFO.get("FOUND_DB")))
    parsed_variant["fusion_score"] = call_safe(float, variant.INFO.get("SCORE", None))
    parsed_variant["hgnc_id_a"] = call_safe(int, variant.INFO.get("HGNC_ID_A", 0))
    parsed_variant["hgnc_id_b"] = call_safe(int, variant.INFO.get("HGNC_ID_B", 0))
    parsed_variant["orientation"] = replace_nan(
        call_safe(str, variant.INFO.get("ORIENTATION", "")), nan_value="nan,nan"
    )
    parsed_variant["frame_status"] = call_safe(
        str, replace_nan(variant.INFO.get("FRAME_STATUS", ""))
    )
    parsed_variant["transcript_id_a"] = call_safe(
        str, replace_nan(variant.INFO.get("TRANSCRIPT_ID_A", ""))
    )
    parsed_variant["transcript_id_b"] = call_safe(
        str, replace_nan(variant.INFO.get("TRANSCRIPT_ID_B", ""))
    )
    parsed_variant["exon_number_a"] = call_safe(
        str, call_safe(int, replace_nan(variant.INFO.get("EXON_NUMBER_A", "")))
    )
    parsed_variant["exon_number_b"] = call_safe(
        str, call_safe(int, replace_nan(variant.INFO.get("EXON_NUMBER_B", "")))
    )
    parsed_variant["fusion_genes"] = [parsed_variant["gene_a"], parsed_variant["gene_b"]]


def add_gene_and_transcript_info_for_fusions(
    parsed_variant: Dict[str, Any]
) -> List[Optional[Dict]]:
    """Add gene and transcript info for fusions. Return list of parsed
    transcripts for later use in parsing.
        Args:
            parsed_variant(dict)
        Return:
            parsed_transcripts(list)
    """
    parsed_transcripts = []
    genes = []
    for suffix in ["a", "b"]:
        genes.append(
            {
                "hgnc_symbol": parsed_variant[f"gene_{suffix}"],
                "hgnc_id": parsed_variant[f"hgnc_id_{suffix}"],
                "transcripts": [],
            }
        )
        # If fusions have transcript information about both fusion partners
        if parsed_variant["transcript_id_a"] and parsed_variant["transcript_id_b"]:
            parsed_transcripts.append(
                {
                    "transcript_id": parsed_variant[f"transcript_id_{suffix}"],
                    "hgnc_id": parsed_variant[f"hgnc_id_{suffix}"],
                    "hgnc_symbol": parsed_variant[f"gene_{suffix}"],
                    "exon": parsed_variant[f"exon_number_{suffix}"],
                }
            )

    # Add transcript info to genes if available
    if parsed_transcripts:
        genes[0]["transcripts"] = [parsed_transcripts[0]]
        genes[1]["transcripts"] = [parsed_transcripts[1]]

    # Add hgnc_id to variant if available
    hgnc_ids = []
    if parsed_variant["hgnc_id_a"] and parsed_variant["hgnc_id_b"]:
        hgnc_ids = [gene["hgnc_id"] for gene in genes]
        parsed_variant["genes"] = genes

    parsed_variant["hgnc_ids"] = hgnc_ids

    return parsed_transcripts


def set_str_source(parsed_variant: Dict[str, Any], variant: Variant):
    """Set source in parsed_variant"""
    str_source_display = variant.INFO.get("SourceDisplay")
    str_source_type = variant.INFO.get("Source")
    str_source_id = variant.INFO.get("SourceId")
    if str_source_display or str_source_type or str_source_id:
        source = {
            "display": str_source_display,
            "type": str_source_type,
            "id": str_source_id,
        }
        parsed_variant["str_source"] = source


def set_mitomap_associated_diseases(parsed_variant, variant):
    """Set mitomap_associated_diseases in parsed_variant
    Args:
        parsed_variant(dict)
        variant(cyvcf2.Variant)
    """
    mitomap_associated_diseases = variant.INFO.get("MitomapAssociatedDiseases")
    if mitomap_associated_diseases and mitomap_associated_diseases != ".":
        parsed_variant["mitomap_associated_diseases"] = str(
            mitomap_associated_diseases.replace("_", " ")
        )


def add_gene_and_transcript_info(parsed_variant, variant, vep_header):
    """Add gene info and transcript info. Return list of parsed
    transcripts for later use in parsing.
       Args:
           parsed_variant(dict)
           variant(cyvcf2.Variant)
           vep_header(list)
       Return:
           parsed_transcripts(list)
    """

    raw_transcripts = []
    parsed_transcripts = []
    dbsnp_ids = set()
    cosmic_ids = set()

    if vep_header:
        vep_info = variant.INFO.get("CSQ")
        if vep_info:
            raw_transcripts = (
                dict(zip(vep_header, transcript_info.split("|")))
                for transcript_info in vep_info.split(",")
            )

    for parsed_transcript in parse_transcripts(raw_transcripts):
        parsed_transcripts.append(parsed_transcript)

        for dbsnp in parsed_transcript.get("dbsnp", []):
            dbsnp_ids.add(dbsnp)
        for cosmic in parsed_transcript.get("cosmic", []):
            cosmic_ids.add(cosmic)

    # The COSMIC tag in INFO is added via VEP and/or bcftools annotate
    cosmic_tag = variant.INFO.get("COSMIC")
    if cosmic_tag:
        for cosmic_id in cosmic_tag.split("&"):
            cosmic_ids.add(cosmic_id)

    if dbsnp_ids and not parsed_variant.get("dbsnp_id"):
        parsed_variant["dbsnp_id"] = ";".join(dbsnp_ids)

    if cosmic_ids:
        parsed_variant["cosmic_ids"] = list(cosmic_ids)

    parsed_variant["genes"] = parse_genes(parsed_transcripts)
    hgnc_ids = set([])

    for gene in parsed_variant["genes"]:
        hgnc_ids.add(gene["hgnc_id"])

    # STR HGNCIds are annotated by Stranger
    str_hgnc_id = variant.INFO.get("HGNCId")
    if str_hgnc_id:
        hgnc_ids.add(str_hgnc_id)

    parsed_variant["hgnc_ids"] = list(hgnc_ids)
    return parsed_transcripts


def set_clnsig(parsed_variant, variant, parsed_transcripts):
    """Set clnsig in parsed_variant
    Args:
        parsed_variant(dict)
        variant(cyvcf2.Variant)
        parsed_transcripts(list)
    """
    # XXX: Why is clnsig_predictions set to emtpy list and then compared?
    clnsig_predictions = []
    if len(clnsig_predictions) == 0 and len(parsed_transcripts) > 0:
        # Parse INFO fielf to collect clnsig info
        clnsig_predictions = parse_clnsig(variant, transcripts=parsed_transcripts)

    parsed_variant["clnsig"] = clnsig_predictions


def set_rank_result(parsed_variant, variant, rank_results_header):
    """Set rank_result in parsed_variant
    Args:
        parsed_variant(dict)
        variant(cyvcf2.Variant)
        rank_results_header(list)
    """
    rank_result = variant.INFO.get("RankResult")
    if rank_result:
        results = [int(i) for i in rank_result.split("|")]
        parsed_variant["rank_result"] = dict(zip(rank_results_header, results))


def set_local_archive_info(parsed_variant, local_archive_info):
    """Set local_archive_info in parsed_variant
    Args:
        parsed_variant(dict)
        local_archive_info(dict)
    """
    if local_archive_info is None:
        return None
    if "Date" in local_archive_info:
        parsed_variant["local_obs_old_date"] = local_archive_info.get("Date")
    if "NrCases" in local_archive_info:
        parsed_variant["local_obs_old_nr_cases"] = local_archive_info.get("NrCases")
    if "Description" in local_archive_info:
        parsed_variant["local_obs_old_desc"] = local_archive_info.get("Description")


def add_hmtvar(parsed_variant, variant):
    """Set hmtvar in parsed_variant
    Args:
        parsed_variant(dict)
        variant(cyvcf2.Variant)
    """
    hmtvar_variant_id = variant.INFO.get("HmtVar")
    if hmtvar_variant_id and hmtvar_variant_id != ".":
        parsed_variant["hmtvar_variant_id"] = int(hmtvar_variant_id)


def parse_custom_data(custom_str):
    """Parse SCOUT_CUSTOM info field

    Input: "key1|val1,key2|val2"
    Output: [ ["key1","val1"], ["key2", "val2"] ]

    """
    pair_list = []
    try:
        for pair in custom_str.split(","):
            pair_list.append(pair.split("|"))
        return pair_list
    except AttributeError:
        return None
