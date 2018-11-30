# -*- coding: utf-8 -*-
import os
import itertools
import requests
import datetime

from bs4 import BeautifulSoup
from xlsxwriter import Workbook
from flask import url_for
from flask_mail import Message
import query_phenomizer

from scout.constants import (CASE_STATUSES, PHENOTYPE_GROUPS, COHORT_TAGS, SEX_MAP, PHENOTYPE_MAP, VERBS_MAP, MT_EXPORT_HEADER)
from scout.constants.variant_tags import MANUAL_RANK_OPTIONS, DISMISS_VARIANT_OPTIONS, GENETIC_MODELS
from scout.export.variant import export_mt_variants
from scout.server.utils import institute_and_case
from scout.parse.clinvar import clinvar_submission_header, clinvar_submission_lines
from scout.server.blueprints.variants.controllers import variant as variant_decorator
from scout.server.blueprints.variants.controllers import sv_variant

STATUS_MAP = {'solved': 'bg-success', 'archived': 'bg-warning'}


def cases(store, case_query, limit=100):
    """Preprocess case objects.

    Add the necessary information to display the 'cases' view

    Args:
        store(adapter.MongoAdapter)
        case_query(pymongo.Cursor)
        limit(int): Maximum number of cases to display

    Returns:
        data(dict): includes the cases, how many there are and the limit.
    """

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
    """Preprocess a single case.

    Prepare the case to be displayed in the case view.

    Args:
        store(adapter.MongoAdapter)
        institute_obj(models.Institute)
        case_obj(models.Case)

    Returns:
        data(dict): includes the cases, how many there are and the limit.

    """
    # Convert individual information to more readable format
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

    # Fetch the variant objects for suspects and causatives
    suspects = [store.variant(variant_id) or variant_id for variant_id in
                case_obj.get('suspects', [])]
    causatives = [store.variant(variant_id) or variant_id for variant_id in
                  case_obj.get('causatives', [])]

    # Set of all unique genes in the default gene panels
    distinct_genes = set()
    case_obj['panel_names'] = []
    for panel_info in case_obj.get('panels', []):
        if not panel_info.get('is_default'):
            continue
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
    """Gather contents to be visualized in a case report

    Args:
        store(adapter.MongoAdapter)
        institute_obj(models.Institute)
        case_obj(models.Case)

    Returns:
        data(dict)

    """
    variant_types = {
        'causatives_detailed': 'causatives',
        'suspects_detailed': 'suspects',
        'classified_detailed': 'acmg_classification',
        'tagged_detailed': 'manual_rank',
        'dismissed_detailed': 'dismiss_variant',
        'commented_detailed': 'is_commented',
    }
    data = case_obj

    # Add the case comments
    data['comments'] = store.events(institute_obj, case=case_obj, comments=True)

    data['manual_rank_options'] = MANUAL_RANK_OPTIONS
    data['dismissed_options'] = DISMISS_VARIANT_OPTIONS
    data['genetic_models'] = dict(GENETIC_MODELS)
    data['report_created_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    evaluated_variants = {}
    for vt in variant_types:
        evaluated_variants[vt] = []
    # We collect all causatives and suspected variants
    # These are handeled in separate since they are on case level
    for var_type in ['causatives', 'suspects']:
        #These include references to variants
        vt = '_'.join([var_type, 'detailed'])
        for var_id in case_obj.get(var_type,[]):
            variant_obj = store.variant(var_id)
            if not variant_obj:
                continue
            # If the variant exists we add it to the evaluated variants
            evaluated_variants[vt].append(variant_obj)

    ## get variants for this case that are either classified, commented, tagged or dismissed.
    for var_obj in store.evaluated_variants(case_id=case_obj['_id']):
        # Check which category it belongs to
        for vt in variant_types:
            keyword = variant_types[vt]
            # When found we add it to the categpry
            # Eac variant can belong to multiple categories
            if keyword in var_obj:
                evaluated_variants[vt].append(var_obj)

    for var_type in evaluated_variants:
        decorated_variants = []
        for var_obj in evaluated_variants[var_type]:
        # We decorate the variant with some extra information
            if var_obj['category'] == 'snv':
                decorated_info = variant_decorator(
                        store=store,
                        institute_obj=institute_obj,
                        case_obj=case_obj,
                        variant_id=None,
                        variant_obj=var_obj,
                        add_case=False,
                        add_other=False,
                        get_overlapping=False
                    )
            else:
                decorated_info = sv_variant(
                    store=store,
                    institute_id=institute_obj['_id'],
                    case_name=case_obj['display_name'],
                    variant_obj=var_obj,
                    add_case=False,
                    get_overlapping=False
                    )
            decorated_variants.append(decorated_info['variant'])
        # Add the decorated variants to the case
        data[var_type] = decorated_variants

    return data


def coverage_report_contents(store, institute_obj, case_obj, base_url):
    """Posts a request to chanjo-report and capture the body of the returned response to include it in case report

    Args:
        store(adapter.MongoAdapter)
        institute_obj(models.Institute)
        case_obj(models.Case)
        base_url(str): base url of server

    Returns:
        coverage_data(str): string rendering of the content between <body </body> tags of a coverage report
    """

    request_data = {}
    # extract sample ids from case_obj and add them to the post request object:
    request_data['sample_id'] = [ ind['individual_id'] for ind in case_obj['individuals'] ]

    # extract default panel names and default genes from case_obj and add them to the post request object
    distinct_genes = set()
    panel_names = []
    for panel_info in case_obj.get('panels', []):
        if not panel_info.get('is_default'):
            continue
        panel_obj = store.gene_panel(panel_info['panel_name'], version=panel_info.get('version'))
        full_name = "{} ({})".format(panel_obj['display_name'], panel_obj['version'])
        panel_names.append(full_name)
    panel_names = ' ,'.join(panel_names)
    request_data['panel_name'] = panel_names

    # add institute-specific cutoff level to the post request object
    request_data['level'] = institute_obj.get('coverage_cutoff', 15)

    #send get request to chanjo report
    resp = requests.get(base_url+'reports/report', params=request_data)

    #read response content
    soup = BeautifulSoup(resp.text)

    # remove links in the printed version of coverage report
    for tag in soup.find_all('a'):
        tag.replaceWith('')

    #extract body content using BeautifulSoup
    coverage_data = ''.join(['%s' % x for x in soup.body.contents])

    return coverage_data


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


def mt_excel_files(store, case_obj, temp_excel_dir):
    """Collect MT variants and format line of a MT variant report
    to be exported in excel format

    Args:
        store(adapter.MongoAdapter)
        case_obj(models.Case)
        temp_excel_dir(os.Path): folder where the temp excel files are written to

    Returns:
        written_files(int): the number of files written to temp_excel_dir

    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    samples = case_obj.get('individuals')

    query = {'chrom':'MT'}
    mt_variants = list(store.variants(case_id=case_obj['_id'], query=query, nr_of_variants= -1, sort_key='position'))

    written_files = 0
    for sample in samples:
        sample_id = sample['individual_id']
        sample_lines = export_mt_variants(variants=mt_variants, sample_id=sample_id)

        # set up document name
        document_name = '.'.join([case_obj['display_name'], sample_id, today]) + '.xlsx'
        workbook = Workbook(os.path.join(temp_excel_dir,document_name))
        Report_Sheet = workbook.add_worksheet()

        # Write the column header
        row = 0
        for col,field in enumerate(MT_EXPORT_HEADER):
            Report_Sheet.write(row,col,field)

        # Write variant lines, after header (start at line 1)
        for row, line in enumerate(sample_lines,1): # each line becomes a row in the document
            for col, field in enumerate(line): # each field in line becomes a cell
                Report_Sheet.write(row,col,field)
        workbook.close()

        if os.path.exists(os.path.join(temp_excel_dir,document_name)):
            written_files += 1

    return written_files


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


def get_sanger_unevaluated(store, institute_id, user_id):
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
    sanger_ordered_by_case = store.sanger_ordered(institute_id, user_id)
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
            if variant_obj is None or variant_obj.get('sanger_ordered') is None or variant_obj.get('sanger_ordered') is False:
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
