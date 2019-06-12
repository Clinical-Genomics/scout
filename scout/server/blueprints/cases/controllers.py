# -*- coding: utf-8 -*-
import os
import itertools
import requests
import datetime

import logging

from bs4 import BeautifulSoup
from xlsxwriter import Workbook
from flask import url_for, current_app
from flask_mail import Message
import query_phenomizer
from flask_login import current_user

from scout.constants import (CASE_STATUSES, PHENOTYPE_GROUPS, COHORT_TAGS, SEX_MAP, PHENOTYPE_MAP,
                             CANCER_PHENOTYPE_MAP, VERBS_MAP, MT_EXPORT_HEADER)
from scout.constants.variant_tags import MANUAL_RANK_OPTIONS, DISMISS_VARIANT_OPTIONS, GENETIC_MODELS
from scout.export.variant import export_mt_variants
from scout.server.utils import institute_and_case, user_institutes
from scout.parse.clinvar import clinvar_submission_header, clinvar_submission_lines
from scout.server.blueprints.variants.controllers import variant as variant_decorator
from scout.server.blueprints.variants.controllers import sv_variant
from scout.parse.matchmaker import hpo_terms, omim_terms, genomic_features, parse_matches
from scout.utils.matchmaker import matchmaker_request
from scout.server.blueprints.variants.controllers import get_predictions
from scout.server.blueprints.genes.controllers import gene

LOG = logging.getLogger(__name__)


STATUS_MAP = {'solved': 'bg-success', 'archived': 'bg-warning'}

TRACKS = {
    'rare': 'Rare Disease',
    'cancer': 'Cancer',
}

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
        case_obj['display_track'] = TRACKS[case_obj.get('track', 'rare')]

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

        pheno_map = PHENOTYPE_MAP
        if case_obj.get('track', 'rare') == 'cancer':
            pheno_map = CANCER_PHENOTYPE_MAP

        individual['phenotype_human'] = pheno_map.get(individual['phenotype'])
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
    o_collaborators = []
    for collab_id in case_obj['collaborators']:
        if collab_id != case_obj['owner'] and store.institute(collab_id):
            o_collaborators.append(store.institute(collab_id))

    case_obj['o_collaborators'] = [(collab_obj['_id'], collab_obj['display_name']) for
                                   collab_obj in o_collaborators]

    irrelevant_ids = ('cust000', institute_obj['_id'])
    collab_ids = [(collab['_id'], collab['display_name']) for collab in store.institutes() if
                  (collab['_id'] not in irrelevant_ids) and
                  (collab['_id'] not in case_obj['collaborators'])]

    events = list(store.events(institute_obj, case=case_obj))
    for event in events:
        event['verb'] = VERBS_MAP[event['verb']]

    case_obj['clinvar_variants'] = store.case_to_clinVars(case_obj['_id'])

    # if updated_at is a list, set it to the last update datetime
    if case_obj.get('updated_at') and isinstance(case_obj['updated_at'], list):
        case_obj['updated_at'] = max(case_obj['updated_at'])

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
        'mme_nodes': current_app.mme_nodes, # Get available MatchMaker nodes for matching case
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

    for individual in data['individuals']:
        try:
            sex = int(individual.get('sex', 0))
        except ValueError as err:
            sex = 0
        individual['sex_human'] = SEX_MAP[sex]
        individual['phenotype_human'] = PHENOTYPE_MAP.get(individual['phenotype'])

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
        display_name = sample['display_name']
        sample_lines = export_mt_variants(variants=mt_variants, sample_id=sample_id)

        # set up document name
        document_name = '.'.join([case_obj['display_name'], display_name, today]) + '.xlsx'
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
    if case_obj['synopsis'] != new_synopsis:
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

def gene_variants(store, variants_query, page=1, per_page=50):
    """Pre-process list of variants."""
    variant_count = variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False
    variant_res = variants_query.skip(skip_count).limit(per_page)

    my_institutes = list(inst['_id'] for inst in user_institutes(store, current_user))

    variants = []
    for variant_obj in variant_res:
        # hide other institutes for now
        if variant_obj['institute'] not in my_institutes:
            LOG.warning("Institute {} not allowed.".format(variant_obj['institute']))
            continue

        # Populate variant case_display_name
        variant_case_obj = store.case(case_id=variant_obj['case_id'])
        if not variant_case_obj:
            # A variant with missing case was encountered
            continue
        case_display_name = variant_case_obj.get('display_name')
        variant_obj['case_display_name'] = case_display_name

        genome_build = variant_case_obj.get('genome_build', '37')
        if genome_build not in ['37','38']:
            genome_build = '37'

        # Update the HGNC symbols if they are not set
        variant_genes = variant_obj.get('genes')
        if variant_genes is not None:
            for gene_obj in variant_genes:
                # If there is no hgnc id there is nothin we can do
                if not gene_obj['hgnc_id']:
                    continue
                # Else we collect the gene object and check the id
                if gene_obj.get('hgnc_symbol') is None or gene_obj.get('description') is None:
                    hgnc_gene = store.hgnc_gene(gene_obj['hgnc_id'], build=genome_build)
                    if not hgnc_gene:
                        continue
                    gene_obj['hgnc_symbol'] = hgnc_gene['hgnc_symbol']
                    gene_obj['description'] = hgnc_gene['description']

        # Populate variant HGVS and predictions
        gene_ids = []
        gene_symbols = []
        hgvs_c = []
        hgvs_p = []
        variant_genes = variant_obj.get('genes')

        if variant_genes is not None:
            functional_annotation = ''

            for gene_obj in variant_genes:
                hgnc_id = gene_obj['hgnc_id']
                gene_symbol = gene(store, hgnc_id)['symbol']
                gene_ids.append(hgnc_id)
                gene_symbols.append(gene_symbol)

                hgvs_nucleotide = '-'
                # gather HGVS info from gene transcripts
                transcripts_list = gene_obj.get('transcripts')
                for transcript_obj in transcripts_list:
                    if transcript_obj.get('is_canonical') and transcript_obj.get('is_canonical') is True:
                        hgvs_nucleotide = str(transcript_obj.get('coding_sequence_name'))
                        hgvs_protein = str(transcript_obj.get('protein_sequence_name'))
                hgvs_c.append(hgvs_nucleotide)
                hgvs_p.append(hgvs_protein)

            if len(gene_symbols) == 1:
                if(hgvs_p[0] != "None"):
                    hgvs = hgvs_p[0]
                elif(hgvs_c[0] != "None"):
                    hgvs = hgvs_c[0]
                else:
                    hgvs = "-"
                variant_obj['hgvs'] = hgvs

            # populate variant predictions for display
            variant_obj.update(get_predictions(variant_genes))

        variants.append(variant_obj)

    return {
        'variants': variants,
        'more_variants': more_variants,
    }

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


def mme_add(store, user_obj, case_obj, add_gender, add_features, add_disorders, genes_only,
    mme_base_url, mme_accepts, mme_token):
    """Add a patient to MatchMaker server

    Args:
        store(adapter.MongoAdapter)
        user_obj(dict) a scout user object (to be added as matchmaker contact)
        case_obj(dict) a scout case object
        add_gender(bool) if True case gender will be included in matchmaker
        add_features(bool) if True HPO features will be included in matchmaker
        add_disorders(bool) if True OMIM diagnoses will be included in matchmaker
        genes_only(bool) if True only genes and not variants will be shared
        mme_base_url(str) base url of the MME server
        mme_accepts(str) request content accepted by MME server
        mme_token(str) auth token of the MME server

    Returns:
        submitted_info(dict) info submitted to MatchMaker and its responses
    """

    if not mme_base_url or not mme_accepts or not mme_token:
        return 'Please check that Matchmaker connection parameters are valid'
    url = ''.join([mme_base_url, '/patient/add'])
    features = []   # this is the list of HPO terms
    disorders = []  # this is the list of OMIM diagnoses
    g_features = []

     # create contact dictionary
    contact_info = {
        'name' : user_obj['name'],
        'href' : ''.join( ['mailto:',user_obj['email']] ),
        'institution' : 'Scout software user, Science For Life Laboratory, Stockholm, Sweden'
    }
    if add_features: # create features dictionaries
        features = hpo_terms(case_obj)

    if add_disorders: # create OMIM disorders dictionaries
        disorders = omim_terms(case_obj)

    # send a POST request and collect response for each affected individual in case
    server_responses = []

    submitted_info = {
        'contact' : contact_info,
        'sex' : add_gender,
        'features' : features,
        'disorders' : disorders,
        'genes_only' : genes_only,
        'patient_id' : []
    }
    for individual in case_obj.get('individuals'):
        if not individual['phenotype'] in  [2, 'affected']: # include only affected individuals
            continue

        patient = {
            'contact' : contact_info,
            'id' : '.'.join([case_obj['_id'], individual.get('individual_id')]), # This is a required field form MME
            'label' : '.'.join([case_obj['display_name'], individual.get('display_name')]),
            'features' : features,
            'disorders' : disorders
        }
        if add_gender:
            if individual['sex'] == '1':
                patient['sex'] = 'MALE'
            else:
                patient['sex'] = 'FEMALE'

        if case_obj.get('suspects'):
            g_features = genomic_features(store, case_obj, individual.get('display_name'), genes_only)
            patient['genomicFeatures'] = g_features

        # send add request to server and capture response
        resp = matchmaker_request(url=url, token=mme_token, method='POST', content_type=mme_accepts,
            accept='application/json', data={'patient':patient})

        server_responses.append({
                'patient': patient,
                'message': resp.get('message'),
                'status_code' : resp.get('status_code')
            })
    submitted_info['server_responses'] = server_responses
    return submitted_info


def mme_delete(case_obj, mme_base_url, mme_token):
    """Delete all affected samples for a case from MatchMaker

    Args:
        case_obj(dict) a scout case object
        mme_base_url(str) base url of the MME server
        mme_token(str) auth token of the MME server

    Returns:
         server_responses(list): a list of object of this type:
                    {
                        'patient_id': patient_id
                        'message': server_message,
                        'status_code': server_status_code
                    }
    """
    server_responses = []

    if not mme_base_url or not mme_token:
        return 'Please check that Matchmaker connection parameters are valid'

    # for each patient of the case in matchmaker
    for patient in case_obj['mme_submission']['patients']:

        # send delete request to server and capture server's response
        patient_id = patient['id']
        url = ''.join([mme_base_url, '/patient/delete/', patient_id])
        resp = matchmaker_request(url=url, token=mme_token, method='DELETE', )

        server_responses.append({
            'patient_id': patient_id,
            'message': resp.get('message'),
            'status_code': resp.get('status_code')
        })

    return server_responses


def mme_matches(case_obj, institute_obj, mme_base_url, mme_token):
    """Show Matchmaker submission data for a sample and eventual matches.

    Args:
        case_obj(dict): a scout case object
        institute_obj(dict): an institute object
        mme_base_url(str) base url of the MME server
        mme_token(str) auth token of the MME server

    Returns:
        data(dict): data to display in the html template
    """
    data = {
        'institute' : institute_obj,
        'case' : case_obj,
        'server_errors' : []
    }
    matches = {}
    # loop over the submitted samples and get matches from the MatchMaker server
    if not case_obj.get('mme_submission'):
        return None

    for patient in case_obj['mme_submission']['patients']:
        patient_id = patient['id']
        matches[patient_id] = None
        url = ''.join([ mme_base_url, '/matches/', patient_id])
        server_resp = matchmaker_request(url=url, token=mme_token, method='GET')
        if 'status_code' in server_resp: # the server returned a valid response
            # and this will be a list of match objects sorted by desc date
            pat_matches = []
            if server_resp.get('matches'):
                pat_matches = parse_matches(patient_id, server_resp['matches'])
            matches[patient_id] = pat_matches
        else:
            LOG.warning('Server returned error message: {}'.format(server_resp['message']))
            data['server_errors'].append(server_resp['message'])

    data['matches'] = matches

    return data


def mme_match(case_obj, match_type, mme_base_url, mme_token, nodes=None, mme_accepts=None):
    """Initiate a MatchMaker match against either other Scout patients or external nodes

    Args:
        case_obj(dict): a scout case object already submitted to MME
        match_type(str): 'internal' or 'external'
        mme_base_url(str): base url of the MME server
        mme_token(str): auth token of the MME server
        mme_accepts(str): request content accepted by MME server (only for internal matches)

    Returns:
        matches(list): a list of eventual matches
    """
    query_patients = []
    server_responses = []
    url = None
    # list of patient dictionaries is required for internal matching
    query_patients = case_obj['mme_submission']['patients']
    if match_type=='internal':
        url = ''.join([mme_base_url,'/match'])
        for patient in query_patients:
            json_resp = matchmaker_request(url=url, token=mme_token, method='POST',
                content_type=mme_accepts, accept=mme_accepts, data={'patient':patient})
            resp_obj = {
                'server' : 'Local MatchMaker node',
                'patient_id' : patient['id'],
                'results' : json_resp.get('results'),
                'status_code' : json_resp.get('status_code'),
                'message' : json_resp.get('message') # None if request was successful
            }
            server_responses.append(resp_obj)
    else: # external matching
        # external matching requires only patient ID
        query_patients = [ patient['id'] for patient in query_patients]
        node_ids = [ node['id'] for node in nodes ]
        if match_type in node_ids: # match is against a specific external node
            node_ids = [match_type]

        # Match every affected patient
        for patient in query_patients:
            # Against every node
            for node in node_ids:
                url = ''.join([mme_base_url,'/match/external/', patient, '?node=', node])
                json_resp = matchmaker_request(url=url, token=mme_token, method='POST')
                resp_obj = {
                    'server' : node,
                    'patient_id' : patient,
                    'results' : json_resp.get('results'),
                    'status_code' : json_resp.get('status_code'),
                    'message' : json_resp.get('message') # None if request was successful
                }
                server_responses.append(resp_obj)
    return server_responses
