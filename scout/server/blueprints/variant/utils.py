import logging

from scout.constants import (CLINSIG_MAP, CALLERS, ACMG_COMPLETE_MAP)
from scout.server.links import (add_gene_links, ensembl, add_tx_links)

LOG = logging.getLogger(__name__)

def transcript_str(transcript_obj, gene_name=None):
    """Generate amino acid change as a string."""
    if transcript_obj.get('exon'):
        gene_part, part_count_raw = 'exon', transcript_obj['exon']
    elif transcript_obj.get('intron'):
        gene_part, part_count_raw = 'intron', transcript_obj['intron']
    else:
        # variant between genes
        gene_part, part_count_raw = 'intergenic', '0'

    part_count = part_count_raw.rpartition('/')[0]
    change_str = "{}:{}{}:{}:{}".format(
        transcript_obj.get('refseq_id', ''),
        gene_part,
        part_count,
        transcript_obj.get('coding_sequence_name', 'NA'),
        transcript_obj.get('protein_sequence_name', 'NA'),
    )
    if gene_name:
        change_str = "{}:".format(gene_name) + change_str
    return change_str


def evaluation(store, evaluation_obj):
    """Fetch and fill-in evaluation object."""
    evaluation_obj['institute'] = store.institute(evaluation_obj['institute_id'])
    evaluation_obj['case'] = store.case(evaluation_obj['case_id'])
    evaluation_obj['variant'] = store.variant(evaluation_obj['variant_specific'])
    evaluation_obj['criteria'] = {criterion['term']: criterion for criterion in
                                  evaluation_obj['criteria']}
    evaluation_obj['classification'] = ACMG_COMPLETE_MAP.get(evaluation_obj['classification'])
    return evaluation_obj

def parse_gene(gene_obj, build=None):
    """Parse variant genes."""
    build = build or 37

    if gene_obj.get('common'):
        add_gene_links(gene_obj, build)
        refseq_transcripts = []
        for tx_obj in gene_obj['transcripts']:
            parse_transcript(gene_obj, tx_obj, build)

            # select refseq transcripts as "primary"
            if not tx_obj.get('refseq_id'):
                continue

            refseq_transcripts.append(tx_obj)

        gene_obj['primary_transcripts'] = (refseq_transcripts if refseq_transcripts else [])

def parse_transcript(gene_obj, tx_obj, build=None):
    """Parse variant gene transcript (VEP)."""
    build = build or 37
    add_tx_links(tx_obj, build)

    if tx_obj.get('refseq_id'):
        gene_name = (gene_obj['common']['hgnc_symbol'] if gene_obj['common'] else
                     gene_obj['hgnc_id'])
        tx_obj['change_str'] = transcript_str(tx_obj, gene_name)


def frequency(variant_obj):
    """Returns a judgement on the overall frequency of the variant.

    Combines multiple metrics into a single call.
    
    Args:
        variant_obj(scout.models.Variant)
    
    Returns:
        str in ['common','uncommon','rare']
    """
    most_common_frequency = max(variant_obj.get('thousand_genomes_frequency') or 0,
                                variant_obj.get('exac_frequency') or 0,
                                variant_obj.get('gnomad_frequency') or 0
                                )

    if most_common_frequency > .05:
        return 'common'
    if most_common_frequency > .01:
        return 'uncommon'
    
    return 'rare'


def end_position(variant_obj):
    """Calculate end position for a variant.
    
    Args:
        variant_obj(scout.models.Variant)
    
    Returns:
        end_position(int)
    """
    alt_bases = len(variant_obj['alternative'])
    num_bases = max(len(variant_obj['reference']), alt_bases)
    return variant_obj['position'] + (num_bases - 1)

def default_panels(store, case_obj):
    """Return the panels that are decided to be default for a case.
    
    Check what panels that are default, fetch those and add them to a list.
    
    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(scout.models.Case)
    
    Returns:
        default_panels(list(dict))
        
    """
    default_panels = []
    # Add default panel information to variant
    for panel in case_obj.get('panels',[]):
        if not panel.get('is_default'):
            continue
        panel_obj = store.gene_panel(panel['panel_name'], panel.get('version'))
        if not panel_obj:
            LOG.warning("Panel {0} version {1} could not be found".format(
                panel['panel_name'], panel.get('version')))
            continue
        default_panels.append(panel_obj)
    return default_panels

def update_hgncsymbol(variant_obj):
    """Check if the HGNC symbols have changed since the variant was loaded"""
    pass

def clinsig_human(variant_obj):
    """Convert to human readable version of CLINSIG evaluation.
    
    The clinical significance from ACMG are stored as numbers. These needs to be converted to human 
    readable format. Also the link to the accession is built
    
    Args:
        variant_obj(scout.models.Variant)
    
    Yields:
        clinsig_objs(dict): {
                                'human': str,
                                'link': str
                            }
    
    """
    for clinsig_obj in variant_obj['clnsig']:
        # The clinsig objects allways have a accession
        if not 'accession' in clinsig_obj:
            continue
        # Old version
        link = "https://www.ncbi.nlm.nih.gov/clinvar/{}"
        if isinstance(clinsig_obj['accession'], int):
            # New version
            link = "https://www.ncbi.nlm.nih.gov/clinvar/variation/{}"

        human_str = 'not provided'
        clnsig_value = clinsig_obj.get('value')
        if clnsig_value:
            try:
                # Old version
                int(clinsig_value)
                human_str = CLINSIG_MAP.get(clinsig_value, 'not provided')
            except ValueError:
                # New version
                human_str = clinsig_value

        clinsig_obj['human'] = human_str
        clinsig_obj['link'] = link.format(clinsig_obj['accession'])

        yield clinsig_obj

def callers(variant_obj, category='snv'):
    """Return info about callers.
    
    Args:
        variant_obj(scout.models.Variant)
        category(str)
    
    Returns:
        calls(list(str)): A list of the callers that identified the variant
    """
    calls = set()
    for caller in CALLERS[category]:
        if variant_obj.get(caller['id']):
            calls.add((caller['name'], variant_obj[caller['id']]))

    return list(calls)
