ANALYSIS_TYPES = ('wgs', 'wes', 'mixed', 'unknown')

SEX_MAP = {1: 'male', 2: 'female', 'other': 'unknown', 0: 'unknown', 
          '1': 'male', '2': 'female', '0': 'unknown'}
REV_SEX_MAP = {'male':'1', 'female': '2', 'unknown': '0'}

PHENOTYPE_MAP = {1: 'unaffected', 2: 'affected', 0: 'unknown', -9: 'unknown'}
REV_PHENOTYPE_MAP = {value: key for key, value in PHENOTYPE_MAP.items()}


CASE_STATUSES = ("prioritized", "inactive", "active", "solved", "archived")
