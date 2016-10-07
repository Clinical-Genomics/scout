from scout.models import (Case)

from . import (build_individual, build_panel)

def build_case(case):
    """Build a mongoengine Case object
    
        Args:
            case(dict): A dictionary with the relevant case information
    
        Returns:
            case_obj(Case): A mongoengine case object
    """
    case_obj = Case(
        case_id=case['case_id'],
        display_name=case['display_name'],
        owner=case['owner'],
    )
    case_obj.collaborators = case.get('collaborators')
    case_obj.analysis_type = case.get('analysis_type')
    case_obj.vcf_file = case.get('vcf_file')
    
    # Individuals
    individual_objs = []
    for individual in case.get('individuals',[]):
        individual_objs.append(build_individual(individual))
    case_obj.individuals = individual_objs
        
    # Meta data
    case_obj.genome_build = case.get('genome_build')
    case_obj.genome_version = case.get('genome_version')
    case_obj.rank_model_version = case.get('rank_model_version')
    
    case_obj.analysis_date = case.get('analysis_date')
    case_obj.analysis_dates = case.get('analysis_dates')
    
    case_obj.analysis_type = case.get['analysis_type']
    
    # Files
    case_obj.madeline_info = case.get('madeline_info')
    case_obj.coverage_report = case.get('coverage_report')
    
    case_obj.vcf_file = case.get('vcf_file')
    
    # Gene Panels
    case_obj.default_panels = case.get('default_panels')
    clinical_panels = []
    research_panels = []
    
    for panel in case['clinical_panels']:
        clinical_panels.append(build_panel(panel))
    case_obj.clinical_panels = clinical_panels
    
    for panel in case['research_panels']:
        research_panels.append(build_panel(panel))
    case_obj.research_panels = research_panels
    
    return case_obj