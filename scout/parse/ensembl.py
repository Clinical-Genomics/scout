"""Code for parsing ensembl information"""
import logging

LOG = logging.getLogger(__name__)


def parse_ensembl_line(line, header):
    """Parse an ensembl formated line

    This parser should be able to handle any ensembl formated line in tsv format, regardless if
    it is exons, transcripts or genes.

    Args:
        line(list): A list with ensembl gene info
        header(list): A list with the header info

    Returns:
        ensembl_info(dict): A dictionary with the relevant info
    """
    line = line.rstrip().split("\t")
    header = [head.lower() for head in header]
    raw_info = dict(zip(header, line))

    ensembl_info = {}

    for word in raw_info:
        value = raw_info[word]

        if not value:
            continue

        if "chromosome" in word:
            ensembl_info["chrom"] = value

        if "gene" in word:
            if "id" in word:
                ensembl_info["ensembl_gene_id"] = value
            elif "start" in word:
                ensembl_info["gene_start"] = int(value)
            elif "end" in word:
                ensembl_info["gene_end"] = int(value)

        if "hgnc symbol" in word:
            ensembl_info["hgnc_symbol"] = value
        if "gene name" in word:
            ensembl_info["hgnc_symbol"] = value

        if "hgnc id" in word:
            ensembl_info["hgnc_id"] = int(value.split(":")[-1])

        if "transcript" in word:
            if "id" in word:
                ensembl_info["ensembl_transcript_id"] = value
            elif "start" in word:
                ensembl_info["transcript_start"] = int(value)
            elif "end" in word:
                ensembl_info["transcript_end"] = int(value)

        if "exon" in word:
            if "start" in word:
                ensembl_info["exon_start"] = int(value)
            elif "end" in word:
                ensembl_info["exon_end"] = int(value)
            elif "id" in word:
                ensembl_info["ensembl_exon_id"] = value
            elif "rank" in word:
                ensembl_info["exon_rank"] = int(value)

        if "utr" in word:

            if "start" in word:
                if "5" in word:
                    ensembl_info["utr_5_start"] = int(value)
                elif "3" in word:
                    ensembl_info["utr_3_start"] = int(value)
            elif "end" in word:
                if "5" in word:
                    ensembl_info["utr_5_end"] = int(value)
                elif "3" in word:
                    ensembl_info["utr_3_end"] = int(value)

        if "strand" in word:
            ensembl_info["strand"] = int(value)

        if "refseq" in word:
            if "mrna" in word:
                if "predicted" in word:
                    ensembl_info["refseq_mrna_predicted"] = value
                else:
                    ensembl_info["refseq_mrna"] = value

            if "ncrna" in word:
                ensembl_info["refseq_ncrna"] = value

    return ensembl_info


def parse_transcripts(transcript_lines):
    """Parse and massage the transcript information

    There could be multiple lines with information about the same transcript.
    This is why it is necessary to parse the transcripts first and then return a dictionary
    where all information has been merged.

    Args:
        transcript_lines(): Iterable with strings

    Returns:
        parsed_transcripts(dict): Map from enstid -> transcript info
    """
    LOG.info("Parsing transcripts")
    transcripts = parse_ensembl_transcripts(transcript_lines)

    # Since there can be multiple lines with information about the same transcript
    # we store transcript information in a dictionary for now
    parsed_transcripts = {}
    # Loop over the parsed transcripts
    for tx in transcripts:
        tx_id = tx["ensembl_transcript_id"]
        ens_gene_id = tx["ensembl_gene_id"]

        # Check if the transcript has been added
        # If not, create a new transcript
        if not tx_id in parsed_transcripts:
            tx_info = {
                "chrom": tx["chrom"],
                "transcript_start": tx["transcript_start"],
                "transcript_end": tx["transcript_end"],
                "mrna": set(),
                "mrna_predicted": set(),
                "nc_rna": set(),
                "ensembl_gene_id": ens_gene_id,
                "ensembl_transcript_id": tx_id,
            }
            parsed_transcripts[tx_id] = tx_info

        tx_info = parsed_transcripts[tx_id]
        # Add the ref seq information
        if tx.get("refseq_mrna_predicted"):
            tx_info["mrna_predicted"].add(tx["refseq_mrna_predicted"])
        if tx.get("refseq_mrna"):
            tx_info["mrna"].add(tx["refseq_mrna"])
        if tx.get("refseq_ncrna"):
            tx_info["nc_rna"].add(tx["refseq_ncrna"])

    return parsed_transcripts


def parse_ensembl_genes(lines):
    """Parse lines with ensembl formated genes

    This is designed to take a biomart dump with genes from ensembl.
    Mandatory columns are:
    'Gene ID' 'Chromosome' 'Gene Start' 'Gene End' 'HGNC symbol'

    Args:
        lines(iterable(str)): An iterable with ensembl formated genes
    Yields:
        ensembl_gene(dict): A dictionary with the relevant information
    """
    LOG.info("Parsing ensembl genes from file")
    header = []
    for index, line in enumerate(lines):

        # File allways start with a header line
        if index == 0:
            header = line.rstrip().split("\t")
            continue
        # After that each line represents a gene

        yield parse_ensembl_line(line, header)


def parse_ensembl_transcripts(lines):
    """Parse lines with ensembl formated transcripts

    This is designed to take a biomart dump with transcripts from ensembl.
    Mandatory columns are:
    'Gene ID' 'Transcript ID' 'Transcript Start' 'Transcript End' 'RefSeq mRNA'

    Args:
        lines(iterable(str)): An iterable with ensembl formated genes
    Yields:
        ensembl_transcript(dict): A dictionary with the relevant information
    """
    header = []
    LOG.info("Parsing ensembl transcripts from file")
    for index, line in enumerate(lines):

        # File allways start with a header line
        if index == 0:
            header = line.rstrip().split("\t")
        # After that each line represents a transcript
        else:
            yield parse_ensembl_line(line, header)


def parse_ensembl_exons(lines):
    """Parse lines with ensembl formated exons

    This is designed to take a biomart dump with exons from ensembl.
    Check documentation for spec for download

    Args:
        lines(iterable(str)): An iterable with ensembl formated exons
    Yields:
        ensembl_gene(dict): A dictionary with the relevant information
    """
    header = []
    for index, line in enumerate(lines):

        # File allways start with a header line
        if index == 0:
            header = line.rstrip().split("\t")
            continue

        exon_info = parse_ensembl_line(line, header)

        exon = {
            "chrom": str(exon_info["chrom"]),
            "gene": exon_info["ensembl_gene_id"],
            "transcript": exon_info["ensembl_transcript_id"],
            "ens_exon_id": exon_info["ensembl_exon_id"],
            "exon_chrom_start": exon_info["exon_start"],
            "exon_chrom_end": exon_info["exon_end"],
            "strand": exon_info["strand"],
            "rank": exon_info["exon_rank"],
        }
        try:
            exon["5_utr_start"] = int(exon_info.get("utr_5_start"))
        except (ValueError, TypeError):
            exon["5_utr_start"] = None

        try:
            exon["5_utr_end"] = int(exon_info.get("utr_5_end"))
        except (ValueError, TypeError):
            exon["5_utr_end"] = None

        try:
            exon["3_utr_start"] = int(exon_info.get("utr_3_start"))
        except (ValueError, TypeError):
            exon["3_utr_start"] = None

        try:
            exon["3_utr_end"] = int(exon_info.get("utr_3_end"))
        except (ValueError, TypeError):
            exon["3_utr_end"] = None

        # Recalculate start and stop (taking UTR regions into account for end exons)
        if exon["strand"] == 1:
            # highest position: start of exon or end of 5' UTR
            # If no 5' UTR make sure exon_start is allways choosen
            start = max(exon["exon_chrom_start"], exon["5_utr_end"] or -1)
            # lowest position: end of exon or start of 3' UTR
            end = min(exon["exon_chrom_end"], exon["3_utr_start"] or float("inf"))
        elif exon["strand"] == -1:
            # highest position: start of exon or end of 3' UTR
            start = max(exon["exon_chrom_start"], exon["3_utr_end"] or -1)
            # lowest position: end of exon or start of 5' UTR
            end = min(exon["exon_chrom_end"], exon["5_utr_start"] or float("inf"))

        exon["start"] = start
        exon["end"] = end
        exon_id = "-".join([str(exon["chrom"]), str(start), str(end)])
        exon["exon_id"] = exon_id

        if start > end:
            raise ValueError("ERROR: %s" % exon_id)

        yield exon
