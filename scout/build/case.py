import logging

from datetime import datetime

from . import build_individual

log = logging.getLogger(__name__)


def build_case(case_data):
    """Build a case object that is to be inserted to the database

    Args:
        case_data (dict): A dictionary with the relevant case information

    Returns:
        case_obj (dict): A case object
    
    dict(
        case_id = str, # required=True, unique
        display_name = str, # required
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

        analysis_date = datetime,
        analysis_dates = list, # list of datetimes

        # default_panels specifies which panels that should be shown when
        # the case is opened
        default_panels = list, # list of dictionaries with panel information
        gene_panels = list, # list of _ids to gene panels

        dynamic_gene_list = list, # List of genes

        genome_build = str, # This should be 37 or 38 
        genome_version = float, # What version of the build

        rank_model_version = float,
        rank_score_threshold = int, # default=8

        phenotype_terms = list, # List of dictionaries with phenotype information
        phenotype_groups = list, # List of dictionaries with phenotype information
    
        madeline_info = str, # madeline info is a full xml file

        vcf_files = dict, # A dictionary with vcf files

        diagnosis_phenotypes = list, # List of references to diseases
        diagnosis_genes = list, # List of references to genes

        has_svvariants = bool, # default=False

        is_migrated = bool # default=False
    
    )
    """
    log.info("build case with id: {0}".format(case_data['case_id']))
    case_obj = {case_id: case_data['case_id']}
    case_obj['display_name'] = case_data['display_name']
    case_obj['owner'] = case_data['owner']
    
    case_obj['collaborators'] = case_data.get('collaborators', [case_data['owner']])
    
    case_obj['assignee'] = case_data.get('assignee')

    # Individuals
    ind_objs = []
    try:
        for individual in case_data.get('individuals', []):
            ind_objs.append(build_individual(individual))
    except Exception as error:
        ## TODO add some action here
        raise error
    # sort the samples to put the affected individual first
    sorted_inds = sorted(ind_objs, key=lambda ind: -ind.phenotype)
    case_obj['individuals'] = sorted_inds

    now = datetime.now()
    case_obj['created_at'] = now
    case_obj['updated_at'] = now
    

    case_obj['status'] = 'inactive'
    case_obj['is_research'] = False
    case_obj['research_requested'] = False

    analysis_date = case_data.get('analysis_date')
    case_obj['analysis_date'] = analysis_date
    case_obj['analysis_dates'] = [analysis_date]
    
    case_obj['gene_panels'] = case_data.get('gene_panels', [])
    case_obj['default_panels'] = case_data.get('default_panels', [])
    
    # Meta data
    case_obj['genome_build'] = case_data.get('genome_build')
    case_obj['genome_version'] = case_data.get('genome_version')
    
    if case_data.get('rank_model_version'):
        case_obj['rank_model_version'] = float(case_data['rank_model_version'])

    if case_data.get('rank_score_threshold'):
        case_obj['rank_score_threshold'] = float(case_data['rank_score_threshold'])

    # Files
    case_obj['madeline_info'] = case_data.get('madeline_info')
    case_obj['vcf_files'] = case_data['vcf_files']

    case_obj['has_svvariants'] = False
    if (case_obj.vcf_files.get('vcf_sv') or case_obj.vcf_files.get('vcf_sv_research')):
        case_obj['has_svvariants'] = True
    
    case_obj['is_migrated'] = False
        

    return case_obj
