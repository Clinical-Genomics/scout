import logging

from pprint import pprint as pp

from scout.utils.md5 import generate_md5_key
from .genotype import parse_genotypes
from .compound import parse_compounds
from .clnsig import parse_clnsig
from .gene import parse_genes
from .frequency import (parse_frequencies, parse_sv_frequencies)
from .conservation import parse_conservations
from .ids import parse_ids
from .callers import parse_callers
from .rank_score import parse_rank_score
from .coordinates import parse_coordinates
from .models import parse_genetic_models
from .transcript import parse_transcripts
from .deleteriousness import parse_cadd

from scout.constants import CHR_PATTERN

from scout.exceptions import VcfError

logger = logging.getLogger(__name__)

def parse_variant(variant, case, variant_type='clinical',
                 rank_results_header=None, vep_header=None,
                 individual_positions=None, category=None):
    """Return a parsed variant

        Get all the necessary information to build a variant object

    Args:
        variant(cyvcf2.Variant)
        case(dict)
        variant_type(str): 'clinical' or 'research'
        rank_results_header(list)
        vep_header(list)
        individual_positions(dict): Explain what position each individual has
                                    in vcf
        category(str): 'snv', 'sv', 'str' or 'cancer'

    Returns:
        parsed_variant(dict): Parsed variant
    """
    # These are to display how the rank score is built
    rank_results_header = rank_results_header or []
    # Vep information
    vep_header = vep_header or []

    parsed_variant = {}

    # Create the ID for the variant
    case_id = case['_id']
    if '-' in case_id:
        logger.debug('internal case id detected')
        genmod_key = case['display_name']
    else:
        genmod_key = case['_id']

    chrom_match = CHR_PATTERN.match(variant.CHROM)
    chrom = chrom_match.group(2)

    # Builds a dictionary with the different ids that are used

    if variant.ALT:
        alt=variant.ALT[0]
    elif not variant.ALT and category == "str":
        alt='.'

    parsed_variant['ids'] = parse_ids(
        chrom=chrom,
        pos=variant.POS,
        ref=variant.REF,
        alt=alt,
        case_id=case_id,
        variant_type=variant_type,
    )
    parsed_variant['case_id'] = case_id
    # type can be 'clinical' or 'research'
    parsed_variant['variant_type'] = variant_type
    # category is sv or snv
    # cyvcf2 knows if it is a sv, indel or snv variant
    if not category:
        category = variant.var_type
        if category == 'indel':
            category = 'snv'
        if category == 'snp':
            category = 'snv'

    parsed_variant['category'] = category

    ################# General information #################

    parsed_variant['reference'] = variant.REF

    ### We allways assume splitted and normalized vcfs!!!
    if len(variant.ALT) > 1:
        raise VcfError("Variants are only allowed to have one alternative")
    parsed_variant['alternative'] = alt

    # cyvcf2 will set QUAL to None if '.' in vcf
    parsed_variant['quality'] = variant.QUAL

    if variant.FILTER:
        parsed_variant['filters'] = variant.FILTER.split(';')
    else:
        parsed_variant['filters'] = ['PASS']

    # Add the dbsnp ids
    parsed_variant['dbsnp_id'] = variant.ID

    # This is the id of other position in translocations
    # (only for specific svs)
    parsed_variant['mate_id'] = None

    ################# Position specific #################
    parsed_variant['chromosome'] = chrom

    coordinates = parse_coordinates(variant, category)

    parsed_variant['position'] = coordinates['position']
    parsed_variant['sub_category'] = coordinates['sub_category']
    parsed_variant['mate_id'] = coordinates['mate_id']
    parsed_variant['end'] = coordinates['end']
    parsed_variant['length'] = coordinates['length']
    parsed_variant['end_chrom'] = coordinates['end_chrom']
    parsed_variant['cytoband_start'] = coordinates['cytoband_start']
    parsed_variant['cytoband_end'] = coordinates['cytoband_end']

    ################# Add rank score #################
    # The rank score is central for displaying variants in scout.

    rank_score = parse_rank_score(variant.INFO.get('RankScore', ''), genmod_key)
    parsed_variant['rank_score'] = rank_score or 0


    ################# Add gt calls #################
    if individual_positions and case['individuals']:
        parsed_variant['samples'] = parse_genotypes(variant, case['individuals'],
                                                    individual_positions)
    else:
        parsed_variant['samples'] = []

    ################# Add compound information #################
    compounds = parse_compounds(compound_info=variant.INFO.get('Compounds'),
                                case_id=genmod_key,
                                variant_type=variant_type)
    if compounds:
        parsed_variant['compounds'] = compounds

    ################# Add inheritance patterns #################

    genetic_models = parse_genetic_models(variant.INFO.get('GeneticModels'), genmod_key)
    if genetic_models:
        parsed_variant['genetic_models'] = genetic_models

    ################# Add autozygosity calls if present #################

    azlength = variant.INFO.get('AZLENGTH')
    if azlength:
        parsed_variant['azlength'] = int(azlength)

    azqual = variant.INFO.get('AZQUAL')
    if azqual:
        parsed_variant['azqual'] = float(azqual)

    ################ Add STR info if present ################

    # repeat id generally corresponds to gene symbol
    repeat_id = variant.INFO.get('REPID')
    if repeat_id:
        parsed_variant['str_repid'] = str(repeat_id)

    # repeat unit - used e g in PanelApp naming of STRs
    repeat_unit = variant.INFO.get('RU')
    if repeat_unit:
        parsed_variant['str_ru'] = str(repeat_unit)

    # repeat ref - reference copy number
    repeat_ref = variant.INFO.get('REF')
    if repeat_ref:
        parsed_variant['str_ref'] = int(repeat_ref)

    # repeat len - number of repeats found in case
    repeat_len = variant.INFO.get('RL')
    if repeat_len:
        parsed_variant['str_len'] = int(repeat_len)

    # str status - this indicates the severity of the expansion level
    str_status = variant.INFO.get('STR_STATUS')
    if str_status:
        parsed_variant['str_status'] = str(str_status)

    ################# Add gene and transcript information #################
    raw_transcripts = []
    if vep_header:
        vep_info = variant.INFO.get('CSQ')
        if vep_info:
            raw_transcripts = (dict(zip(vep_header, transcript_info.split('|')))
                               for transcript_info in vep_info.split(','))

    parsed_transcripts = []
    dbsnp_ids = set()
    cosmic_ids = set()
    for parsed_transcript in parse_transcripts(raw_transcripts, parsed_variant['alternative']):
        parsed_transcripts.append(parsed_transcript)
        for dbsnp in parsed_transcript.get('dbsnp', []):
            dbsnp_ids.add(dbsnp)
        for cosmic in parsed_transcript.get('cosmic', []):
            cosmic_ids.add(cosmic)

    # The COSMIC tag in INFO is added via VEP and/or bcftools annotate

    cosmic_tag = variant.INFO.get('COSMIC')
    if cosmic_tag:
        cosmic_ids.add(cosmic_tag[4:])

    if (dbsnp_ids and not parsed_variant['dbsnp_id']):
        parsed_variant['dbsnp_id'] = ';'.join(dbsnp_ids)

    if cosmic_ids:
        parsed_variant['cosmic_ids'] = list(cosmic_ids)

    gene_info = parse_genes(parsed_transcripts)

    parsed_variant['genes'] = gene_info

    hgnc_ids = set([])

    for gene in parsed_variant['genes']:
        hgnc_ids.add(gene['hgnc_id'])

    parsed_variant['hgnc_ids'] = list(hgnc_ids)

    ################# Add clinsig prediction #################
    if variant.INFO.get('CLNACC'):
        acc = variant.INFO.get('CLNACC')
    else:
        acc = variant.INFO.get('CLNVID')
    clnsig_predictions = parse_clnsig(
        acc=acc,
        sig=variant.INFO.get('CLNSIG'),
        revstat=variant.INFO.get('CLNREVSTAT'),
        transcripts=parsed_transcripts
        )

    if clnsig_predictions:
        parsed_variant['clnsig'] = clnsig_predictions

    ################# Add the frequencies #################
    frequencies = parse_frequencies(variant, parsed_transcripts)

    parsed_variant['frequencies'] = frequencies

    # parse out old local observation count
    local_obs_old = variant.INFO.get('Obs')
    if local_obs_old:
        parsed_variant['local_obs_old'] = int(local_obs_old)

    local_obs_hom_old = variant.INFO.get('Hom')
    if local_obs_hom_old:
        parsed_variant['local_obs_hom_old'] = int(local_obs_hom_old)

    ###################### Add severity predictions ######################
    cadd = parse_cadd(variant, parsed_transcripts)
    if cadd:
        parsed_variant['cadd_score'] = cadd

    spidex = variant.INFO.get('SPIDEX')
    if spidex:
        parsed_variant['spidex'] = float(spidex)

    ###################### Add conservation ######################

    parsed_variant['conservation'] = parse_conservations(variant)

    parsed_variant['callers'] = parse_callers(variant, category=category)

    rank_result = variant.INFO.get('RankResult')
    if rank_result:
        results = [int(i) for i in rank_result.split('|')]
        parsed_variant['rank_result'] = dict(zip(rank_results_header, results))

    ###################### Add SV specific annotations ######################
    sv_frequencies = parse_sv_frequencies(variant)
    for key in sv_frequencies:
        parsed_variant['frequencies'][key] = sv_frequencies[key]

    ###################### Add Cancer specific annotations ######################
    # MSK_MVL indicates if variants are in the MSK managed variant list
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5437632/
    mvl_tag = variant.INFO.get('MSK_MVL')
    if mvl_tag:
        parsed_variant['mvl_tag'] = True

    return parsed_variant
