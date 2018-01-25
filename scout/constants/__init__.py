# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

from intervaltree import (IntervalTree, Interval)

from scout.parse.cytoband import parse_cytoband
from scout.resources import cytobands_path
from scout.utils.handle import get_file_handle

from .indexes import INDEXES

from .acmg import (ACMG_COMPLETE_MAP, ACMG_OPTIONS, ACMG_CRITERIA, ACMG_MAP, REV_ACMG_MAP)
from .so_terms import (SO_TERMS, SO_TERM_KEYS, SEVERE_SO_TERMS)
from .variant_tags import (CONSEQUENCE, CONSERVATION, FEATURE_TYPES, SV_TYPES, SPIDEX_LEVELS,
                           GENETIC_MODELS, VARIANT_CALL, MANUAL_RANK_OPTIONS)
from .case_tags import (ANALYSIS_TYPES, SEX_MAP, REV_SEX_MAP, PHENOTYPE_MAP,
                        REV_PHENOTYPE_MAP, CASE_STATUSES)
from .clnsig import (CLINSIG_MAP, REV_CLINSIG_MAP)
from .phenotype import (PHENOTYPE_GROUPS, COHORT_TAGS)

cytobands_handle = get_file_handle(cytobands_path)

CYTOBANDS = parse_cytoband(cytobands_handle)

PAR_COORDINATES = {
    '37': {
        'X': IntervalTree([Interval(60001, 2699521, 'par1'),
                           Interval(154931044, 155260561, 'par2')]),
        'Y': IntervalTree([Interval(10001, 2649521, 'par1'),
                           Interval(59034050, 59363567, 'par2')])
    },
    '38': {
        'X': IntervalTree([Interval(10001, 2781480, 'par1'),
                           Interval(155701383, 156030896, 'par2')]),
        'Y': IntervalTree([Interval(10001, 2781480, 'par1'),
                           Interval(56887903, 57217416, 'par2')])
    },
}

CALLERS = {
    'snv': [{
        'id': 'gatk',
        'name': 'GATK',
    }, {
        'id': 'freebayes',
        'name': 'Freebayes',
    }, {
        'id': 'samtools',
        'name': 'SAMtools',
    }, {
        'id': 'mutect',
        'name': 'MuTect',
    }, {
        'id': 'pindel',
        'name': 'Pindel',
    }],
    'sv': [{
        'id': 'cnvnator',
        'name': 'CNVnator',
    }, {
        'id': 'delly',
        'name': 'Delly',
    }, {
        'id': 'tiddit',
        'name': 'TIDDIT',
    }, {
        'id': 'manta',
        'name': 'Manta',
    }]
}

BND_ALT_PATTERN = re.compile(r".*[\],\[](.*?):(.*?)[\],\[]")
CHR_PATTERN = re.compile(r'(chr)?(.*)', re.IGNORECASE)

