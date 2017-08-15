import logging

from scout.constants import REV_CLINSIG_MAP

logger = logging.getLogger(__name__)


def parse_clnsig(acc, sig, revstat, transcripts):
    """Get the clnsig information

    Args:
        acc(str): The clnsig accession number, raw from vcf
        sig(str): The clnsig significance score, raw from vcf
        revstat(str): The clnsig revstat, raw from vcf
        transcripts(iterable(dict))

    Returns:
        clnsig_accsessions(list): A list with clnsig accessions
    """
    clnsig_accsessions = []
    if acc:
        # There are sometimes different separators so we need to check which
        # one to use
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

    elif transcripts:
        clnsig = set()
        for transcript in transcripts:
            for annotation in transcript.get('clinsig', []):
                clnsig.add(annotation)
        for annotation in clnsig:
            if annotation in REV_CLINSIG_MAP:
                clnsig_accsessions.append({'value': REV_CLINSIG_MAP[annotation]})

    return clnsig_accsessions
