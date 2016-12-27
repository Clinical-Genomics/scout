import logging

from path import path
from ped_parser import FamilyParser

from scout.exceptions import PedigreeError
from scout.constants import PHENOTYPE_MAP, SEX_MAP

logger = logging.getLogger(__name__)


def parse_case(config, ped=None):
    """Parse case information from config or PED files.

    Args:
        config (dict): case config with detailed information
        ped (stream): PED file stream with sample information

    Returns:
        dict: parsed case data
    """
    if ped:
        family_id, samples = parse_ped(ped)
        config['family'] = family_id
        config['samples'] = samples

    individuals = [{
        'individual_id': sample['sample_id'],
        'father': sample.get('father'),
        'mother': sample.get('mother'),
        'display_name': sample.get('sample_name', sample['sample_id']),
        'sex': sample['sex'],
        'phenotype': sample['phenotype'],
        'bam_file': sample.get('bam_path'),
        'analysis_type': sample.get('analysis_type'),
        'capture_kits': ([sample.get('capture_kit')] if 'capture_kit' in sample
                         else []),
    } for sample in config['samples']]

    owner = config['owner']
    family_id = config['family']
    case_data = {
        'owner': owner,
        'collaborators': [owner],
        # Q: can we switch to a dash? we use this across other apps
        'case_id': "{}-{}".format(owner, family_id),
        'display_name': family_id,
        'genome_build': config.get('human_genome_build'),
        'rank_model_version': config.get('rank_model_version'),
        'rank_score_treshold': config.get('rank_score_treshold', 5),
        'analysis_date': config['analysis_date'],
        'individuals': individuals,
        'vcf_files': {
            'vcf_snv': config.get('vcf_snv'),
            'vcf_sv': config.get('vcf_sv'),
            'vcf_snv_research': config.get('vcf_snv_research'),
            'vcf_sv_research': config.get('vcf_sv_research'),
        },
        'default_panels': config.get('default_gene_panels'),
        'gene_panels': config.get('gene_panels'),
    }

    # add the pedigree figure, this is a xml file which is dumped in the db
    if 'madeline' in config:
        mad_path = path(config['madeline'])
        if not mad_path.exists():
            raise ValueError("madeline path not found: {}".format(mad_path))
        with mad_path.open('r') as in_handle:
            case_data['madeline_info'] = in_handle.read()

    return case_data


def parse_ped(ped_stream, family_type='mip'):
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
