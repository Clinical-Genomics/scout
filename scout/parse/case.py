import copy
import logging
import datetime

from pprint import pprint as pp

from path import Path
from ped_parser import FamilyParser

from scout.exceptions import (PedigreeError, ConfigError)
from scout.constants import (PHENOTYPE_MAP, SEX_MAP, REV_SEX_MAP,
                             REV_PHENOTYPE_MAP)

from scout.parse.peddy import (parse_peddy_ped, parse_peddy_ped_check,
                               parse_peddy_sex_check)

log = logging.getLogger(__name__)


def parse_case_data(config=None, ped=None, owner=None, vcf_snv=None,
                    vcf_sv=None, vcf_cancer=None, vcf_str=None, peddy_ped=None,
                    peddy_sex=None, peddy_check=None, delivery_report=None, multiqc=None):
    """Parse all data necessary for loading a case into scout

    This can be done either by providing a VCF file and other information
    on the command line. Or all the information can be specified in a config file.
    Please see Scout documentation for further instructions.

    Args:
        config(dict): A yaml formatted config file
        ped(iterable(str)): A ped formatted family file
        owner(str): The institute that owns a case
        vcf_snv(str): Path to a vcf file
        vcf_str(str): Path to a VCF file
        vcf_sv(str): Path to a vcf file
        vcf_cancer(str): Path to a vcf file
        peddy_ped(str): Path to a peddy ped
        multiqc(str): Path to dir with multiqc information

    Returns:
        config_data(dict): Holds all the necessary information for loading
                           Scout
    """
    config_data = copy.deepcopy(config) or {}
    # Default the analysis date to now if not specified in load config
    if 'analysis_date' not in config_data:
        config_data['analysis_date'] = datetime.datetime.now()

    # If the family information is in a ped file we nned to parse that
    if ped:
        family_id, samples = parse_ped(ped)
        config_data['family'] = family_id
        config_data['samples'] = samples

    # Each case has to have a owner. If not provided in config file it needs to be given as a
    # argument
    if 'owner' not in config_data:
        if not owner:
            raise SyntaxError("Case has no owner")
        else:
            config_data['owner'] = owner

    if 'gene_panels' in config_data:
        # handle whitespace in gene panel names
        config_data['gene_panels'] = [panel.strip() for panel in
                                      config_data['gene_panels']]
        config_data['default_gene_panels'] = [panel.strip() for panel in
                                              config_data['default_gene_panels']]

    ##################### Add information from peddy if existing #####################
    config_data['peddy_ped'] = peddy_ped or config_data.get('peddy_ped')
    config_data['peddy_sex_check'] = peddy_sex or config_data.get('peddy_sex')
    config_data['peddy_ped_check'] = peddy_check or config_data.get('peddy_check')

    # This will add information from peddy to the individuals
    add_peddy_information(config_data)

    ##################### Add multiqc information #####################
    config_data['multiqc'] = multiqc or config_data.get('multiqc')

    config_data['vcf_snv'] = vcf_snv if vcf_snv else config_data.get('vcf_snv')
    config_data['vcf_sv'] = vcf_sv if vcf_sv else config_data.get('vcf_sv')
    config_data['vcf_str'] = vcf_str if vcf_str else config_data.get('vcf_str')
    log.debug("Config vcf_str set to {0}".format(config_data['vcf_str']))

    config_data['vcf_cancer'] = vcf_cancer if vcf_cancer else config_data.get('vcf_cancer')

    config_data['delivery_report'] = delivery_report if delivery_report else config_data.get('delivery_report')

    config_data['rank_model_version'] = config_data.get('rank_model_version')
    config_data['rank_score_threshold'] = config_data.get('rank_score_threshold', 0)

    return config_data


def add_peddy_information(config_data):
    """Add information from peddy outfiles to the individuals"""
    ped_info = {}
    ped_check = {}
    sex_check = {}
    relations = []

    if config_data.get('peddy_ped'):
        file_handle = open(config_data['peddy_ped'], 'r')
        for ind_info in parse_peddy_ped(file_handle):
            ped_info[ind_info['sample_id']] = ind_info

    if config_data.get('peddy_ped_check'):
        file_handle = open(config_data['peddy_ped_check'], 'r')
        for pair_info in parse_peddy_ped_check(file_handle):
            ped_check[(pair_info['sample_a'], pair_info['sample_b'])] = pair_info

    if config_data.get('peddy_sex_check'):
        file_handle = open(config_data['peddy_sex_check'], 'r')
        for ind_info in parse_peddy_sex_check(file_handle):
            sex_check[ind_info['sample_id']] = ind_info

    analysis_inds = {}
    for ind in config_data['samples']:
        ind_id = ind['sample_id']
        analysis_inds[ind_id] = ind

    for ind_id in analysis_inds:
        ind = analysis_inds[ind_id]
        # Check if peddy has inferred the ancestry
        if ind_id in ped_info:
            ind['predicted_ancestry'] = ped_info[ind_id].get('ancestry-prediction', 'UNKNOWN')
        # Check if peddy has inferred the sex
        if ind_id in sex_check:
            if sex_check[ind_id]['error']:
                ind['confirmed_sex'] = False
            else:
                ind['confirmed_sex'] = True

        # Check if peddy har confirmed parental relations
        for parent in ['mother', 'father']:
            # If we are looking at individual with parents
            if ind[parent] != '0':
                # Check if the child/parent pair is in peddy data
                for pair in ped_check:
                    if (ind_id in pair and ind[parent] in pair):
                        # If there is a parent error we mark that
                        if ped_check[pair]['parent_error']:
                            analysis_inds[ind[parent]]['confirmed_parent'] = False
                        else:
                            # Else if parent confirmation has not been done
                            if 'confirmed_parent' not in analysis_inds[ind[parent]]:
                                # Set confirmatio to True
                                analysis_inds[ind[parent]]['confirmed_parent'] = True

def parse_individual(sample):
    """Parse individual information

        Args:
            sample (dict)

        Returns:
            {
                'individual_id': str,
                'father': str,
                'mother': str,
                'display_name': str,
                'sex': str,
                'phenotype': str,
                'bam_file': str,
                'vcf2cytosure': str,
                'analysis_type': str,
                'capture_kits': list(str),
            }

    """
    ind_info = {}
    if 'sample_id' not in sample:
        raise PedigreeError("One sample is missing 'sample_id'")
    sample_id = sample['sample_id']
    # Check the sex
    if 'sex' not in sample:
        raise PedigreeError("Sample %s is missing 'sex'" % sample_id)
    sex = sample['sex']
    if sex not in REV_SEX_MAP:
        log.warning("'sex' is only allowed to have values from {}"
                    .format(', '.join(list(REV_SEX_MAP.keys()))))
        raise PedigreeError("Individual %s has wrong formated sex" % sample_id)

    # Check the phenotype
    if 'phenotype' not in sample:
        raise PedigreeError("Sample %s is missing 'phenotype'"
                            % sample_id)
    phenotype = sample['phenotype']
    if phenotype not in REV_PHENOTYPE_MAP:
        log.warning("'phenotype' is only allowed to have values from {}"
                    .format(', '.join(list(REV_PHENOTYPE_MAP.keys()))))
        raise PedigreeError("Individual %s has wrong formated phenotype" % sample_id)

    ind_info['individual_id'] = sample_id
    ind_info['display_name'] = sample.get('sample_name', sample['sample_id'])

    ind_info['sex'] = sex
    ind_info['phenotype'] = phenotype

    ind_info['father'] = sample.get('father')
    ind_info['mother'] = sample.get('mother')

    ind_info['confirmed_parent'] = sample.get('confirmed_parent')
    ind_info['confirmed_sex'] = sample.get('confirmed_sex')
    ind_info['predicted_ancestry'] = sample.get('predicted_ancestry')

    bam_file = sample.get('bam_path')
    if bam_file:
        ind_info['bam_file'] = bam_file

    mt_bam = sample.get('mt_bam')
    if mt_bam:
        ind_info['mt_bam'] = mt_bam

    analysis_type = sample.get('analysis_type')
    if analysis_type:
        ind_info['analysis_type'] = analysis_type

    ind_info['capture_kits'] = ([sample.get('capture_kit')]
                                if 'capture_kit' in sample else [])

    vcf2cytosure = sample.get('vcf2cytosure')
    if vcf2cytosure:
        ind_info['vcf2cytosure'] = vcf2cytosure

    return ind_info


def parse_individuals(samples):
    """Parse the individual information

        Reformat sample information to proper individuals

        Args:
            samples(list(dict))

        Returns:
            individuals(list(dict))
    """
    individuals = []
    if len(samples) == 0:
        raise PedigreeError("No samples could be found")

    ind_ids = set()
    for sample_info in samples:
        parsed_ind = parse_individual(sample_info)
        individuals.append(parsed_ind)
        ind_ids.add(parsed_ind['individual_id'])

    # Check if relations are correct
    for parsed_ind in individuals:
        father = parsed_ind['father']
        if (father and father != '0'):
            if father not in ind_ids:
                raise PedigreeError('father %s does not exist in family' % father)
        mother = parsed_ind['mother']
        if (mother and mother != '0'):
            if mother not in ind_ids:
                raise PedigreeError('mother %s does not exist in family' % mother)

    return individuals


def parse_case(config):
    """Parse case information from config or PED files.

    Args:
        config (dict): case config with detailed information

    Returns:
        dict: parsed case data
    """
    if 'owner' not in config:
        raise ConfigError("A case has to have a owner")

    if 'family' not in config:
        raise ConfigError("A case has to have a 'family'")

    individuals = parse_individuals(config['samples'])
    case_data = {
        'owner': config['owner'],
        'collaborators': [config['owner']],
        'case_id': config['family'],
        'display_name': config.get('family_name', config['family']),
        'genome_build': config.get('human_genome_build'),
        'rank_model_version': config.get('rank_model_version'),
        'rank_score_threshold': config.get('rank_score_threshold', 0),
        'analysis_date': config['analysis_date'],
        'individuals': individuals,
        'vcf_files': {
            'vcf_snv': config.get('vcf_snv'),
            'vcf_sv': config.get('vcf_sv'),
            'vcf_str': config.get('vcf_str'),
            'vcf_cancer': config.get('vcf_cancer'),
            'vcf_snv_research': config.get('vcf_snv_research'),
            'vcf_sv_research': config.get('vcf_sv_research'),
            'vcf_cancer_research': config.get('vcf_cancer_research'),
        },
        'default_panels': config.get('default_gene_panels', []),
        'gene_panels': config.get('gene_panels', []),
        'assignee': config.get('assignee'),
        'peddy_ped': config.get('peddy_ped'),
        'peddy_sex': config.get('peddy_sex'),
        'peddy_check': config.get('peddy_check'),
        'delivery_report': config.get('delivery_report'),
        'multiqc': config.get('multiqc'),
    }

    # add the pedigree figure, this is a xml file which is dumped in the db
    if 'madeline' in config:
        mad_path = Path(config['madeline'])
        if not mad_path.exists():
            raise ValueError("madeline path not found: {}".format(mad_path))
        with mad_path.open('r') as in_handle:
            case_data['madeline_info'] = in_handle.read()

    return case_data


def parse_ped(ped_stream, family_type='ped'):
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

    samples = [{
        'sample_id': ind_id,
        'father': individual.father,
        'mother': individual.mother,
        # Convert sex to human readable
        'sex': SEX_MAP[individual.sex],
        'phenotype': PHENOTYPE_MAP[int(individual.phenotype)],
    } for ind_id, individual in family.individuals.items()]

    return family_id, samples
