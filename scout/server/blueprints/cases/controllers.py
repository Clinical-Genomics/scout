# -*- coding: utf-8 -*-
import itertools
import datetime

from flask import url_for
from flask_mail import Message
import query_phenomizer

from scout.constants import (CASE_STATUSES, PHENOTYPE_GROUPS, COHORT_TAGS, SEX_MAP, PHENOTYPE_MAP, VERBS_MAP)
from scout.constants.variant_tags import MANUAL_RANK_OPTIONS, DISMISS_VARIANT_OPTIONS, GENETIC_MODELS
from scout.server.utils import institute_and_case
from scout.parse.clinvar import clinvar_submission_header, clinvar_submission_lines
from scout.server.blueprints.variants.controllers import variants_filter_by_field

STATUS_MAP = {'solved': 'bg-success', 'archived': 'bg-warning'}


def cases(store, case_query, limit=100):
    """Preprocess case objects."""

    case_groups = {status: [] for status in CASE_STATUSES}
    for case_obj in case_query.limit(limit):
        analysis_types = set(ind['analysis_type'] for ind in case_obj['individuals'])

        case_obj['analysis_types'] = list(analysis_types)
        case_obj['assignees'] = [store.user(user_email) for user_email in
                                 case_obj.get('assignees', [])]
        case_groups[case_obj['status']].append(case_obj)
        case_obj['is_rerun'] = len(case_obj.get('analyses', [])) > 0
        case_obj['clinvar_variants'] = store.case_to_clinVars(case_obj['_id'])
    data = {
        'cases': [(status, case_groups[status]) for status in CASE_STATUSES],
        'found_cases': case_query.count(),
        'limit': limit,
    }
    return data


def case(store, institute_obj, case_obj):
    """Preprocess a single case."""
    case_obj['individual_ids'] = []
    for individual in case_obj['individuals']:
        try:
            sex = int(individual.get('sex', 0))
        except ValueError as err:
            sex = 0
        individual['sex_human'] = SEX_MAP[sex]
        individual['phenotype_human'] = PHENOTYPE_MAP.get(individual['phenotype'])
        case_obj['individual_ids'].append(individual['individual_id'])

    case_obj['assignees'] = [store.user(user_email) for user_email in
                             case_obj.get('assignees', [])]
    suspects = [store.variant(variant_id) or variant_id for variant_id in
                case_obj.get('suspects', [])]
    causatives = [store.variant(variant_id) or variant_id for variant_id in
                  case_obj.get('causatives', [])]

    distinct_genes = set()
    case_obj['panel_names'] = []
    for panel_info in case_obj.get('panels', []):
        if panel_info.get('is_default'):
            panel_obj = store.gene_panel(panel_info['panel_name'], version=panel_info.get('version'))
            distinct_genes.update([gene['hgnc_id'] for gene in panel_obj.get('genes', [])])
            full_name = "{} ({})".format(panel_obj['display_name'], panel_obj['version'])
            case_obj['panel_names'].append(full_name)
    case_obj['default_genes'] = list(distinct_genes)

    for hpo_term in itertools.chain(case_obj.get('phenotype_groups', []),
                                    case_obj.get('phenotype_terms', [])):
        hpo_term['hpo_link'] = ("http://compbio.charite.de/hpoweb/showterm?id={}"
                                .format(hpo_term['phenotype_id']))

    # other collaborators than the owner of the case
    o_collaborators = [store.institute(collab_id) for collab_id in case_obj['collaborators'] if
                       collab_id != case_obj['owner']]
    case_obj['o_collaborators'] = [(collab_obj['_id'], collab_obj['display_name']) for
                                   collab_obj in o_collaborators]

    irrelevant_ids = ('cust000', institute_obj['_id'])
    collab_ids = [(collab['_id'], collab['display_name']) for collab in store.institutes() if
                  (collab['_id'] not in irrelevant_ids) and
                  (collab['_id'] not in case_obj['collaborators'])]

    events = list(store.events(institute_obj, case=case_obj))
    for event in events:
        event['verb'] = VERBS_MAP[event['verb']]

    case_obj['clinvar_variants'] = store.case_to_clinVars(case_obj['display_name'])

    # Phenotype groups can be specific for an institute, there are some default groups
    pheno_groups = institute_obj.get('phenotype_groups') or PHENOTYPE_GROUPS

    data = {
        'status_class': STATUS_MAP.get(case_obj['status']),
        'other_causatives': store.check_causatives(case_obj=case_obj),
        'comments': store.events(institute_obj, case=case_obj, comments=True),
        'hpo_groups': pheno_groups,
        'events': events,
        'suspects': suspects,
        'causatives': causatives,
        'collaborators': collab_ids,
        'cohort_tags': COHORT_TAGS,
    }
    return data


def case_report_content(store, institute_obj, case_obj):
    """Gather contents to be visualized in a case report"""

    data = case(store, institute_obj, case_obj)

    data['manual_rank_options'] = MANUAL_RANK_OPTIONS
    data['dismissed_options'] = DISMISS_VARIANT_OPTIONS
    data['genetic_models'] = dict(GENETIC_MODELS)
    data['report_created_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # We collect all causatives and suspected variants
    for var_type in ['causatives', 'suspects']:
        # data[var_type] can include strings so we need to be careful
        # remove any element which is not a dictionary
        raw = [var for var in data[var_type] if isinstance(var, dict)]
        # get detailed info for the causatives and add to data
        var_type += '_detailed'
        data[var_type] = variants_filter_by_field(store, raw, '_id', case_obj, institute_obj)

    ## get variants for this case that are either classified, commented, tagged or dismissed.
    evaluated_variants = store.evaluated_variants(case_id=case_obj['_id'])

    # get complete info for the acmg classified variants
    data['classified_detailed'] = variants_filter_by_field(store, evaluated_variants,
                                                           'acmg_classification', case_obj, institute_obj)

    # get complete info for tagged variants
    data['tagged_detailed'] = variants_filter_by_field(store, evaluated_variants,
                                                       'manual_rank', case_obj, institute_obj)

    # get complete info for dismissed variants
    data['dismissed_detailed'] = variants_filter_by_field(store, evaluated_variants,
                                                        'dismiss_variant', case_obj, institute_obj)

    data['commented_detailed'] = variants_filter_by_field(store, evaluated_variants,
                                                        'is_commented', case_obj, institute_obj)

    return data


def clinvar_submissions(store, user_id, institute_id):
    """Get all Clinvar submissions for a user and an institute"""
    submissions = list(store.clinvar_submissions(user_id, institute_id))
    return submissions


def clinvar_header(submission_objs, csv_type):
    """ Call clinvar parser to extract required fields to include in csv header from clinvar submission objects"""

    clinvar_header_obj = clinvar_submission_header(submission_objs, csv_type)
    return clinvar_header_obj


def clinvar_lines(clinvar_objects, clinvar_header):
    """ Call clinvar parser to extract required lines to include in csv file from clinvar submission objects and header"""

    clinvar_lines = clinvar_submission_lines(clinvar_objects, clinvar_header)
    return clinvar_lines



def update_synopsis(store, institute_obj, case_obj, user_obj, new_synopsis):
    """Update synopsis."""
    # create event only if synopsis was actually changed
    if new_synopsis and case_obj['synopsis'] != new_synopsis:
        link = url_for('cases.case', institute_id=institute_obj['_id'],
                       case_name=case_obj['display_name'])
        store.update_synopsis(institute_obj, case_obj, user_obj, link,
                              content=new_synopsis)


def hpo_diseases(username, password, hpo_ids, p_value_treshold=1):
    """Return the list of HGNC symbols that match annotated HPO terms.

    Args:
        username (str): username to use for phenomizer connection
        password (str): password to use for phenomizer connection

    Returns:
        query_result: a generator of dictionaries on the form
        {
            'p_value': float,
            'disease_source': str,
            'disease_nr': int,
            'gene_symbols': list(str),
            'description': str,
            'raw_line': str
        }
    """
    # skip querying Phenomizer unless at least one HPO terms exists
    try:
        results = query_phenomizer.query(username, password, *hpo_ids)
        diseases = [result for result in results
                    if result['p_value'] <= p_value_treshold]
        return diseases
    except SystemExit:
        return None


def rerun(store, mail, current_user, institute_id, case_name, sender, recipient):
    """Request a rerun by email."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for('cases.case', institute_id=institute_id, case_name=case_name)
    store.request_rerun(institute_obj, case_obj, user_obj, link)

    # this should send a JSON document to the SuSy API in the future
    html = """
        <p>{institute}: {case} ({case_id})</p>
        <p>Re-run requested by: {name}</p>
    """.format(institute=institute_obj['display_name'],
               case=case_obj['display_name'], case_id=case_obj['_id'],
               name=user_obj['name'].encode())

    # compose and send the email message
    msg = Message(subject=("SCOUT: request RERUN for {}"
                           .format(case_obj['display_name'])),
                  html=html, sender=sender, recipients=[recipient],
                  # cc the sender of the email for confirmation
                  cc=[user_obj['email']])
    mail.send(msg)


def update_default_panels(store, current_user, institute_id, case_name, panel_ids):
    """Update default panels for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for('cases.case', institute_id=institute_id, case_name=case_name)
    panel_objs = [store.panel(panel_id) for panel_id in panel_ids]
    store.update_default_panels(institute_obj, case_obj, user_obj, link, panel_objs)

def vcf2cytosure(store, institute_id, case_name, individual_id):
    """vcf2cytosure CGH file for inidividual."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    for individual in case_obj['individuals']:
        if individual['individual_id'] == individual_id:
            individual_obj = individual

    return (individual_obj['display_name'], individual_obj['vcf2cytosure'])


def multiqc(store, institute_id, case_name):
    """Find MultiQC report for the case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    return dict(
        institute=institute_obj,
        case=case_obj,
    )


def get_sanger_unevaluated(store, institute_id):
    """Get all variants for an institute having Sanger validations ordered but still not evaluated

        Args:
            store(scout.adapter.MongoAdapter)
            institute_id(str)

        Returns:
            unevaluated: a list that looks like this: [ {'case1': [varID_1, varID_2, .., varID_n]}, {'case2' : [varID_1, varID_2, .., varID_n]} ],
                         where the keys are case_ids and the values are lists of variants with Sanger ordered but not yet validated

    """

    # Retrieve a list of ids for variants with Sanger ordered grouped by case from the 'event' collection
    # This way is much faster than querying over all variants in all cases of an institute
    sanger_ordered_by_case = store.sanger_ordered_by_institute(institute_id)
    unevaluated = []

    # for each object where key==case and value==[variant_id with Sanger ordered]
    for item in sanger_ordered_by_case:
        case_id = item['_id']
        # Get the case to collect display name
        case_obj = store.case(case_id=case_id)

        if not case_obj: # the case might have been removed
            continue

        case_display_name = case_obj.get('display_name')

        # List of variant document ids
        varid_list = item['vars']

        unevaluated_by_case = {}
        unevaluated_by_case[case_display_name] = []

        for var_id in varid_list:
            # For each variant with sanger validation ordered
            variant_obj = store.variant(document_id=var_id, case_id=case_id)

            # Double check that Sanger was ordered (and not canceled) for the variant
            if variant_obj is None or variant_obj.get('sanger_ordered') is None:
                continue

            validation = variant_obj.get('validation', 'not_evaluated')

            # Check that the variant is not evaluated
            if validation in ['True positive', 'False positive']:
                continue

            unevaluated_by_case[case_display_name].append(variant_obj['_id'])

        # If for a case there is at least one Sanger validation to evaluate add the object to the unevaluated objects list
        if len(unevaluated_by_case[case_display_name]) > 0:
            unevaluated.append(unevaluated_by_case)

    return unevaluated
