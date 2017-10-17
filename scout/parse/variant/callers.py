from scout.constants import CALLERS


def parse_callers(variant):
    """Parse how the different variant callers have performed

        Args:
            variant(dict): A variant dictionary

        Returns:
            callers(dict): A dictionary on the form
            {'gatk': <filter>,'freebayes': <filter>,'samtools': <filter>}
    """
    relevant_callers = CALLERS['sv' if variant.var_type == 'sv' else 'snv']
    callers = {caller['id']: None for caller in relevant_callers}
    raw_info = variant.INFO.get('set')
    if raw_info:
        info = raw_info.split('-')
        for call in info:
            if call == 'FilteredInAll':
                for caller in callers:
                    callers[caller] = 'Filtered'
            elif call == 'Intersection':
                for caller in callers:
                    callers[caller] = 'Pass'
            elif 'filterIn' in call:
                for caller in callers:
                    if caller in call:
                        callers[caller] = 'Filtered'

            elif call in set(callers.keys()):
                callers[call] = 'Pass'
    # The following is parsing of a custom made merge
    other_info = variant.INFO.get('FOUND_IN')
    if other_info:
        for info in other_info.split(','):
            called_by = info.split('|')[0]
            callers[called_by] = 'Pass'

    return callers
