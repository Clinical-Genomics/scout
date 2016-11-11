
def parse_callers(variant):
    """Parse how the different variant callers have performed
    
        Args:
            variant(dict): A variant dictionary
    
        Returns:
            callers(dict): A dictionary on the form 
            {'gatk': <filter>,'freebayes': <filter>,'samtools': <filter>}
    """
    callers = {
        'gatk': None,
        'freebayes': None,
        'samtools': None
    }
    raw_info = variant['info_dict'].get('set')
    if raw_info:
        info = raw_info[0].split('-')
        for call in info:
            if call == 'FilteredInAll':
                callers['gatk'] = 'Filtered'
                callers['samtools'] = 'Filtered'
                callers['freebayes'] = 'Filtered'
            elif call == 'Intersection':
                callers['gatk'] = 'Pass'
                callers['samtools'] = 'Pass'
                callers['freebayes'] = 'Pass'
            elif 'filterIn' in call:
                if 'gatk' in call:
                    callers['gatk'] = 'Filtered'
                if 'samtools' in call:
                    callers['samtools'] = 'Filtered'
                if 'freebayes' in call:
                    callers['freebayes'] = 'Filtered'
            elif call in ['gatk', 'samtools', 'freebayes']:
                callers[call] = 'Pass'
    return callers
