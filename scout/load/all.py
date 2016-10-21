import logging

from . import load_case, load_variants, delete_variants

logger = logging.getLogger(__name__)


def load_scout(adapter, config):
    """Load a new case from a Scout config."""
    samples = [{
        'individual_id': sample['id'],
        'father': sample.get('father'),
        'mother': sample.get('mother'),
        'display_name': sample.get('name', sample['id']),
        'sex': sample['sex'],
        'phenotype': sample['phenotype'],
        'bam_file': sample.get('bam_path'),
        'analysis_type': sample.get('analysis_type'),
        'capture_kit': sample.get('capture_kit')
    } for sample in config['samples']]

    case_obj = load_case(
        adapter=adapter,
        family_id=config['family'],
        owner=config['institute'],
        analysis_date=config['analysis_date'],
        default_panels=config['default_panels'],
        genome_build=config['human_genome_build'],
        rank_model_version=config['rank_model_version'],
        vcf=config['vcf'],
        vcf_sv=config['vcf_sv'],
        vcf_research=config['vcf_research'],
        vcf_research_sv=config['vcf_research_sv'],
        samples=samples,
    )

    logger.info("Delete variants for case %s", case_obj.case_id)
    delete_variants(adapter=adapter, case_obj=case_obj)

    logger.info("Load SNV variants for case %s", case_obj.case_id)
    load_variants(adapter=adapter, variant_file=config['vcf'],
                  case_obj=case_obj, variant_type='clinical', category='snv')

    if 'sv_vcf' in config:
        logger.info("Load SV variants for case %s", case_obj.case_id)
        load_variants(adapter=adapter, variant_file=config['vcf_sv'],
                      case_obj=case_obj, variant_type='clinical',
                      category='sv')
        case_obj.has_svvariants = True
        case_obj.save()
