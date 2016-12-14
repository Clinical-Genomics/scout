# -*- coding: utf-8 -*-
import logging

from . import load_case, load_variants, delete_variants
from scout.parse.case import parse_case
from scout.build import build_case
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
        if not adapter.gene_panel(panel_id=panel):
            log.warning("Panel {} does not exist in database".format(panel))
            panels_exist = False
    return panels_exist

def load_scout(adapter, config, ped=None, update=False):
    """Load a new case from a Scout config."""
    log.info("Check that the panels exists")
    if not check_panels(adapter, config.get('gene_panels',[]), config.get('default_panels')):
        raise ConfigError("Some panel(s) does not exist in the database")
    log.debug('parse case data from config and ped')
    case_data = parse_case(config, ped)
    log.debug('build case object from parsed case data')
    case_obj = build_case(case_data)
    log.debug('load case object into database')
    load_case(adapter, case_obj, update=update)

    log.info("Delete variants for case %s", case_obj.case_id)
    delete_variants(adapter=adapter, case_obj=case_obj)

    log.info("Load SNV variants for case %s", case_obj.case_id)
    load_variants(adapter=adapter, variant_file=config['vcf_snv'],
                  case_obj=case_obj, variant_type='clinical', category='snv',
                  rank_treshold=config.get('rank_threshold'))

    if config.get('vcf_sv'):
        log.info("Load SV variants for case %s", case_obj.case_id)
        load_variants(adapter=adapter, variant_file=config['vcf_sv'],
                      case_obj=case_obj, variant_type='clinical',
                      category='sv',
                      rank_treshold=config.get('rank_threshold'))

        case_obj.has_svvariants = True
        case_obj.save()
