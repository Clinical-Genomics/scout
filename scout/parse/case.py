import logging
from typing import Any, Dict, Tuple

from ped_parser import FamilyParser

from scout.constants import PHENOTYPE_MAP, REV_SEX_MAP, SEX_MAP
from scout.exceptions import PedigreeError
from scout.models.case.case_loading_models import CaseLoader
from scout.parse.mitodel import parse_mitodel_file
from scout.parse.pedqc import (
    parse_peddy_ped,
    parse_peddy_ped_check,
    parse_peddy_sex_check,
    parse_somalier_ancestry,
    parse_somalier_pairs,
    parse_somalier_samples,
)
from scout.parse.smn import parse_smn_file

LOG = logging.getLogger(__name__)


def parse_case_data(**kwargs):
    """Parse all data necessary for loading a case into scout

    This can be done either by providing a VCF file and other information
    on the command line. Or all the information can be specified in a config file.
    Please see Scout documentation for further instructions.

    Possible keyword args are formally available in the CaseLoader class, but here is a common list with explanations:
        cnv_report: Path to pdf file with CNV report
        config(dict): A yaml formatted config file
        coverage_qc_report: Path to html file with coverage and qc report
        gene_fusion_report: Path to the gene fusions report
        gene_fusion_report_research: Path to the gene fusions research report
        multiqc(str): Path to dir with multiqc information
        owner(str): The institute that owns a case
        ped(iterable(str)): A ped formatted family file
        peddy_ped(str): Path to a peddy ped
        RNAfusion_inspector: Path to the RNA fusion inspector report
        RNAfusion_inspector_research: Path to the research RNA fusion inspector report
        RNAfusion_report: Path to the RNA fusion report
        RNAfusion_report_research: Path to the research RNA fusion report
        smn_tsv(str): Path to an SMN tsv file
        status(str): Optional case status ("prioritized", "inactive", "ignored", "active", "solved", "archived")
        vcf_cancer(str): Path to a vcf file
        vcf_cancer_sv(str): Path to a vcf file
        vcf_fusion(str): Path to a vcf file
        vcf_mei(str): Path to a vcf file
        vcf_snv(str): Path to a vcf file
        vcf_str(str): Path to a VCF file
        vcf_sv(str): Path to a vcf file

    Returns:
        config_data(dict): Holds all the necessary information for loading
                           Scout
    """
    config = kwargs.pop("config", {})

    # populate configuration according to Pydantic defined classes
    config_dict: dict = parse_case_config(config=config)

    # If ped file  provided we need to parse that first
    if kwargs.get("ped"):
        LOG.warning(
            "Loading cases using .ped files is deprecated and will be no longer supported in the future. Load cases using .yaml config files instead.",
        )
        family_id, samples = parse_ped(kwargs["ped"])
        config_dict["family"] = family_id
        config_dict["samples"] = samples

    # Give passed keyword arguments precedence over file configuration
    # Except for 'owner', precedence config file over arguments
    if "owner" in config_dict:
        kwargs.pop("owner", None)
    for key in kwargs:
        if kwargs[key] is not None:
            config_dict[key] = kwargs[key]
        else:
            try:
                config_dict[key] = config[key]
            except KeyError:
                config_dict[key] = None

    # This will add pedigree qc information from Peddy and Somalier to the individuals.
    # Let the newer Somalier have the last word if there is any disagreement
    add_peddy_information(config_dict)
    add_somalier_information(config_dict)

    if config_dict.get("smn_tsv"):
        add_smn_info(config_dict)

    add_mitodel_info(config_dict)

    # Ensure case_id is set, this situation arises when case is loaded with ped file
    if config_dict.get("case_id") is None:
        config_dict["case_id"] = config_dict["family"]

    if config_dict.get("smn_tsv"):
        add_smn_info_case(config_dict)

    return remove_none_recursive(config_dict)


def parse_case_config(config: dict) -> dict:
    """Parse configuration data for a case. Returns a dict"""
    if config == {}:
        LOG.warning("No configuration in command: {}".format(config))
        return {}
    return CaseLoader(**config).model_dump()


def add_mitodel_info(config_data):
    """Add mitodel data from short mitoSign txt files to individuals

    Args:
        config_data(dict)
    """

    for individual in config_data.get("individuals", []):
        mitodel_file = individual.get("mitodel_file")
        if not mitodel_file:
            continue

        LOG.info(
            "Adding mitosign info from {} to {}".format(mitodel_file, individual["individual_id"])
        )

        file_handle = open(mitodel_file, "r")
        individual["mitodel"] = parse_mitodel_file(file_handle)


def add_smn_info(config_data):
    """Add SMN CN / SMA prediction from TSV files to individuals

    Args:
        config_data(dict)
    """
    LOG.info("Adding SMN info from {}.".format(config_data["smn_tsv"]))
    if not config_data.get("smn_tsv"):
        LOG.warning("No smn_tsv though add_smn_info called. This is odd.")
        return

    file_handle = open(config_data["smn_tsv"], "r")
    smn_info = {}
    for smn_ind_info in parse_smn_file(file_handle):
        smn_info[smn_ind_info["sample_id"]] = smn_ind_info

    for ind in config_data["individuals"]:
        ind_id = ind["individual_id"]
        try:
            for key in [
                "is_sma",
                "is_sma_carrier",
                "smn1_cn",
                "smn2_cn",
                "smn2delta78_cn",
                "smn_27134_cn",
            ]:
                ind[key] = smn_info[ind_id][key]
        except KeyError as err:
            LOG.warning("Individual {} has no SMN info to update: {}.".format(ind_id, err))


def add_smn_info_case(case_data):
    """Add SMN CN / SMA prediction from TSV files to individuals in a yaml load case context

    Args:
        case_data(dict)
    """

    if not case_data.get("smn_tsv"):
        LOG.warning("No smn_tsv though add_smn_info_case called. This is odd.")
        return

    file_handle = open(case_data["smn_tsv"], "r")
    smn_info = {}
    for smn_ind_info in parse_smn_file(file_handle):
        smn_info[smn_ind_info["sample_id"]] = smn_ind_info

    for ind in case_data["individuals"]:
        ind_id = ind["individual_id"]
        try:
            for key in [
                "is_sma",
                "is_sma_carrier",
                "smn1_cn",
                "smn2_cn",
                "smn2delta78_cn",
                "smn_27134_cn",
            ]:
                ind[key] = smn_info[ind_id][key]
        except KeyError as err:
            LOG.warning(f"Individual {ind_id} has no SMN info to update: {err}.")


def set_somalier_sex_check_ind(ind: Dict[str, str], sex_check: Dict[str, Dict[str, str]]):
    """Check if Somalier has inferred the sex"""

    ind_id = ind["individual_id"]
    if ind_id in sex_check and all(
        key in sex_check[ind_id] for key in ("sex", "original_pedigree_sex")
    ):
        ind["confirmed_sex"]: bool = (
            sex_check[ind_id]["sex"] == REV_SEX_MAP[sex_check[ind_id]["original_pedigree_sex"]]
        )


def set_somalier_confirmed_parent(
    analysis_inds: Dict[str, Any], ind: Dict[str, Any], ped_check: Dict[Tuple, Any]
):
    """Check if Somalier confirmed parental relations.
    First, check that we are looking at individual with parents.
    Double-check that the child/parent pair is in somalier data and set ok.
    If we demand Somalier be run with "relate --infer" we can skip this.
    """

    ind_id = ind["individual_id"]
    for parent in ["mother", "father"]:
        parent_id = ind[parent]
        if parent_id == "0":
            continue

        for pair in ped_check:
            if ind_id not in pair or parent_id not in pair:
                continue
            if (
                ped_check[pair]["relatedness"] > 0.32
                and ped_check[pair]["relatedness"] < 0.67
                and ped_check[pair]["ibs0"] / ped_check[pair]["ibs2"] < 0.014
            ):
                analysis_inds[parent_id]["confirmed_parent"] = True
                continue
            # else if parent confirmation failed
            analysis_inds[parent_id]["confirmed_parent"] = False


def set_somalier_sex_and_relatedness_checks(
    case_config: dict,
    ped_check: Dict[Tuple, Any],
    sex_check: Dict[str, Dict],
    ancestry_info: Dict[str, Dict],
):
    """
    Update ancestry, sex and relatedness checks for individuals in case config based on parsed Somalier file content.
    """
    analysis_inds = {}
    for ind in case_config["individuals"]:
        ind_id = ind["individual_id"]
        analysis_inds[ind_id] = ind

    for ind_id in analysis_inds:
        ind = analysis_inds[ind_id]
        # Check if Somalier has inferred the ancestry
        if ind_id in ancestry_info:
            ind["predicted_ancestry"]: str = ancestry_info[ind_id].get(
                "predicted_ancestry", "UNKNOWN"
            )
        set_somalier_sex_check_ind(ind, sex_check)
        set_somalier_confirmed_parent(analysis_inds, ind, ped_check)


def add_somalier_information(case_config: dict):
    """
    Parse any somalier files, and update ancestry, sex and relatedness checks for individuals in case config
    based on them.
    """
    ped_check = {}
    sex_check = {}
    ancestry_info = {}

    if case_config.get("somalier_pairs"):
        with open(case_config["somalier_pairs"], "r") as file_handle:
            for pair_info in parse_somalier_pairs(file_handle):
                ped_check[(pair_info["sample_a"], pair_info["sample_b"])] = pair_info

    if case_config.get("somalier_samples"):
        with open(case_config["somalier_samples"], "r") as file_handle:
            for ind_info in parse_somalier_samples(file_handle):
                sex_check[ind_info["sample_id"]] = ind_info

    if case_config.get("somalier_ancestry"):
        with open(case_config["somalier_ancestry"], "r") as file_handle:
            for ind_info in parse_somalier_ancestry(file_handle):
                ancestry_info[ind_info["sample_id"]] = ind_info

    if not (ped_check or sex_check or ancestry_info):
        return

    LOG.info("Adding Somalier info")
    set_somalier_sex_and_relatedness_checks(case_config, ped_check, sex_check, ancestry_info)


def add_peddy_information(config_data):
    """Add information from peddy outfiles to the individuals

    Args:
        config_data(dict)
    """
    ped_info = {}
    ped_check = {}
    sex_check = {}

    if config_data.get("peddy_ped"):
        with open(config_data["peddy_ped"], "r") as file_handle:
            for ind_info in parse_peddy_ped(file_handle):
                ped_info[ind_info["sample_id"]] = ind_info

    if config_data.get("peddy_ped_check"):
        with open(config_data["peddy_ped_check"], "r") as file_handle:
            for pair_info in parse_peddy_ped_check(file_handle):
                ped_check[(pair_info["sample_a"], pair_info["sample_b"])] = pair_info

    if config_data.get("peddy_sex_check"):
        with open(config_data["peddy_sex_check"], "r") as file_handle:
            for ind_info in parse_peddy_sex_check(file_handle):
                sex_check[ind_info["sample_id"]] = ind_info

    if not ped_info:
        return

    analysis_inds = {}
    for ind in config_data["individuals"]:
        ind_id = ind["individual_id"]
        analysis_inds[ind_id] = ind

    for ind_id in analysis_inds:
        ind = analysis_inds[ind_id]
        # Check if peddy has inferred the ancestry
        if ind_id in ped_info:
            ind["predicted_ancestry"] = ped_info[ind_id].get("ancestry-prediction", "UNKNOWN")
        # Check if peddy has inferred the sex
        if ind_id in sex_check:
            if sex_check[ind_id]["error"]:
                ind["confirmed_sex"] = False
            else:
                ind["confirmed_sex"] = True
        # Check if peddy har confirmed parental relations
        for parent in ["mother", "father"]:
            # If we are looking at individual with parents
            parent_id = ind[parent]
            if parent_id == "0":
                continue
            # Check if the child/parent pair is in peddy data
            for pair in ped_check:
                if not (ind_id in pair and parent_id in pair):
                    continue
                if ped_check[pair]["parent_error"]:
                    analysis_inds[parent_id]["confirmed_parent"] = False
                    continue
                # Else if parent confirmation has not been done
                if (
                    "confirmed_parent" not in analysis_inds[parent_id]
                    or analysis_inds[parent_id]["confirmed_parent"] is None
                ):
                    # Set confirmatio to True
                    analysis_inds[parent_id]["confirmed_parent"] = True


def parse_ped(ped_stream, family_type="ped"):
    """Parse out minimal family information from a PED file.

    Args:
        ped_stream(iterable(str))
        family_type(str): Format of the pedigree information

    Returns:
        family_id(str), samples(list[dict])
    """
    pedigree = FamilyParser(ped_stream, family_type=family_type)

    if len(pedigree.families) != 1:
        raise PedigreeError("Only one case per ped file is allowed")

    family_id = list(pedigree.families.keys())[0]
    family = pedigree.families[family_id]

    samples = [
        {
            "sample_id": ind_id,
            "father": individual.father,
            "mother": individual.mother,
            # Convert sex to human readable
            "sex": SEX_MAP[individual.sex],
            "phenotype": PHENOTYPE_MAP[int(individual.phenotype)],
        }
        for ind_id, individual in family.individuals.items()
    ]
    return family_id, samples


def remove_none_values(dictionary):
    """If value = None in key/value pair, the pair is removed.
        Python >3
    Args:
        dictionary: dict

    Returns:
        dict
    """

    return {k: v for k, v in dictionary.items() if v is not None}


def remove_none_recursive(dictionary):
    """Recursively remove None from dictionary"""
    return remove_none_recursive_aux(dictionary, {})


def remove_none_recursive_aux(dictionary, new_dict):
    """Auxilary Function to remove_none_recursive. Recursively removes
    None from dictionary by adding non-None key/value pairs to new_dict.
    Args:
        dictionary: dict with configuration values
        new_dict: assembly dict
    Return:
        dictionary with no None values"""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            clean_value = remove_none_recursive(value)
            if len(clean_value) > 0:
                new_dict.update({key: clean_value})
        elif (
            isinstance(value, list)
            and len(value) > 0
            and key
            not in [
                "capture_kits",
                "collaborators",
                "cohorts",
                "default_panels",
                "default_gene_panels",
                "gene_panels",
                "synopsis",
                "phenotype_groups",
                "phenotype_terms",
                "panel",
            ]
        ):
            new_list = [remove_none_recursive_aux(item, {}) for item in value]
            new_dict.update({key: new_list})
        elif value is not None:
            new_dict.update({key: value})
        else:
            continue
    return new_dict
