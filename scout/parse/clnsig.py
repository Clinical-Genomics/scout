import logging

logger = logging.getLogger(__name__)
def get_clnsig(variant):
    """Get the clnsig information

        We are only interested when clnsig = 5. So for each 5 we return the
        CLNSIG accesson number.

        Args:
            variant (dict): A Variant dictionary

        Returns:
            clnsig_accsessions(list)
    """
    clnsig_key = 'SnpSift_CLNSIG'
    accession_key = 'SnpSift_CLNACC'
    clnsig_annotation = variant['info_dict'].get(clnsig_key)
    accession_annotation = variant['info_dict'].get(accession_key)

    clnsig_accsessions = []
    if clnsig_annotation:
        clnsig_annotation = clnsig_annotation[0].split('|')
        logger.debug("Found clnsig annotations {0}".format(
            ', '.join(clnsig_annotation)))
        try:
            accession_annotation = (accession_annotation or [])[0].split('|')
            for index, entry in enumerate(clnsig_annotation):
                if int(entry) == 5:
                    if accession_annotation:
                        clnsig_accsessions.append(accession_annotation[index])
        except (ValueError, IndexError):
            pass

    return clnsig_accsessions
