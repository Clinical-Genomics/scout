import logging

from path import path

from ped_parser import FamilyParser
from scout.models import (Case, Individual, Institute, User)
from scout.ext.backend.utils import get_gene_panel

logger = logging.getLogger(__name__)

def get_mongo_case(case_lines, owner, case_type='mip', collaborators=set(), 
                   analysis_type='unknown', scout_configs={}):
    """docstring for get_mongo_case"""
    logger.info("Setting up a family parser")
    case_parser = FamilyParser(
                        case_lines,
                        family_type=case_type
                  )
    if len(case_parser.families) != 1:
        raise SyntaxError("Only one case per ped file is allowed")
    
    case_id = list(case_parser.families.keys())[0]
    logger.info("Found case {0}".format(case_id))
    
    logger.info("Creating Case with id {0}".format(
        '_'.join([owner, case_id])))

    case = Case(
        case_id='_'.join([owner, case_id]),
        display_name=case_id,
        owner=owner,
    )
    
    #Check if there are any collaborators
    if collaborators:
        if isinstance(collaborators, list):
            collaborators = set(collaborators)
        else:
            collaborators = set([collaborators])
    #Owner is allways one of the collaborators
    collaborators.add(owner)
    case['collaborators'] = list(collaborators)
    logger.debug("Setting collaborators to: {0}".format(
      ', '.join(collaborators)))
    
    case['analysis_type'] = analysis_type.lower()
    logger.debug("Setting analysis type to: {0}".format(analysis_type))
    
    individuals = []
    # Add the individuals
    for ind_id in case_parser.individuals:
        ped_individual = case_parser.individuals[ind_id]
        individual = Individual(
            individual_id=ind_id,
            father=ped_individual.father,
            mother=ped_individual.mother,
            display_name=ped_individual.extra_info.get(
                                'display_name', ind_id),
            sex=str(ped_individual.sex),
            phenotype=ped_individual.phenotype,
        )
        # Path to the bam file for IGV:
        individual['bam_file'] = scout_configs.get(
            'individuals',{}).get(
                ind_id, {}).get(
                    'bam_path', '')

        individual['capture_kits'] = scout_configs.get(
            'individuals',{}).get(
                ind_id, {}).get(
                    'capture_kit', [])
        #Add affected individuals first
        if ped_individual.affected:
            logger.info("Adding individual {0} to case {1}".format(
                ind_id, case_id))
            case.individuals.append(individual)
        else:
            individuals.append(individual)

    for individual in individuals:
        logger.info("Adding individual {0} to case {1}".format(
                individual.individual_id, case_id))
        case.individuals.append(individual)
    
    # Get the path of vcf from configs
    vcf = scout_configs.get('igv_vcf', '')
    case['vcf_file'] = vcf
    logger.debug("Setting igv vcf file to: {0}".format(vcf))
    
    # Add the genome build information
    genome_build = scout_configs.get('human_genome_build', '')
    case['genome_build'] = genome_build
    logger.debug("Setting genome build to: {0}".format(genome_build))
    
    # Get the genome version
    genome_version = float(scout_configs.get('human_genome_version', '0'))
    case['genome_version'] = genome_version
    logger.debug("Setting genome version to: {0}".format(genome_version))
    
    # Add the rank model version
    rank_model_version = scout_configs.get('rank_model_version', '')
    case['rank_model_version'] = rank_model_version
    logger.debug("Setting rank model version to: {0}".format(
          rank_model_version))
    
    # Check the analysis date
    analysis_date = scout_configs.get('analysis_date')
    if analysis_date:
        case['analysis_date'] = analysis_date
        case['analysis_dates'] = [analysis_date]
        logger.debug("Setting analysis date to: {0}".format(analysis_date))
    else:
        case['analysis_dates'] = []
    
    # Add the pedigree picture, this is a xml file that will be read and
    # saved in the mongo database
    madeline_path = path(scout_configs.get('madeline', '/__menoexist.tXt'))
    if madeline_path.exists():
        logger.debug("Found madeline info")
        with madeline_path.open('r') as handle:
            case['madeline_info'] = handle.read()
            logger.debug("Madeline file was read succesfully")
    else:
        logger.info("No madeline file found. Skipping madeline file.")
    
    # Add the coverage report
    coverage_report_path = path(scout_configs.get('coverage_report', '/__menoexist.tXt'))
    if coverage_report_path.exists():
        logger.debug("Found a coverage report")
        with coverage_report_path.open('rb') as handle:
            case['coverage_report'] = handle.read()
            logger.debug("Coverage was read succesfully")
    else:
        logger.info("No coverage report found. Skipping coverage report.")
    
    clinical_panels = []
    research_panels = []
    
    for gene_list in scout_configs.get('gene_lists', {}):
        logger.info("Found gene list {0}".format(gene_list))
        panel_info = scout_configs['gene_lists'][gene_list]

        panel_path = panel_info.get('file')
        panel_type = panel_info.get('type', 'clinical')
        panel_date = panel_info.get('date')
        panel_version = float(panel_info.get('version', '0'))
        panel_id = panel_info.get('name')
        display_name = panel_info.get('full_name', panel_id)

        # lookup among existing gene panels
        panel = self.gene_panel(panel_id, panel_version)
        if panel is None:
            panel = get_gene_panel(list_file_name=panel_path,
                                   institute_id=owner,
                                   panel_id=panel_id,
                                   panel_version=panel_version,
                                   display_name=display_name,
                                   panel_date=panel_date)

        if panel_type == 'clinical':
            logger.info("Adding {0} to clinical gene lists".format(
                        panel.panel_name))
            clinical_panels.append(panel)
        else:
            logger.info("Adding {0} to research gene lists".format(
                        panel.panel_name))
            research_panels.append(panel)

    case['clinical_panels'] = clinical_panels
    case['research_panels'] = research_panels

    default_panels = scout_configs.get('default_panels', [])
    logger.info("Adding {0} as default panels to case {1}".format(
        ', '.join(default_panels), case_id))
    case['default_panels'] = list(default_panels)
    
    return case
    
    