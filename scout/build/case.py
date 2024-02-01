import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

from scout.constants import CUSTOM_CASE_REPORTS, PHENOTYPE_GROUPS
from scout.exceptions import ConfigError, IntegrityError

from . import build_individual

LOG = logging.getLogger(__name__)


def build_phenotype(phenotype_id: str, adapter) -> Dict[str, str]:
    """Build a small phenotype object

        Build a dictionary with phenotype_id and description
    Args:
        adapter: MongoAdapter (importing it for typing is a bit tricky here)

    Returns:
        dict(
            phenotype_id = str,
            feature = str, # description of phenotype
            )
    """
    phenotype_obj = {}
    phenotype = adapter.hpo_term(phenotype_id)
    if phenotype:
        phenotype_obj["phenotype_id"] = phenotype["hpo_id"]
        phenotype_obj["feature"] = phenotype["description"]
    return phenotype_obj


def _populate_pipeline_info(case_obj, case_data):
    """Populates the field named pipeline_version

    Args:
        case_obj(dict): scout.models.Case
        case_data (dict): A dictionary with the relevant case information
    """
    if case_data.get("exe_ver"):
        case_obj["pipeline_version"] = case_data["exe_ver"]


def set_abspath_case_file(case_obj: dict, case_data: dict, case_file: str):
    """Abs path case file. E.g. demo files appear as relative path files, and storing absolute paths
    ensures we do not have to load cases from the same working directory as we start the server process.
    """
    file_path = case_data.get(case_file)
    if file_path and os.path.exists(file_path):
        case_obj[case_file] = os.path.abspath(file_path)
    else:
        case_obj[case_file] = None


def set_abspath_case_nested_files(case_obj: dict, case_data: dict, nested_file_key: str):
    """Absolute path nested case files. Similar to the single abs path setter, but some paths reside nested
    directly under a particular key.
    """
    case_obj[nested_file_key] = case_data.get(nested_file_key)
    if case_obj.get(nested_file_key):
        for file_type, nested_file_item in case_obj[nested_file_key].items():
            if nested_file_item and os.path.exists(nested_file_item):
                case_obj[nested_file_key][file_type] = os.path.abspath(nested_file_item)
            else:
                case_obj[nested_file_key][file_type] = None


def set_abspath_case_nested_image_files(
    case_obj: dict,
    case_data: dict,
    nested_file_key: Optional[str] = "custom_images",
    path_key: Optional[str] = "path",
):
    """Absolute path for complexly nested custom image paths. Similar to the single abs path setter, but the custom image paths reside nested
    in arrays, with the sub-key name "path" one or two levels into the dictionary.

    E.g. case["custom_images"]["str_variants_images"][2]["path"] or
    case["custom_images"]["case_images"]["section_one"][1]["path"].
    """

    def case_images_abspath(level: Union[Dict, List]):
        """Recursively set path to abs_path for all path_key items in lists in dicts in level."""
        for sub_level in level:
            if isinstance(sub_level, dict):
                update_case_images(sub_level)
            elif isinstance(sub_level, list):
                for image in sub_level:
                    image_path = image.get(path_key)
                    if image_path and os.path.exists(image_path):
                        image[path_key] = os.path.abspath(image_path)

    case_obj[nested_file_key] = case_data.get(nested_file_key)
    case_images_abspath(case_obj[nested_file_key])


def build_case(case_data, adapter):
    """Build a case object that is to be inserted to the database

    Args:
        case_data (dict): A dictionary with the relevant case information
        adapter (scout.adapter.MongoAdapter)

    Returns:
        case_obj (dict): A case object

    dict(
        case_id = str, # required=True, unique
        display_name = str, # If not display name use case_id
        owner = str, # required

        # These are the names of all the collaborators that are allowed to view the
        # case, including the owner
        collaborators = list, # List of institute_ids
        assignee = str, # _id of a user
        individuals = list, # list of dictionaries with individuals
        created_at = datetime,
        updated_at = datetime,
        suspects = list, # List of variants referred by there _id
        causatives = list, # List of variants referred by there _id

        synopsis = str, # The synopsis is a text blob
        status = str, # default='inactive', choices=STATUS
        is_research = bool, # default=False
        research_requested = bool, # default=False
        rerun_requested = bool, # default=False
        cohorts = list, # list of strings
        analysis_date = datetime,
        analyses = list, # list of dict

        # default_panels specifies which panels that should be shown when
        # the case is opened
        panels = list, # list of dictionaries with panel information

        dynamic_gene_list = list, # List of genes

        genome_build = str, # This should be 37 or 38

        rank_model_version = str,
        rank_score_threshold = int, # default=8

        phenotype_terms = list, # List of dictionaries with phenotype information
        phenotype_groups = list, # List of dictionaries with phenotype information

        madeline_info = str, # madeline info is a full xml file

        multiqc = str, # path to dir with multiqc information

        cnv_report = str, # path to file with cnv report
        coverage_qc_report = str, # path to file with coverage and qc report
        gene_fusion_report = str, # path to the gene fusions report
        gene_fusion_report_research = str, # path to the research gene fusions report
        RNAfusion_inspector = str, # path to the RNA fusion inspector report
        RNAfusion_inspector_research = str, # path to the research RNA fusion inspector report
        RNAfusion_report = str, # path to the RNA fusion report
        RNAfusion_report_research = str, # path to the research RNA fusion report

        vcf_files = dict, # A dictionary with vcf files

        diagnosis_phenotypes = list, # List of references to diseases
        diagnosis_genes = list, # List of references to genes

        has_svvariants = bool, # default=False

        is_migrated = bool # default=False

    )
    """
    LOG.info("build case with id: {0}".format(case_data["case_id"]))
    case_obj = {
        "_id": case_data["case_id"],
        "display_name": case_data.get("display_name", case_data["case_id"]),
    }

    # Check if institute exists in database
    try:
        institute_id = case_data["owner"]
    except KeyError as err:
        raise ConfigError("Case has to have a institute")
    institute_obj = adapter.institute(institute_id)
    if not institute_obj:
        raise IntegrityError("Institute %s not found in database" % institute_id)
    case_obj["owner"] = case_data["owner"]

    # Owner allways has to be part of collaborators
    collaborators = set(case_data.get("collaborators", []))
    collaborators.add(case_data["owner"])
    case_obj["collaborators"] = list(collaborators)

    if case_data.get("assignee"):
        case_obj["assignees"] = [case_data["assignee"]]

    case_obj["smn_tsv"] = case_data.get("smn_tsv")

    # Individuals
    ind_objs = []
    try:
        for individual in case_data.get("individuals", []):
            ind_objs.append(build_individual(individual))
    except Exception as error:
        raise error
    # sort the samples to put the affected individual first
    sorted_inds = sorted(ind_objs, key=lambda ind: -ind["phenotype"])
    case_obj["individuals"] = sorted_inds

    now = datetime.now()
    case_obj["created_at"] = now
    case_obj["updated_at"] = now

    if case_data.get("suspects"):
        case_obj["suspects"] = case_data["suspects"]
    if case_data.get("causatives"):
        case_obj["causatives"] = case_data["causatives"]

    case_obj["synopsis"] = case_data.get("synopsis", "")

    case_obj["status"] = "inactive"
    case_obj["is_research"] = False
    case_obj["research_requested"] = False
    case_obj["rerun_requested"] = False

    case_obj["lims_id"] = case_data.get("lims_id", "")

    analysis_date = case_data.get("analysis_date")
    if analysis_date:
        case_obj["analysis_date"] = analysis_date

    # We store some metadata and references about gene panels in 'panels'
    case_panels = case_data.get("gene_panels", [])
    default_panels = case_data.get("default_panels", [])
    panels = []

    for panel_name in case_panels:
        panel_obj = adapter.gene_panel(panel_name)
        if not panel_obj:
            LOG.warning(
                "Panel %s does not exist in database and will not be saved in case document."
                % panel_name
            )
            continue
        panel = {
            "panel_id": panel_obj["_id"],
            "panel_name": panel_obj["panel_name"],
            "display_name": panel_obj["display_name"],
            "version": panel_obj["version"],
            "updated_at": panel_obj["date"],
            "nr_genes": len(panel_obj["genes"]),
        }
        if panel_name in default_panels:
            panel["is_default"] = True
        else:
            panel["is_default"] = False
        panels.append(panel)

    case_obj["panels"] = panels

    case_obj["dynamic_gene_list"] = []

    # Meta data
    genome_build = case_data.get("genome_build", "37")
    if not genome_build in ["37", "38"]:
        pass

    case_obj["genome_build"] = genome_build

    if case_data.get("rank_model_version"):
        case_obj["rank_model_version"] = str(case_data["rank_model_version"])

    if case_data.get("sv_rank_model_version"):
        case_obj["sv_rank_model_version"] = str(case_data["sv_rank_model_version"])

    if case_data.get("rank_score_threshold"):
        case_obj["rank_score_threshold"] = float(case_data["rank_score_threshold"])

    # Cohort information
    if case_data.get("cohorts"):
        case_obj["cohorts"] = case_data["cohorts"]
        # Check if all case cohorts are registered under the institute
        institute_cohorts = set(institute_obj.get("cohorts", []))
        all_cohorts = institute_cohorts.union(set(case_obj["cohorts"]))
        if len(all_cohorts) > len(institute_cohorts):
            # if not, update institute with new cohorts
            LOG.warning("Updating institute object with new cohort terms")
            adapter.institute_collection.find_one_and_update(
                {"_id": institute_obj["_id"]}, {"$set": {"cohorts": list(all_cohorts)}}
            )

    # phenotype information
    if case_data.get("phenotype_terms"):
        phenotypes = []
        for phenotype in case_data["phenotype_terms"]:
            phenotype_obj = adapter.hpo_term(phenotype)
            if phenotype_obj is None:
                LOG.warning(
                    f"Could not find term with ID '{phenotype}' in HPO collection, skipping phenotype term."
                )
                continue

            phenotypes.append(
                {"phenotype_id": phenotype, "feature": phenotype_obj.get("description")}
            )
        if phenotypes:
            case_obj["phenotype_terms"] = phenotypes

    # phenotype groups
    if case_data.get("phenotype_groups"):
        phenotype_groups = []

        institute_phenotype_groups = set(PHENOTYPE_GROUPS.keys())
        if institute_obj.get("phenotype_groups"):
            institute_phenotype_groups.update(institute_obj.get("phenotype_groups").keys())

        for phenotype in case_data["phenotype_groups"]:
            if phenotype not in institute_phenotype_groups:
                LOG.warning(
                    f"Could not find phenotype group term '{phenotype}' for institute '{institute_id}'. It is not added to case."
                )
                continue

            phenotype_obj = build_phenotype(phenotype, adapter)
            if phenotype_obj:
                phenotype_groups.append(phenotype_obj)
            else:
                LOG.warning(
                    f"Could not find phenotype group term '{phenotype}' in term collection. It is not added to case."
                )
        if phenotype_groups:
            case_obj["phenotype_groups"] = phenotype_groups

    # Files
    case_obj["madeline_info"] = case_data.get("madeline_info")

    set_abspath_case_nested_image_files(case_obj, case_data)

    set_abspath_case_file(case_obj, case_data, "delivery_report")

    for report_key in [report.get("key_name") for report in CUSTOM_CASE_REPORTS.values()]:
        if report_key in case_data:
            set_abspath_case_file(case_obj, case_data, report_key)

    set_abspath_case_nested_files(case_obj, case_data, "vcf_files")

    _populate_pipeline_info(case_obj, case_data)

    case_obj["has_svvariants"] = bool(
        case_obj["vcf_files"].get("vcf_sv") or case_obj["vcf_files"].get("vcf_sv_research")
    )

    case_obj["has_strvariants"] = bool(case_obj["vcf_files"].get("vcf_str"))

    case_obj["has_meivariants"] = bool(case_obj["vcf_files"].get("vcf_mei"))

    case_obj["is_migrated"] = False

    # What experiment is used, alternatives are rare (rare disease) or cancer
    case_obj["track"] = case_data.get("track", "rare")

    case_obj["group"] = case_data.get("group", [])

    return case_obj
