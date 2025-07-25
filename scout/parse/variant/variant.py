import logging
from typing import Any, Dict, List, Optional

from cyvcf2 import Variant

from scout.constants import CHR_PATTERN, DNA_SAMPLE_VARIANT_CATEGORIES
from scout.exceptions import VcfError
from scout.utils.convert import call_safe
from scout.utils.dict_utils import remove_nonetype

from .callers import parse_callers
from .clnsig import parse_clnsig, parse_clnsig_onc
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
    case: dict,
    variant_type: str = "clinical",
    rank_results_header: list = None,
    vep_header: list = None,
    individual_positions: dict = None,
    category: str = None,
    local_archive_info: dict = None,
) -> dict:
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

    # Create the ID for the variant
    case_id = case["_id"]

    genmod_key = get_genmod_key(case)
    chrom_match = CHR_PATTERN.match(variant.CHROM)
    chrom = chrom_match.group(2)

    ### We always assume split and normalized vcfs!!!
    if len(variant.ALT) > 1:
        raise VcfError("Variants are only allowed to have one alternative")

    # Builds a dictionary with the different ids that are used
    parsed_variant = {
        "case_id": case_id,
        "variant_type": variant_type,
        "reference": variant.REF,
        "quality": variant.QUAL,  # cyvcf2 will set QUAL to None if '.' in vcf
        "filters": get_filters(variant),
        "chromosome": chrom,
        "compounds": parse_compounds(
            compound_info=variant.INFO.get("Compounds"),
            case_id=genmod_key,
            variant_type=variant_type,
        ),
        "rank_score": parse_rank_score(variant.INFO.get("RankScore", ""), genmod_key) or 0,
        "norm_rank_score": parse_rank_score(variant.INFO.get("RankScoreNormalized", ""), genmod_key)
        or 0,
        "genetic_models": parse_genetic_models(variant.INFO.get("GeneticModels"), genmod_key),
        "str_swegen_mean": call_safe(float, variant.INFO.get("SweGenMean")),
        "str_swegen_std": call_safe(float, variant.INFO.get("SweGenStd")),
        "somatic_score": call_safe(int, variant.INFO.get("SOMATICSCORE")),
        "custom": parse_custom_data(variant.INFO.get("SCOUT_CUSTOM")),
    }
    category = get_and_set_category(parsed_variant, variant, category)
    alt = get_and_set_variant_alternative(parsed_variant, variant, category)

    parsed_variant["ids"] = parse_ids(
        chrom=chrom,
        pos=variant.POS,
        ref=variant.REF,
        alt=alt,
        case_id=case_id,
        variant_type=variant_type,
    )

    set_coordinates(parsed_variant, variant, case, category)

    parsed_variant["samples"] = get_samples(variant, individual_positions, case, category)

    set_dbsnp_id(parsed_variant, variant.ID)

    # This is the id of other position in translocations
    # (only for specific svs)
    parsed_variant["mate_id"] = None

    ################# Add autozygosity calls if present #################
    parsed_variant["azlength"] = call_safe(int, variant.INFO.get("AZLENGTH"))
    parsed_variant["azqual"] = call_safe(float, variant.INFO.get("AZQUAL"))

    # STR variant info
    set_str_info(variant, parsed_variant)
    # STR source dict with display string, source type and entry id
    set_str_source(parsed_variant, variant)

    # MEI variant info
    set_mei_info(variant, parsed_variant)

    # Add Fusion info
    set_fusion_info(variant, parsed_variant)

    ################# Add mitomap info, from HmtNote #################
    set_mitomap_associated_diseases(parsed_variant, variant)

    ################# Add HmtVar variant id, from HmtNote #################
    add_hmtvar(parsed_variant, variant)

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

    set_loqus_archive_frequencies(parsed_variant, variant, local_archive_info)

    set_severity_predictions(parsed_variant, variant, parsed_transcripts)

    ###################### Add conservation ######################
    parsed_variant["conservation"] = parse_conservations(variant, parsed_transcripts)

    parsed_variant["callers"] = parse_callers(variant, category=category)
    set_rank_result(parsed_variant, variant, rank_results_header)

    ##################### Add type specific #####################
    set_sv_specific_annotations(parsed_variant, variant)

    set_mei_specific_annotations(parsed_variant, variant)

    set_cancer_specific_annotations(parsed_variant, variant)

    remove_nonetype(parsed_variant)
    return parsed_variant


def set_coordinates(parsed_variant: dict, variant: dict, case: dict, category: str):
    """
    Parse and set coordinate annotations
    """
    coordinates = parse_coordinates(variant, category, case.get("genome_build"))
    parsed_variant.update(
        {
            "cytoband_end": coordinates["cytoband_end"],
            "cytoband_start": coordinates["cytoband_start"],
            "end": coordinates["end"],
            "end_chrom": coordinates["end_chrom"],
            "length": coordinates["length"],
            "mate_id": coordinates["mate_id"],
            "position": coordinates["position"],
            "sub_category": coordinates["sub_category"],
        }
    )


def set_mei_specific_annotations(parsed_variant: dict, variant: dict):
    """Add MEI specific annotations"""
    if parsed_variant.get("category") in ["mei"]:
        mei_frequencies = parse_mei_frequencies(variant)
        for key in mei_frequencies:
            parsed_variant["frequencies"][key] = mei_frequencies[key]


def set_cancer_specific_annotations(parsed_variant: dict, variant: dict):
    """
    ###################### Add Cancer specific annotations ######################
    # MSK_MVL indicates if variants are in the MSK managed variant list
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5437632/
    """
    if variant.INFO.get("MSK_MVL"):
        parsed_variant["mvl_tag"] = True


def set_sv_specific_annotations(parsed_variant: dict, variant: dict):
    """
    Add SV specific annotations
    """
    if parsed_variant.get("category") in ["sv", "cancer_sv"]:
        sv_frequencies = parse_sv_frequencies(variant)
        for key in sv_frequencies:
            parsed_variant["frequencies"][key] = sv_frequencies[key]


def set_loqus_archive_frequencies(parsed_variant: dict, variant: dict, local_archive_info: dict):
    """
    loqusdb archive frequencies
    Fist, RD germline, for MIP and Balsamic
    Then, Cancer (Balsamic) Germline and Somatic loqus archives
    SNVs contain INFO field Obs, SVs contain clinical_genomics_loqusObs
    """

    def safe_val(val):
        """Convert -1 to None, leave other values unchanged."""
        return None if val == -1 else val

    info = variant.INFO

    # RD observations (SNVs or SVs)
    local_obs_old = (
        info.get("Obs") or info.get("clinical_genomics_loqusObs") or info.get("clin_obs")
    )
    parsed_variant["local_obs_old"] = safe_val(call_safe(int, local_obs_old))
    parsed_variant["local_obs_hom_old"] = safe_val(call_safe(int, info.get("Hom")))
    parsed_variant["local_obs_old_freq"] = safe_val(
        call_safe(float, info.get("clinical_genomics_loqusFrq") or info.get("Frq"))
    )

    # Optional local archive metadata
    set_local_archive_info(parsed_variant, local_archive_info)

    # Cancer observations (germline and somatic)
    FREQ_KEYS = ["Cancer_Germline", "Cancer_Somatic", "Cancer_Somatic_Panel"]
    for prefix in FREQ_KEYS:
        key = prefix.lower()
        parsed_variant[f"local_obs_{key}_old"] = safe_val(call_safe(int, info.get(f"{prefix}_Obs")))
        parsed_variant[f"local_obs_{key}_hom_old"] = safe_val(
            call_safe(int, info.get(f"{prefix}_Hom"))
        )
        parsed_variant[f"local_obs_{key}_old_freq"] = safe_val(
            call_safe(float, info.get(f"{prefix}_Frq"))
        )


def set_severity_predictions(parsed_variant: dict, variant: dict, parsed_transcripts: dict):
    """
    Set severity predictions on parsed variant.
    """

    parsed_variant["cadd_score"] = parse_cadd(variant, parsed_transcripts)
    parsed_variant["spidex"] = call_safe(float, variant.INFO.get("SPIDEX"))

    if len(parsed_transcripts) > 0:
        parsed_variant["revel_score"] = parsed_transcripts[0].get(
            "revel_rankscore"
        )  # This is actually the value of REVEL_rankscore
        parsed_variant["revel"] = get_highest_revel_score(parsed_transcripts)


def get_highest_revel_score(parsed_transcripts: List[dict]) -> Optional[float]:
    """Retrieve the highest REVEL_score value from parsed variant transcripts."""
    tx_revel_scores: List(float) = [
        tx.get("revel_raw_score") for tx in parsed_transcripts if tx.get("revel_raw_score") != None
    ]
    if tx_revel_scores:
        return max(tx_revel_scores)


def get_genmod_key(case):
    """Gen genmod key

    Args:
        case(dict)
    Return:
        case._id(str) or case.display_name(str)
    """
    case_id = case["_id"]
    if "-" in case_id:
        return case["display_name"]
    return case["_id"]


def get_and_set_variant_alternative(parsed_variant: dict, variant: Variant, category: str) -> str:
    """Get and set variant's ALT as alternative"""

    if variant.ALT:
        alt = variant.ALT[0]
    elif not variant.ALT and category == "str":
        alt = "."
    parsed_variant["alternative"] = alt
    return alt


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


def get_samples(variant: Variant, individual_positions: dict, case: dict, category: str) -> List:
    """Get samples

    Add GT calls to individuals.

    Do not add individuals if they are not wanted based on the analysis type,
    eg a WTS only individual for a DNA SNV variant.
    """
    invalid_sample_types: List[str] = []
    if category in DNA_SAMPLE_VARIANT_CATEGORIES:
        invalid_sample_types = ["wts"]

    if individual_positions and bool(case["individuals"]):
        individuals = [
            ind
            for ind in case["individuals"]
            if ind.get("analysis_type") not in invalid_sample_types
        ]
        return parse_genotypes(variant, individuals, individual_positions)
    return []


def get_and_set_category(parsed_variant: dict, variant: Variant, category: str) -> str:
    """Set category of variant. Convenience return of category.

    If category not set, use variant type, but convert types SNP or INDEL (or old MNP) to "snv".
    """
    if category:
        parsed_variant["category"] = category
        return category

    category = variant.var_type
    if category in ["indel", "snp"]:
        category = "snv"
    if category == "mnp":
        category = "snv"
        LOG.warning("Category MNP found for variant. Setting to SNV.")

    parsed_variant["category"] = category
    return category


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

    # repeat id from trgt - generally corresponds to gene symbol and/or disease
    parsed_variant["str_trid"] = call_safe(str, variant.INFO.get("TRID"))

    # repeat unit - used e g in PanelApp naming of STRs
    parsed_variant["str_struc"] = call_safe(str, variant.INFO.get("STRUC"))

    # repeat motif(s) - used e g in TRGT MC motif splits
    parsed_variant["str_motifs"] = call_safe(str, variant.INFO.get("MOTIFS"))

    # repeat pathologic motifs structure - list of indicies of pathologic motifs counting towards MC
    parsed_variant["str_pathologic_struc"] = call_safe(str, variant.INFO.get("PathologicStruc"))

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
    parsed_variant: Dict[str, Any],
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
    hgnc_ids = []
    hgnc_symbols = []

    for suffix in ["a", "b"]:
        # If fusions have transcript information about a fusion partner
        parsed_transcript = {}
        if parsed_variant.get(f"transcript_id_{suffix}"):
            # Add transcript info to genes if available
            parsed_transcript = {
                "transcript_id": parsed_variant[f"transcript_id_{suffix}"],
                "hgnc_id": parsed_variant[f"hgnc_id_{suffix}"],
                "hgnc_symbol": parsed_variant[f"gene_{suffix}"],
                "exon": parsed_variant[f"exon_number_{suffix}"],
            }
            parsed_transcripts.append(parsed_transcript)

        if parsed_variant.get(f"hgnc_id_{suffix}"):
            if parsed_variant.get(f"gene_{suffix}"):
                # Add hgnc_symbol to variant if available
                hgnc_symbols.append(parsed_variant.get(f"gene_{suffix}"))

            # Add hgnc_id to variant if available
            hgnc_ids.append(parsed_variant.get(f"hgnc_id_{suffix}"))

            genes.append(
                {
                    "hgnc_symbol": parsed_variant[f"gene_{suffix}"],
                    "hgnc_id": parsed_variant[f"hgnc_id_{suffix}"],
                    "transcripts": [parsed_transcript] if parsed_transcript else [],
                }
            )

    parsed_variant["genes"] = genes
    parsed_variant["hgnc_ids"] = hgnc_ids
    parsed_variant["hgnc_symbols"] = hgnc_symbols

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
    clnsig_predictions = parse_clnsig(variant, transcripts=parsed_transcripts)
    parsed_variant["clnsig"] = clnsig_predictions

    clnsig_onco_predictions = parse_clnsig_onc(variant)
    if clnsig_onco_predictions:
        parsed_variant["clnsig_onc"] = clnsig_onco_predictions


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
