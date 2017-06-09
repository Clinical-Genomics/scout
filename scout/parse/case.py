import logging
import yaml
import datetime

from path import Path
from ped_parser import FamilyParser

from scout.exceptions import (PedigreeError, ConfigError)
from scout.constants import (PHENOTYPE_MAP, SEX_MAP, REV_SEX_MAP,
                             REV_PHENOTYPE_MAP)

log = logging.getLogger(__name__)

def parse_case_data(config=None, ped=None, owner=None, vcf_snv=None, 
                    vcf_sv=None, vcf_cancer=None):
    """Parse all data necessary for loading a case into scout
    
    This can be done either by providing a VCF file and other information 
    on the command line. Or all the information can be specifed in a config file.
    Please see Scout documentation for further instructions.
    
    Args:
        config(iterable(str)): A yaml formatted config file
        ped(iterable(str)): A ped formatted family file
        owner(str): The institute that owns a case
    
    Returns:
        config_data(dict): Holds all the necessary information for loading 
                           Scout
    """
    config_data = yaml.load(config) if config else {}
    # Default the analysis date to now if not specified in load config
    if not config_data:
        config_data['analysis_date'] = datetime.datetime.now()

    if ped:
        with open(ped, 'r') as f:
            family_id, samples = parse_ped(f)
            config_data['family'] = family_id
            config_data['samples'] = samples

    if 'owner' not in config_data:
        if not owner:
            click.echo()
            raise SyntaxError("Case has no owner")
        else:
            config_data['owner'] = owner

    if 'gene_panels' in config_data:
        log.debug("handle whitespace in gene panel names")
        config_data['gene_panels'] = [panel.strip() for panel in
                                      config_data['gene_panels']]
        config_data['default_gene_panels'] = [panel.strip() for panel in
                                              config_data['default_gene_panels']]
    
    config_data['vcf_snv'] = vcf_snv if vcf_snv else config_data.get('vcf_snv')
    config_data['vcf_sv'] = vcf_sv if vcf_sv else config_data.get('vcf_sv')
    config_data['vcf_cancer'] = vcf_cancer if vcf_cancer else config_data.get('vcf_cancer')
    
    # Set default rank score treshold to 0
    config_data['rank_score_threshold'] = config_data.get('rank_score_threshold', 0)
    
    return config_data


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

    bam_file = sample.get('bam_path')
    if bam_file:
        ind_info['bam_file'] = bam_file

    analysis_type =  sample.get('analysis_type')
    if analysis_type:
        ind_info['analysis_type'] = analysis_type
    
    ind_info['capture_kits'] = ([sample.get('capture_kit')]
                                if 'capture_kit' in sample else [])

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
                raise PedigreeError('father %s does not exist in family'
                                    % father)
        mother = parsed_ind['mother']
        if (mother and mother != '0'):
            if mother not in ind_ids:
                raise PedigreeError('mother %s does not exist in family'
                                    % mother)

    return individuals


def parse_case(config, ped=None):
    """Parse case information from config or PED files.

    Args:
        config (dict): case config with detailed information
        ped (stream): PED file stream with sample information

    Returns:
        dict: parsed case data
    """
    if 'owner' not in config:
        raise ConfigError("A case has to have a owner")
    owner = config['owner']

    if ped:
        with open(ped, 'r') as f:
            family_id, samples = parse_ped(f)
        config['family'] = family_id
        config['samples'] = samples

    if 'family' not in config:
        raise ConfigError("A case has to have a 'family'")
    family_id = config['family']

    individuals = parse_individuals(config['samples'])

    case_data = {
        'owner': owner,
        'collaborators': [owner],
        # Q: can we switch to a dash? we use this across other apps
        'case_id': "{}-{}".format(owner, family_id),
        'display_name': family_id,
        'genome_build': config.get('human_genome_build'),
        'rank_model_version': config.get('rank_model_version'),
        'rank_score_threshold': config.get('rank_score_threshold', 0),
        'analysis_date': config['analysis_date'],
        'individuals': individuals,
        'vcf_files': {
            'vcf_snv': config.get('vcf_snv'),
            'vcf_sv': config.get('vcf_sv'),
            'vcf_cancer': config.get('vcf_cancer'),
            'vcf_snv_research': config.get('vcf_snv_research'),
            'vcf_sv_research': config.get('vcf_sv_research'),
            'vcf_cancer_research': config.get('vcf_cancer_research'),
        },
        'default_panels': config.get('default_gene_panels',[]),
        'gene_panels': config.get('gene_panels',[]),
        'assignee': config.get('assignee'),
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
    """Parse out minimal family information from a PED file."""
    pedigree = FamilyParser(ped_stream, family_type=family_type)

    if len(pedigree.families) != 1:
        raise PedigreeError("Only one case per ped file is allowed")

    family_id = list(pedigree.families.keys())[0]
    family = pedigree.families[family_id]

    samples = [{
        'sample_id': ind_id,
        'father': individual.father,
        'mother': individual.mother,
        'sex': SEX_MAP[individual.sex],
        'phenotype': PHENOTYPE_MAP[int(individual.phenotype)],
    } for ind_id, individual in family.individuals.items()]

    return family_id, samples
