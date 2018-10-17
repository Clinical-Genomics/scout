import logging

LOG = logging.getLogger(__name__)

def get_case_info(adapter, total_cases, institute_id=None):
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

    phenotype_cases = adapter.case(phenotype_terms=True, institute_id=institute_id)
    causative_cases = adapter.case(has_causatives=True, institute_id=institute_id)
    pinned_cases = adapter.cases.find(pinned=True, institute_id=institute_id)
    cohort_cases = adapter.cases.find(cohort=True, institute_id=institute_id)
    
    LOG.info("Fetch sanger variants")
    nr_evaluated = adapter.variant_collection.find({'validation': {'$exists':True, '$ne': "Not validated"}}).count()
    
    LOG.info("Fetch sanger events")
    sanger_cases = store.event_collection.distinct('case', {'verb':'sanger'})
    LOG.info("Sanger events fetched")
    
    sanger_ordered = len(sanger_cases)
    
    overview = [
        {
            'title': 'Phenotype terms',
            'count': phenotype_terms,
            'percent': phenotype_cases / total_cases,
        }, 
        {
            'title': 'Causative variants',
            'count': causative_variants,
            'percent': causative_cases / total_cases,
        }, 
        {
            'title': 'Pinned variants',
            'count': pinned_variants,
            'percent': pinned_cases / total_cases,
        }, 
        {
            'title': 'Cohort tag',
            'count': cohort_tags,
            'percent': cohort_cases / total_cases,
        },
        {
            'title': 'Sanger ordered',
            'count': sanger_ordered,
            'percent': sanger_ordered / total_cases,
        },
        {
            'title': 'Sanger confirmed',
            'count': nr_evaluated,
            'percent': nr_evaluated / total_cases,
        },
    ]
    
    
    
    
    return data