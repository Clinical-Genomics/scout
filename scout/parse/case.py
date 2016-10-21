import logging

from path import path

from ped_parser import FamilyParser

from scout.exceptions import PedigreeError
from . import parse_gene_panel

logger = logging.getLogger(__name__)

def parse_individual(ind_obj, bam_file='', capture_kits=[]):
    """Return an individual

        Args:
            ind_obj(ped_parser.Individual)
            bam_file(str): Path to bam file
            capture_kits(list(str)): Capture kits used
    """
    individual = {}

    ind_id = ind_obj.individual_id
    individual['individual_id'] = ind_id
    individual['father'] = ind_obj.father
    individual['mother'] = ind_obj.mother
    individual['display_name'] = ind_obj.extra_info.get('display_name', ind_id)

    individual['sex'] = str(ind_obj.sex)

    individual['phenotype'] =int(ind_obj.phenotype)

    # Path to the bam file for IGV:
    individual['bam_file'] = bam_file

    individual['capture_kits'] = capture_kits

    return individual


def parse_case(case_lines, owner, case_type='mip', analysis_type='unknown',
               scout_configs=None):
    """Return a parsed case

        Args:
            case_lines(Iterable): An iterable with ped like case lines
            owner(str): Id of institute that owns the case
            case_type(str): A string that describes the format of the case lines
            analysis_type(str): 'WES', 'WGS', 'unknown' or 'mixed'
            scout_configs(dict): A dictionary with meta information

        Returns:
            case(dict): A dictionary with the relevant information about
                        individuals etc
    """
    case = {}
    scout_configs = scout_configs or {}

    case['owner'] = owner
    case['collaborators'] = [owner]

    logger.info("Setting up a family parser")
    case_parser = FamilyParser(case_lines,family_type=case_type)

    if len(case_parser.families) != 1:
        raise PedigreeError("Only one case per ped file is allowed")

    family_id = list(case_parser.families.keys())[0]
    family = case_parser.families[family_id]

    case['case_id'] = '_'.join([owner, family_id])
    case['display_name'] = family_id

    logger.info("Addind case id {0}".format(case['case_id']))

    case['analysis_type'] = analysis_type.lower()
    case['individuals'] = []

    #Add the individuals
    individuals = []
    for ind_id in family.individuals:
        individual = family.individuals[ind_id]

        config_individual = scout_configs.get('individuals',{}).get(ind_id, {})
        bam_file = config_individual.get('bam_path', '')

        capture_kits = config_individual.get('capture_kit', [])

        individual = parse_individual(
            ind_obj=individual,
            bam_file=bam_file,
            capture_kits=capture_kits
            )

        #Add affected first
        if individual['phenotype'] == 2:
            case['individuals'].append(individual)
        else:
            individuals.append(individual)

    for individual in individuals:
        case['individuals'].append(individual)

    vcf = scout_configs.get('igv_vcf', '')
    case['vcf_file'] = vcf
    logger.debug("Setting vcf file to: {0}".format(vcf))

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
        case['madeline_info'] = None
        logger.info("No madeline file found. Skipping madeline file.")

    case['clinical_panels'] = []
    case['research_panels'] = []

    for panel_id in scout_configs.get('gene_lists', {}):

        logger.info("Found gene panel {0}".format(panel_id))
        panel_info = scout_configs['gene_lists'][panel_id]

        panel = parse_gene_panel(panel_info, institute=owner)

        if panel['type'] == 'clinical':
            logger.info("Add panel {0} to clinical panels".format(panel['id']))
            case['clinical_panels'].append(panel)
        else:
            logger.info("Add panel {0} to research panels".format(panel['id']))
            case['research_panels'].append(panel)

    case['default_panels'] = list(scout_configs.get('default_panels', []))

    return case

