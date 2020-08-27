"""
Methods for parsing HPO terms extracted from the following files:
http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/util/annotation/genes_to_phenotype.txt
http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/util/annotation/phenotype_to_genes.txt
"""
import logging

LOG = logging.getLogger(__name__)


def parse_hpo_to_genes(lines):
    """Parse the map from hpo term to hgnc symbol

    Args:
        lines(iterable(str)): example:
        #Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol\
        <tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
        HP:0000002	Abnormality of body height	3954	LETM1	-	mim2gene	OMIM:194190
        HP:0000002	Abnormality of body height	197131	UBR1	-	mim2gene	OMIM:243800
        HP:0000002	Abnormality of body height	79633	FAT4		orphadata	ORPHA:314679

    Yields:
        hpo_to_gene(dict): A dictionary with information on how a term map to a hgnc symbol
    """
    for line in lines:
        if line.startswith("#") or len(line) < 5:
            continue
        line = line.rstrip().split("\t")
        hpo_id = line[0]
        hgnc_symbol = line[3]

        yield {"hpo_id": hpo_id, "hgnc_symbol": hgnc_symbol}


def parse_hpo_diseases(hpo_lines):
    """Parse hpo disease phenotypes

            Args:
                lines(iterable(str)): example:
                #Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol\
                <tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
                HP:0000002	Abnormality of body height	3954	LETM1	-	mim2gene	OMIM:194190
                HP:0000002	Abnormality of body height	197131	UBR1	-	mim2gene	OMIM:243800
                HP:0000002	Abnormality of body height	79633	FAT4		orphadata	ORPHA:314679

        Returns:
            diseases(dict): A dictionary with mim numbers as keys
    """
    diseases = {}
    LOG.info("Parsing hpo diseases...")
    for index, line in enumerate(hpo_lines):
        # First line is a header
        if index == 0:
            continue
        # Skip empty lines
        if not len(line) > 3:
            continue
        # Parse the info
        disease_info = parse_hpo_disease(line)
        # Skip the line if there where no info
        if not disease_info:
            continue
        disease_nr = disease_info.get("disease_nr")
        hgnc_symbol = disease_info.get("hgnc_symbol")
        hpo_term = disease_info.get("hpo_term")
        source = disease_info.get("source")
        disease_id = "{0}:{1}".format(source, disease_nr)

        if disease_id not in diseases:
            diseases[disease_id] = {
                "disease_nr": disease_nr,
                "source": source,
                "hgnc_symbols": set(),
                "hpo_terms": set(),
            }

        if hgnc_symbol:
            diseases[disease_id]["hgnc_symbols"].add(hgnc_symbol)
        if hpo_term:
            diseases[disease_id]["hpo_terms"].add(hpo_term)

    LOG.info("Parsing done.")
    return diseases


def parse_hpo_disease(hpo_line):
    """Parse hpo disease line

        Args:
            hpo_line(str) a line with the following formatting:

            #Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol\
            <tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
            HP:0000002	Abnormality of body height	3954	LETM1	-	mim2gene	OMIM:194190
            HP:0000002	Abnormality of body height	197131	UBR1	-	mim2gene	OMIM:243800
            HP:0000002	Abnormality of body height	79633	FAT4		orphadata	ORPHA:314679
    """

    hpo_line = hpo_line.rstrip().split("\t")
    hpo_info = {}
    gd_source = hpo_line[5]  # mim2gene or orphadata
    if gd_source == "orphadata":
        return

    disease = hpo_line[6].split(":")

    hpo_info["source"] = disease[0]
    hpo_info["disease_nr"] = int(disease[1])
    hpo_info["hgnc_symbol"] = None
    hpo_info["hpo_term"] = None

    if len(hpo_line) >= 3:
        hpo_info["hgnc_symbol"] = hpo_line[3]

        if len(hpo_line) >= 4:
            hpo_info["hpo_term"] = hpo_line[0]

    return hpo_info
