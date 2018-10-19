import logging

LOG = logging.getLogger(__name__)

def get_dashboard_info(adapter, institute_id=None):
    """Returns cases with phenotype
    
        If phenotypes are provided search for only those
    
    Args:
        adapter(adapter.MongoAdapter)
        institute_id(str)
    
    Returns:
        data(dict): Dictionary with relevant information
    """
    general_info = get_general_case_info(adapter, institute_id)
    total_cases = general_info['total_cases']
    
    data = {'total_cases': total_cases}
    if total_cases == 0:
        return data
    
    data['pedigree'] = []
    for ped_info in general_info['pedigree'].values():
        ped_info['percent'] = ped_info['count'] / total_cases
        data['pedigree'].append(ped_info)
        
    
    data['cases'] = get_case_groups(adapter, total_cases, institute_id)
    
    data['analysis_types'] = get_analysis_types(adapter, total_cases, institute_id)

    # Fetch variant information
    LOG.info("Fetch sanger variants")
    validation_query = {'sanger_ordered': True}

    # Case level information
    validation_cases = set()
    validated_cases = set()
    
    # Variant level information
    validated_tp = set()
    validated_fp = set()

    LOG.info("Find all validated variants with query {}".format(institute_id))
    validation_ordered = adapter.variant_collection.find(validation_query)

    case_ids = general_info['case_ids']
    nr_ordered = 0
    for nr_ordered, variant in enumerate(validation_ordered,1):
        case_id = variant['case_id']
        if institute_id:
            if not case_id in case_ids:
                continue
        variant_id = variant['_id']
        # Add case id to validation cases
        validation_cases.add(case_id)

        validation = variant.get('validation')
        if validation == 'True positive':
            validated_tp.add(variant_id)
            validated_cases.add(case_id)

        elif validation == 'False positive':
            validated_fp.add(variant_id)
            validated_cases.add(case_id)
    
    nr_validation_cases = len(validation_cases)

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
    if nr_validation_cases:
        overview.append(
        {
            'title': 'Validation ordered',
            'count': nr_validation_cases,
            'percent': nr_validation_cases / total_cases,
        })
        overview.append(
        {
            'title': 'Validated',
            'count': len(validated_cases),
            'percent': len(validated_cases) / nr_validation_cases,
        })

    data['overview'] = overview
    
    variants = []
    nr_validated = len(validated_tp) + len(validated_fp)
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

def get_general_case_info(adapter, institute_id=None):
    """Return general information about cases
    
    Args:
        adapter(adapter.MongoAdapter)
        institute_id(str)
    
    Returns:
        general(dict)
    """
    general = {}
    # Fetch information about cases with certain activities
    cases = adapter.cases(collaborator=institute_id)
    
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
    

def get_case_groups(adapter, total_cases, institute_id=None):
    """Return the information about case groups
    
    Args:
        store(adapter.MongoAdapter)
        total_cases(int): Total number of cases
    
    Returns:
        cases(dict):
    """
    # Create a group with all cases in the database
    cases = [{'status': 'all', 'count': total_cases, 'percent': 1}]
    # Group the cases based on their status
    pipeline = []
    group = {'$group' : {'_id': '$status', 'count': {'$sum': 1}}}
    query = {}
    if institute_id:
        query = {'$match': {'owner': institute_id}}
    
    if query:
        pipeline.append(query)

    pipeline.append(group)
    res = adapter.case_collection.aggregate(pipeline)
    
    for status_group in res:
        cases.append({'status': status_group['_id'],
                      'count': status_group['count'],
                      'percent': status_group['count'] / total_cases})
    
    return cases

def get_analysis_types(adapter, total_cases, institute_id=None):
    """Return information about case status"""
    # Group cases based on analysis type of the individuals
    query = {}
    if institute_id:
        query = {'$match': {'owner': institute_id}}
    
    pipeline = []
    if query:
        pipeline.append(query)
    
    pipeline.append({'$unwind': '$individuals'})
    pipeline.append({'$group': {'_id': '$individuals.analysis_type', 'count': {'$sum': 1}}})
    analysis_query = adapter.case_collection.aggregate(pipeline)
    analysis_types = [{'name': group['_id'], 'count': group['count']} for group in analysis_query]
    
    return analysis_types