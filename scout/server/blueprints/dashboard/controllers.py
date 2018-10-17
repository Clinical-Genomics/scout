import logging

LOG = logging.getLogger(__name__)

def get_dashboard_info(adapter, total_cases, institute_id=None):
    """Returns cases with phenotype
    
        If phenotypes are provided search for only those
    
    Args:
        adapter(adapter.MongoAdapter)
        institute_obj(models.Institute)
    
    Returns:
        data(dict): Dictionary with relevant information
    """
    total_cases = total_cases or 0
    data = {}
    if total_cases == 0:
        return data
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


    data['cases'] = cases
    
    # Group cases based on analysis type
    analysis_query = adapter.case_collection.aggregate([
        {'$unwind': '$individuals'},
        {'$group': {'_id': '$individuals.analysis_type', 'count': {'$sum': 1}}}
    ])
    analysis_types = [{'name': group['_id'], 'count': group['count']} for group in analysis_query]
    
    data['analysis_types'] = analysis_types

    phenotype_cases = sum(1 for i in adapter.case(phenotype_terms=True, institute_id=institute_id))
    causative_cases = sum(1 for i in adapter.case(has_causatives=True, institute_id=institute_id))
    pinned_cases = sum(1 for i in adapter.cases.find(pinned=True, institute_id=institute_id))
    cohort_cases = sum(1 for i in adapter.cases.find(cohort=True, institute_id=institute_id))
    
    LOG.info("Fetch sanger variants")
    sanger_query = {'sanger_ordered': True}
    if institute_id:
        sanger_query['institute_id'] = institute_id

    sanger_cases = set()
    sanger_validated_cases = set()
    sanger_validated_tp = set()
    sanger_validated_fp = set()

    sanger_ordered = adapter.variant_collection.find(sanger_query)

    for variant in sanger_ordered:
        case_id = variant['case_id']
        sanger_cases.add(case_id)
        validation = variant.get('validation')
        if validation == 'True positive':
            sanger_validated_tp.add(case_id)
            sanger_validated_cases.add(case_id)
        elif validation == 'False positive':
            sanger_validated_fp.add(case_id)
            sanger_validated_cases.add(case_id)

    sanger_ordered = len(sanger_cases)
    
    overview = [
        {
            'title': 'Phenotype terms',
            'count': phenotype_cases,
            'percent': phenotype_cases / total_cases,
        }, 
        {
            'title': 'Causative variants',
            'count': causative_cases,
            'percent': causative_cases / total_cases,
        }, 
        {
            'title': 'Pinned variants',
            'count': pinned_cases,
            'percent': pinned_cases / total_cases,
        }, 
        {
            'title': 'Cohort tag',
            'count': cohort_cases,
            'percent': cohort_cases / total_cases,
        },
        {
            'title': 'Validation ordered',
            'count': len(sanger_cases),
            'percent': len(sanger_cases) / total_cases,
        },
        {
            'title': 'Validated',
            'count': len(sanger_validated_cases),
            'percent': len(sanger_validated_cases) / total_cases,
        },
        {
            'title': 'Validated True Positive',
            'count': len(sanger_validated_cases),
            'percent': len(sanger_validated_cases) / total_cases,
        },
        {
            'title': 'Validated False Positive',
            'count': len(sanger_validated_cases),
            'percent': len(sanger_validated_cases) / total_cases,
        },
    ]

    return data