import logging

LOG = logging.getLogger(__name__)

def parse_clnsig(variant, transcripts=None):
    """Get the clnsig information

    Args:
        variant(cyvcf2.Variant)
        acc(str): The clnsig accession number, raw from vcf
        sig(str): The clnsig significance score, raw from vcf
        revstat(str): The clnsig revstat, raw from vcf
        transcripts(iterable(dict))

    Returns:
        clnsig_accsessions(list(dict)): A list with clnsig accessions
    """
    LOG.debug("Parsing ")
    acc = variant.INFO.get('CLNACC', variant.INFO.get('CLNVID',''))
    sig = variant.INFO.get('CLNSIG', '').lower()
    revstat = variant.INFO.get('CLNREVSTAT','').lower()
    
    clnsig_accsessions = []

    # There are some versions where clinvar uses integers to represent terms
    if acc.isdigit():
        revstat_groups = []
        if revstat:
            revstat_groups = [rev.lstrip('_') for rev in revstat.split(',')]

        sig_groups = []
        for significance in sig.split(','):
            for term in significance.lstrip('_').split('/'):
                sig_groups.append('_'.join(term.split(' ')))

        for sig_term in sig_groups:
            clnsig_accsessions.append({
                'value': sig_term,
                'accession': int(acc),
                'revstat': ','.join(revstat_groups),
            })
    if not clnsig_accsessions and acc:
    # This is the 'old' clinvar format
        acc_groups = acc.split('|')
        sig_groups = sig.split('|')
        revstat_groups = revstat.split('|')
        for acc_group, sig_group, revstat_group in zip(acc_groups, sig_groups, revstat_groups):
            accessions = acc_group.split(',')
            significances = sig_group.split(',')
            revstats = revstat_group.split(',')
            for accession, significance, revstat in zip(accessions, significances, revstats):
                clnsig_accsessions.append({
                    'value': int(significance),
                    'accession': accession,
                    'revstat': revstat,
                })

    if not clnsig_accsessions and transcripts:
        clnsig = set()
        for transcript in transcripts:
            for annotation in transcript.get('clnsig', []):
                clnsig.add(annotation)
        for annotation in clnsig:
            clnsig_accsessions.append({'value': annotation})

    return clnsig_accsessions
