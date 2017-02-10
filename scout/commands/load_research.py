import logging

import click

from scout.load.variant import load_variants, delete_variants

log = logging.getLogger(__name__)


@click.command(short_help='Upload research variants')
@click.option('-c', '--case-id', help='family or case id')
@click.option('-i', '--institute', help='institute id of related cases')
@click.option('-f', '--force', is_flag=True, help='upload without request')
@click.pass_context
def research(context, case_id, institute, force):
    """Upload research variants to cases

        If a case is specified, all variants found for that case will be
        uploaded.

        If no cases are specified then all cases that have 'research_requested'
        will have there research variants uploaded
    """
    log.info("Running scout load research")
    adapter = context.obj['adapter']

    if case_id:
        if not institute:
            # Assume institute-case combo
            institute, case_id = case_id.split('-', 1)
        case_obj = adapter.case(institute_id=institute, case_id=case_id)
        if case_obj is None:
            log.info("No matching case found")
            context.abort()
        else:
            case_objs = [case_obj]
    else:
        # Fetch all cases that have requested research
        case_objs = adapter.cases(research_requested=True)

    default_threshold = 8
    for case_obj in case_objs:
        if force or case_obj.research_requested:
            log.info("Delete variants for case %s", case_obj.case_id)
            delete_variants(adapter=adapter, case_obj=case_obj, variant_type='research')

            log.info("Load research SNV for: %s", case_obj.case_id)
            load_variants(
                adapter=adapter,
                variant_file=case_obj.vcf_files['vcf_snv_research'],
                case_obj=case_obj,
                variant_type='research',
                category='snv',
                rank_threshold=default_threshold,
            )
            if case_obj.vcf_files.get('vcf_sv_research'):
                log.info("Load research SV for: %s", case_obj.case_id)
                load_variants(
                    adapter=adapter,
                    variant_file=case_obj.vcf_files['vcf_sv_research'],
                    case_obj=case_obj,
                    variant_type='research',
                    category='sv',
                    rank_threshold=default_threshold,
                )
            case_obj.is_research = True
            case_obj.research_requested = False
            case_obj.save()
        else:
            log.warn("research not requested, use '--force'")
