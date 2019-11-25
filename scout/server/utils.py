# -*- coding: utf-8 -*-
import logging
import os
from functools import wraps

from flask import render_template, request, abort, flash
from flask_login import current_user

LOG = logging.getLogger(__name__)

def templated(template=None):
    """Template decorator.
    Ref: http://flask.pocoo.org/docs/patterns/viewdecorators/
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint.replace('.', '/') + '.html'
            context = f(*args, **kwargs)
            if context is None:
                context = {}
            elif not isinstance(context, dict):
                return context
            return render_template(template_name, **context)
        return decorated_function
    return decorator


def public_endpoint(function):
    function.is_public = True
    return function


def institute_and_case(store, institute_id, case_name=None):
    """Fetch insitiute and case objects."""
    institute_obj = store.institute(institute_id)
    if institute_obj is None:
        flash("Can't find institute: {}".format(institute_id), 'warning')
        return abort(404)


    if case_name:
        case_obj = store.case(institute_id=institute_id, display_name=case_name)
        if case_obj is None:
            return abort(404)

    # validate that user has access to the institute

    if not current_user.is_admin:
        if institute_id not in current_user.institutes:
            if not case_name or not any(inst_id in case_obj['collaborators'] for inst_id in
                                        current_user.institutes):
                # you don't have access!!
                flash("You don't have acccess to: {}".format(institute_id),'danger')
                return abort(403)

    # you have access!
    if case_name:
        return institute_obj, case_obj
    else:
        return institute_obj


def user_institutes(store, login_user):
    """Preprocess institute objects."""
    if login_user.is_admin:
        institutes = store.institutes()
    else:
        institutes = [store.institute(inst_id) for inst_id in login_user.institutes]

    return institutes

def variant_case(store, case_obj, variant_obj):
    """Pre-process case for the variant view.

    Adds information about files from case obj to variant

    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(scout.models.Case)
        variant_obj(scout.models.Variant)
    """

    case_append_bam(case_obj)

    try:
        chrom = None
        starts = []
        ends = []
        for gene in variant_obj.get('genes', []):
            chrom = gene['common']['chromosome']
            starts.append(gene['common']['start'])
            ends.append(gene['common']['end'])

        if (crom and starts and ends):
            vcf_path = store.get_region_vcf(
                case_obj,
                chrom=chrom,
                start=min(starts),
                end=max(ends)
            )

            # Create a reduced VCF with variants in the region
            case_obj['region_vcf_file'] = vcf_path
    except (SyntaxError, Exception):
        LOG.warning("skip VCF region for alignment view")

def case_append_bam(case_obj):
    """Deconvolute information about files to case_obj.

    This function prepares the bam files in a certain way so that they are easily accessed in the
    templates.

    Loops over the the individuals and gather bam files, indexes and sample display names in lists

    Args:
        case_obj(scout.models.Case)
    """
    case_obj['bam_files'] = []
    case_obj['mt_bams'] = []
    case_obj['bai_files'] = []
    case_obj['mt_bais'] = []
    case_obj['sample_names'] = []

    bam_files = [
        ('bam_file','bam_files', 'bai_files'),
        ('mt_bam', 'mt_bams', 'mt_bais')
    ]

    for individual in case_obj['individuals']:
        case_obj['sample_names'].append(individual.get('display_name'))
        for bam in bam_files:
            bam_path = individual.get(bam[0])
            if not (bam_path and os.path.exists(bam_path)):
                LOG.debug("%s: no bam file found", individual['individual_id'])
                continue
            case_obj[bam[1]].append(bam_path) # either bam_files or mt_bams
            case_obj[bam[2]].append(find_bai_file(bam_path)) # either bai_files or mt_bais

def find_bai_file(bam_file):
    """Find out BAI file by extension given the BAM file.

    Index files wither ends with filename.bam.bai or filename.bai

    Args:
        bam_file(str): The path to a bam file

    Returns:
        bai_file(str): Path to index file
    """
    bai_file = bam_file.replace('.bam', '.bai')
    if not os.path.exists(bai_file):
        # try the other convention
        bai_file = "{}.bai".format(bam_file)
    return bai_file
