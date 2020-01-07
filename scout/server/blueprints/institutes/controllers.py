# -*- coding: utf-8 -*-
from flask import flash

def institute(store, institute_id):
    """ Process institute data.

    Args:
        store(adapter.MongoAdapter)
        institute_id(str)

    Returns
        data(dict): includes institute obj and specific settings
    """

    institute_obj = store.institute(institute_id)
    users = store.users(institute_id)

    data = {
        'institute' : institute_obj,
        'users': users,
    }
    return data

def update_institute_settings(store, institute_obj, form):
    """ Update institute settings with data collected from institute form

    Args:
        score(adapter.MongoAdapter)
        institute_id(str)
        form(dict)

    Returns:
        updated_institute(dict)

    """
    sanger_recipients = []
    sharing_institutes = []
    phenotype_groups = []
    group_abbreviations = []

    if form.get('sanger_recipients'):
        sanger_recipients = form.get('sanger_recipients').split(', ')

    for inst in form.getlist('institutes'):
        sharing_institutes.append(inst)

    for pheno_group in form.getlist('pheno_groups'):
        phenotype_groups.append(pheno_group.split(' ,')[0])
        group_abbreviations.append(pheno_group[pheno_group.find("( ")+2:pheno_group.find(" )")])

    ## STUFF COLLECTED FROM FORM AND STILL TO INTEGRATE INTO INSTITUTE:
    # snvs_rank_threshold
    # svs_rank_threshold
    # patient cohorts

    updated_institute = store.update_institute(
        internal_id = institute_obj['internal_id'],
        sanger_recipients = sanger_recipients,
        coverage_cutoff = form.get('coverage_cutoff'),
        frequency_cutoff = form.get('frequency_cutoff'),
        display_name = form.get('display_name'),
        phenotype_groups = phenotype_groups,
        group_abbreviations = group_abbreviations,
        add_groups = False,
        sharing_institutes = sharing_institutes
    )
    return updated_institute
