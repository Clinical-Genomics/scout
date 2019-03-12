import logging
from flask_login import current_user

LOG = logging.getLogger(__name__)

def get_dashboard_info(adapter, institute_id=None, slice_query=None):
    """Returns cases with phenotype

        If phenotypes are provided search for only those

    Args:
        adapter(adapter.MongoAdapter)
        institute_id(str)
        slice_query(str):   Query to filter cases to obtain statistics for.

    Returns:
        data(dict): Dictionary with relevant information
    """

    LOG.debug("General query with institute_id {}.".format(institute_id))

    # if institute_id == 'None' or None, all cases and general stats will be returned
    if institute_id == 'None':
        institute_id = None

    general_info = get_general_case_info(adapter, institute_id=institute_id,
                                                    slice_query=slice_query)
    total_cases = general_info['total_cases']

    data = {'total_cases': total_cases}
    if total_cases == 0:
        return data

    data['pedigree'] = []
    for ped_info in general_info['pedigree'].values():
        ped_info['percent'] = ped_info['count'] / total_cases
        data['pedigree'].append(ped_info)


    data['cases'] = get_case_groups(adapter, total_cases,
                        institute_id=institute_id, slice_query=slice_query)

    data['analysis_types'] = get_analysis_types(adapter, total_cases,
                                institute_id=institute_id, slice_query=slice_query)

    # VARIANTS

    # Here we disregard any slice query.
    general_info = get_general_case_info(adapter, institute_id=institute_id)

    total_cases = general_info['total_cases']
    # Fetch variant information
    LOG.info("Fetch sanger variants")
    order_query = {'sanger_ordered': True}
    # NOTE: this will not find all verified variants. Any pinned variant can
    #       be tagged true or false positive. Generally speaking all
    #       causatives were true positives.

    # validation_query = {'validation': {'$in'}} #unused
    # Also actually query for TPs and FPs
    tp_query = {'validation': "True positive"}
    fp_query = {'validation': "False positive"}

    # Case level information
    ordered_validation_cases = set()
    validated_cases = set()

    # Variant level information
    validated_tp = set()
    validated_fp = set()

    LOG.info("Find all validated variants with query {}".format(order_query))
    validation_ordered = adapter.variant_collection.find(order_query)

# If you want the full collection:
#    validation_status_set = adapter.variant_collection.find(
#                    {'validation': {'$in': ["False positive", "True positive"]}})

    validated_tp_cursor = adapter.variant_collection.find(tp_query)
    validated_fp_cursor = adapter.variant_collection.find(fp_query)

    case_ids = general_info['case_ids']
    nr_ordered = 0
    for nr_ordered, variant in enumerate(validation_ordered,1):
        case_id = variant['case_id']
        if institute_id:
            if not case_id in case_ids:
                continue
    #    variant_id = variant['_id']
        # Add case id to validation cases
        if case_id not in ordered_validation_cases:
            ordered_validation_cases.add(case_id)

    for our_validated_positives, variant in enumerate(validated_tp_cursor, 1):
        case_id = variant['case_id']
        if institute_id:
            if not case_id in case_ids:
                continue

        variant_id = variant['_id']
        validation = variant.get('validation')
        if validation == 'True positive':
            validated_tp.add(variant_id)
            if case_id not in validated_cases:
                validated_cases.add(case_id)

    for our_validated_negatives, variant in enumerate(validated_fp_cursor, 1):
        case_id = variant['case_id']
        if institute_id:
            if not case_id in case_ids:
                continue

        variant_id = variant['_id']
        validation = variant.get('validation')
        if validation == 'False positive':
            validated_fp.add(variant_id)
            if case_id not in validated_cases:
                validated_cases.add(case_id)

    nr_validation_cases = len(ordered_validation_cases)

    overview = [
        {
            'title': 'Phenotype terms',
            'count': general_info['phenotype_cases'],
            'percent': general_info['phenotype_cases'] / total_cases,
        },
        {
            'title': 'Causative variants',
            'count': general_info['causative_cases'],
            'percent': general_info['causative_cases'] / total_cases,
        },
        {
            'title': 'Pinned variants',
            'count': general_info['pinned_cases'],
            'percent': general_info['pinned_cases'] / total_cases,
        },
        {
            'title': 'Cohort tag',
            'count': general_info['cohort_cases'],
            'percent': general_info['cohort_cases'] / total_cases,
        }
    ]
    if nr_validation_cases or validated_cases:
        overview.append(
        {
            'title': 'Validation ordered',
            'count': nr_validation_cases,
            'percent': nr_validation_cases / total_cases,
        })
        overview.append(
        {
            'title': 'Validated cases',
            'count': len(validated_cases),
            'percent': len(validated_cases) / total_cases,
        })

    data['overview'] = overview

    variants = []
    nr_validated = our_validated_positives + our_validated_negatives
    if nr_ordered:
        variants.append(
            {
                'title': 'Validation ordered',
                'count': nr_ordered,
                'percent': 1
            }
        )
    if nr_validated:
            variants.append(
                {
                    'title': 'Validated True Positive',
                    'count': len(validated_tp),
                    'percent': len(validated_tp) / nr_validated,
                }
            )

            variants.append(
                {
                    'title': 'Validated False Positive',
                    'count': len(validated_fp),
                    'percent': len(validated_fp) / nr_validated,
                }
            )

    data['variants'] = variants

    return data

def get_general_case_info(adapter, institute_id=None, slice_query=None):
    """Return general information about cases

    Args:
        adapter(adapter.MongoAdapter)
        institute_id(str)
        slice_query(str):   Query to filter cases to obtain statistics for.


    Returns:
        general(dict)
    """
    general = {}

    # Potentially sensitive slice queries are assumed allowed if we have got this far
    name_query = slice_query

    cases = adapter.cases(owner=institute_id, name_query=name_query)

    phenotype_cases = 0
    causative_cases = 0
    pinned_cases = 0
    cohort_cases = 0

    pedigree = {
        1: {
            'title': 'Single',
            'count': 0
        },
        2: {
            'title': 'Duo',
            'count': 0
        },
        3: {
            'title': 'Trio',
            'count': 0
        },
        'many': {
            'title': 'Many',
            'count': 0
        },
    }

    case_ids = set()

    total_cases = 0
    for total_cases,case in enumerate(cases,1):
        # If only looking at one institute we need to save the case ids
        if institute_id:
            case_ids.add(case['_id'])
        if case.get('phenotype_terms'):
            phenotype_cases += 1
        if case.get('causatives'):
            causative_cases += 1
        if case.get('suspects'):
            pinned_cases += 1
        if case.get('cohorts'):
            cohort_cases += 1

        nr_individuals = len(case.get('individuals',[]))
        if nr_individuals == 0:
            continue
        if nr_individuals > 3:
            pedigree['many']['count'] += 1
        else:
            pedigree[nr_individuals]['count'] += 1

    general['total_cases'] = total_cases
    general['phenotype_cases'] = phenotype_cases
    general['causative_cases'] = causative_cases
    general['pinned_cases'] = pinned_cases
    general['cohort_cases'] = cohort_cases
    general['pedigree'] = pedigree
    general['case_ids'] = case_ids

    return general


def get_case_groups(adapter, total_cases, institute_id=None, slice_query=None):
    """Return the information about case groups

    Args:
        store(adapter.MongoAdapter)
        total_cases(int): Total number of cases
        slice_query(str): Query to filter cases to obtain statistics for.

    Returns:
        cases(dict):
    """
    # Create a group with all cases in the database
    cases = [{'status': 'all', 'count': total_cases, 'percent': 1}]
    # Group the cases based on their status
    pipeline = []
    group = {'$group' : {'_id': '$status', 'count': {'$sum': 1}}}

    subquery = {}
    if institute_id and slice_query:
        subquery = adapter.cases(owner=institute_id, name_query=slice_query,
                              yield_query=True)
    elif institute_id:
        subquery = adapter.cases(owner=institute_id, yield_query=True)
    elif slice_query:
        subquery = adapter.cases(name_query=slice_query, yield_query=True)

    query = {'$match': subquery} if subquery else {}

    if query:
        pipeline.append(query)

    pipeline.append(group)
    res = adapter.case_collection.aggregate(pipeline)

    for status_group in res:
        cases.append({'status': status_group['_id'],
                      'count': status_group['count'],
                      'percent': status_group['count'] / total_cases})

    return cases

def get_analysis_types(adapter, total_cases, institute_id=None, slice_query=None):
    """ Return information about analysis types.
        Group cases based on analysis type for the individuals.
    Args:
        adapter(adapter.MongoAdapter)
        total_cases(int): Total number of cases
        institute_id(str)
        slice_query(str): Query to filter cases to obtain statistics for.
    Returns:
        analysis_types array of hashes with name: analysis_type(str), count: count(int)

    """
    # Group cases based on analysis type of the individuals
    query = {}

    subquery = {}
    if institute_id and slice_query:
        subquery = adapter.cases(owner=institute_id, name_query=slice_query,
                              yield_query=True)
    elif institute_id:
        subquery = adapter.cases(owner=institute_id, yield_query=True)
    elif slice_query:
        subquery = adapter.cases(name_query=slice_query, yield_query=True)

    query = {'$match': subquery}

    pipeline = []
    if query:
        pipeline.append(query)

    pipeline.append({'$unwind': '$individuals'})
    pipeline.append({'$group': {'_id': '$individuals.analysis_type', 'count': {'$sum': 1}}})
    analysis_query = adapter.case_collection.aggregate(pipeline)
    analysis_types = [{'name': group['_id'], 'count': group['count']} for group in analysis_query]

    return analysis_types
