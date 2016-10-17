# -*- coding: utf-8 -*-
from .hgnc import parse_hgnc_genes
from .panel import parse_gene_panel
from .ids import parse_ids
from .callers import parse_callers
from .conservation import parse_conservations
from .frequency import parse_frequencies
from .genotype import parse_genotypes
from .omim import (get_omim_gene_ids, get_omim_phenotype_ids)
from .transcript import (parse_transcripts, parse_disease_associated)
from .gene import parse_genes
from .compound import parse_compounds
from .clnsig import get_clnsig
from .case import (parse_individual,parse_case)
from .variant import parse_variant
