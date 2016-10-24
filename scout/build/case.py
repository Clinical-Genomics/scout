import logging

from scout.models import Case

from . import build_individual

log = logging.getLogger(__name__)


def build_case(case_data):
    """Build a mongoengine Case object

    Args:
        case_data (dict): A dictionary with the relevant case information

    Returns:
        case_obj (Case): A mongoengine case object
    """
    log.info("build case with id: {0}".format(case_data['case_id']))
    case_obj = Case(
        case_id=case_data['case_id'],
        display_name=case_data['display_name'],
        owner=case_data['owner'],
    )
    case_obj.collaborators = case_data.get('collaborators')
    case_obj.analysis_type = case_data.get('analysis_type')

    # Individuals
    ind_objs = []
    for individual in case_data.get('individuals', []):
        ind_objs.append(build_individual(individual))
    # sort the samples to put the affected individual first
    sorted_inds = sorted(ind_objs, key=lambda ind: -ind.phenotype)
    case_obj.individuals = sorted_inds

    # Meta data
    case_obj.genome_build = case_data.get('genome_build')
    case_obj.rank_model_version = str(case_data.get('rank_model_version'))

    analysis_date = case_data.get('analysis_date')
    if analysis_date:
        case_obj.analysis_date = analysis_date.date().isoformat()
        case_obj.analysis_dates.append(case_obj.analysis_date)

    # Files
    case_obj.madeline_info = case_data.get('madeline_info')
    return case_obj
