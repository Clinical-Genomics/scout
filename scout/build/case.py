import logging
from datetime import datetime

from scout.constants import CUSTOM_CASE_REPORTS
from scout.exceptions import ConfigError, IntegrityError
from . import build_individual

LOG = logging.getLogger(__name__)


def build_phenotype(phenotype_id, adapter):
    """Build a small phenotype object

        Build a dictionary with phenotype_id and description

    Args:
        phenotype_id (str): The phenotype id
        adapter (scout.adapter.MongoAdapter)

    Returns:
        phenotype_obj (dict):

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
    return phenotype


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
    except KeyError as _err:
        raise ConfigError("Case has to have a institute")
    institute_obj = adapter.institute(institute_id)
    if not institute_obj:
        raise IntegrityError("Institute %s not found in database" % institute_id)

    case_obj["owner"] = case_data["owner"]
    case_obj["smn_tsv"] = case_data.get("smn_tsv")
    case_obj["collaborators"] = get_collaborators(case_data)
    case_obj["individuals"] = get_individuals(case_data)
    case_obj["synopsis"] = case_data.get("synopsis", "")

    set_analysis_date(case_obj, case_data)
    set_assignee(case_obj, case_data)
    set_causatives(case_obj, case_data)
    set_suspects(case_obj, case_data)
    set_timestamps(case_obj)

    case_obj["is_research"] = False
    case_obj["lims_id"] = case_data.get("lims_id", "")
    case_obj["rerun_requested"] = False
    case_obj["research_requested"] = False
    case_obj["status"] = "inactive"
    case_obj["panels"] = get_panels(case_data, adapter)
    case_obj["dynamic_gene_list"] = []

    # Meta data
    set_genome_build(case_obj, case_data)

    if case_data.get("rank_model_version"):
        case_obj["rank_model_version"] = str(case_data["rank_model_version"])

    if case_data.get("sv_rank_model_version"):
        case_obj["sv_rank_model_version"] = str(case_data["sv_rank_model_version"])

    if case_data.get("rank_score_threshold"):
        case_obj["rank_score_threshold"] = float(case_data["rank_score_threshold"])

    set_cohort(case_obj, case_data, institute_obj, adapter)
    set_phenotype_terms(case_obj, case_data, adapter)
    set_phenotype_groups(case_obj, case_data, adapter)

    # Files
    case_obj["madeline_info"] = case_data.get("madeline_info")

    case_obj["custom_images"] = case_data.get("custom_images")
    set_custom_report(case_obj, case_data)
    case_obj["vcf_files"] = case_data.get("vcf_files", {})
    case_obj["delivery_report"] = case_data.get("delivery_report")

    case_obj["has_svvariants"] = False
    if case_obj["vcf_files"].get("vcf_sv") or case_obj["vcf_files"].get(
        "vcf_sv_research"
    ):
        case_obj["has_svvariants"] = True

    case_obj["has_strvariants"] = False
    if case_obj["vcf_files"].get("vcf_str"):
        case_obj["has_strvariants"] = True

    case_obj["is_migrated"] = False

    # What experiment is used, alternatives are rare (rare disease) or cancer
    case_obj["track"] = case_data.get("track", "rare")
    case_obj["group"] = case_data.get("group", [])

    return case_obj


def get_collaborators(case_data):
    """Return a list of collaborators with owner appended.  Owner must
    be part of collaborators"""
    collaborators = set(case_data.get("collaborators", []))
    collaborators.add(case_data["owner"])
    return list(collaborators)


def get_individuals(case_data):
    """Return samples with with affected individual first"""
    ind_objs = []
    for individual in case_data.get("individuals", []):
        ind_objs.append(build_individual(individual))
    return sorted(ind_objs, key=lambda ind: -ind["phenotype"])


def get_panels(case_data, adapter):
    """Return list of gene panels from case_data

    Args:
        case_data(Dict)
        adapter(scout.adapter.MongoAdapter)

    Returns:
        List(panel{})

    """
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
            "display_name": panel_obj["display_name"],
            "is_default": False,
            "nr_genes": len(panel_obj["genes"]),
            "panel_id": panel_obj["_id"],
            "panel_name": panel_obj["panel_name"],
            "updated_at": panel_obj["date"],
            "version": panel_obj["version"],
        }
        if panel_name in default_panels:
            panel["is_default"] = True
        panels.append(panel)

    return panels


def set_timestamps(case_obj):
    """Set case_obj's internal creation and update timestamps to now"""
    now = datetime.now()
    case_obj["created_at"] = now
    case_obj["updated_at"] = now


def set_suspects(case_obj, case_data):
    if case_data.get("suspects"):
        case_obj["suspects"] = case_data["suspects"]


def set_causatives(case_obj, case_data):
    if case_data.get("causatives"):
        case_obj["causatives"] = case_data["causatives"]


def set_assignee(case_obj, case_data):
    if case_data.get("assignee"):
        case_obj["assignees"] = [case_data["assignee"]]


def set_analysis_date(case_obj, case_data):
    if case_data.get("analysis_date"):
        case_obj["analysis_date"] = case_data["analysis_date"]


def set_genome_build(case_obj, case_data):
    genome_build = case_data.get("genome_build", 37)
    if not genome_build in [37, 38]:
        raise ValueError(f"Genome build {genome_build} not supported")
    case_obj["genome_build"] = genome_build


def set_cohort(case_obj, case_data, institute_obj, adapter):
    """Set cohort information to case_obj. Also check if all case cohorts are
    registered under the institute db. If not update the database.

    Args:
        case_obj(Dict)
        case_data(Dict)
        institute_obj()
        adapter(scout.adapter.MongoAdapter)

    Returns:
        None
    """
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


def set_phenotype_terms(case_obj, case_data, adapter):
    """Update case_obj with phenotype_terms from phenotypes found in case_data"""
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


def set_phenotype_groups(case_obj, case_data, adapter):
    """Set phenotype groups"""
    if case_data.get("phenotype_groups"):
        phenotype_groups = []
        for phenotype in case_data["phenotype_groups"]:
            phenotype_obj = build_phenotype(phenotype, adapter)
            if phenotype_obj:
                phenotype_groups.append(phenotype_obj)
        if phenotype_groups:
            case_obj["phenotype_groups"] = phenotype_groups


def set_custom_report(case_obj, case_data):
    """Set custom_report of case_obj if matching macro is found.
    For example: multiqc, cnv_report, etc"""
    for custom_report in CUSTOM_CASE_REPORTS:
        if custom_report in case_data:
            case_obj[custom_report] = case_data.get(custom_report)
