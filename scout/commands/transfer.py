# -*- coding: utf-8 -*-
import click


@click.command('transfer', short_help='Transfer cases between institutes')
@click.argument('orig_cust')
@click.argument('case_id')
@click.argument('new_cust')
@click.pass_context
def transfer(ctx, orig_cust, case_id, new_cust):
    """Transfer a case between two customers."""
    case_obj = ctx.obj['adapter'].case(orig_cust, case_id)
    case_obj.owner = new_cust
    case_obj.collaborators.remove(orig_cust)
    if new_cust not in case_obj.collaborators:
        case_obj.collaborators.append(new_cust)
    case_obj.assignee = None
    case_obj.save()
