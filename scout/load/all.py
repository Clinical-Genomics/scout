# -*- coding: utf-8 -*-
import logging

from scout.exceptions.config import ConfigError

log = logging.getLogger(__name__)


def check_panels(adapter, panels, default_panels=None):
    """Make sure that the gene panels exist in the database
        Also check if the default panels are defined in gene panels

        Args:
            adapter(MongoAdapter)
            panels(list(str)): A list with panel names

        Returns:
            panels_exists(bool)
    """
    default_panels = default_panels or []
    panels_exist = True
    for panel in default_panels:
        if panel not in panels:
            log.warning("Default panels have to be defined in panels")
            panels_exist = False
    for panel in panels:
        if not adapter.gene_panel(panel):
            log.warning("Panel {} does not exist in database".format(panel))
            panels_exist = False
    return panels_exist


def load_region(adapter, case_id, hgnc_id=None, chrom=None, start=None, end=None):
    """Load all variants in a region defined by a HGNC id

    Args:
        adapter (MongoAdapter)
        case_id (str): Case id
        hgnc_id (int): If all variants from a gene should be uploaded
        chrom (str): If variants from coordinates should be uploaded
        start (int): Start position for region
        end (int): Stop position for region
    """
    if hgnc_id:
        gene_obj = adapter.hgnc_gene(hgnc_id)
        if not gene_obj:
            ValueError("Gene {} does not exist in database".format(hgnc_id))
        chrom = gene_obj['chromosome']
        start = gene_obj['start']
        end = gene_obj['end']

    case_obj = adapter.case(case_id=case_id)
    if not case_obj:
        raise ValueError("Case {} does not exist in database".format(case_id))

    log.info("Load clinical SNV variants for case: {0} region: chr {1}, start"
             " {2}, end {3}".format(case_obj['_id'], chrom, start, end))

    adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                          category='snv', chrom=chrom, start=start, end=end)

    vcf_sv_file = case_obj['vcf_files'].get('vcf_sv')
    if vcf_sv_file:
        log.info("Load clinical SV variants for case: {0} region: chr {1}, "
                 "start {2}, end {3}".format(case_obj['_id'], chrom, start, end))
        adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                              category='sv', chrom=chrom, start=start, end=end)

    vcf_str_file = case_obj['vcf_files'].get('vcf_str')
    if vcf_str_file: 
        log.info("Load clinical STR variants for case: {0} region: chr {1}, "
                 "start {2}, end {3}".format(case_obj['_id'], chrom, start, end))
        adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                              category='str', chrom=chrom, start=start, end=end)

    if case_obj['is_research']:
        log.info("Load research SNV variants for case: {0} region: chr {1}, "
                 "start {2}, end {3}".format(case_obj['_id'], chrom, start, end))
        adapter.load_variants(case_obj=case_obj, variant_type='research',
                              category='snv', chrom=chrom, start=start, end=end)

        vcf_sv_research = case_obj['vcf_files'].get('vcf_sv_research')
        if vcf_sv_research:
            log.info("Load research SV variants for case: {0} region: chr {1},"
                     " start {2}, end {3}".format(case_obj['_id'], chrom, start, end))
            adapter.load_variants(case_obj=case_obj, variant_type='research',
                                  category='sv', chrom=chrom, start=start, end=end)


def load_scout(adapter, config, ped=None, update=False):
    """Load a new case from a Scout config.

        Args:
            adapter(MongoAdapter)
            config(dict): loading info
            ped(Iterable(str)): Pedigree ingformation
            update(bool): If existing case should be updated

    """
    log.info("Check that the panels exists")
    if not check_panels(adapter, config.get('gene_panels', []),
                        config.get('default_gene_panels')):
        raise ConfigError("Some panel(s) does not exist in the database")
    case_obj = adapter.load_case(config, update=update)
    return case_obj
