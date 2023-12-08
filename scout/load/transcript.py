import logging

from click import progressbar

from scout.build.genes.transcript import build_transcript
from scout.parse.ensembl import parse_transcripts
from scout.utils.ensembl_biomart_clients import EnsemblBiomartHandler

LOG = logging.getLogger(__name__)

TRANSCRIPT_CATEGORIES = ["mrna", "nc_rna", "mrna_predicted"]


def load_transcripts(adapter, transcripts_lines=None, build="37", ensembl_genes=None):
    """Load all the transcripts

    Transcript information is from ensembl.

    Args:
        adapter(MongoAdapter)
        transcripts_lines(iterable): iterable with ensembl transcript lines
        build(str)
        ensembl_genes(dict): Map from ensembl_id -> HgncGene

    Returns:
        transcript_objs(list): A list with all transcript objects
    """
    # Fetch all genes with ensemblid as keys
    ensembl_genes = ensembl_genes or adapter.ensembl_genes(build)

    if transcripts_lines is None:
        ensembl_client = EnsemblBiomartHandler(build=build)
        transcripts_lines = ensembl_client.stream_resource(interval_type="transcripts")

    # Map with all transcripts enstid -> parsed transcript
    transcripts_dict = parse_transcripts(transcripts_lines)
    missing_in_build = 0
    for ens_tx_id in list(transcripts_dict):
        parsed_tx = transcripts_dict[ens_tx_id]
        # Get the ens gene id
        ens_gene_id = parsed_tx["ensembl_gene_id"]

        # Fetch the internal gene object to find out the correct hgnc id
        gene_obj = ensembl_genes.get(ens_gene_id)
        # If the gene is non existing in scout we skip the transcript
        if not gene_obj:
            transcripts_dict.pop(ens_tx_id)
            missing_in_build += 1
            continue

        # Add the correct hgnc id
        parsed_tx["hgnc_id"] = gene_obj["hgnc_id"]
        # Primary transcript information is collected from HGNC
        parsed_tx["primary_transcripts"] = set(gene_obj.get("primary_transcripts", []))

    LOG.warning(f"{missing_in_build} genes not existing in build {build}")

    ref_seq_transcripts = 0
    nr_primary_transcripts = 0
    nr_transcripts = len(transcripts_dict)

    transcript_objs = []

    with progressbar(
        transcripts_dict.values(), label="Building transcripts", length=nr_transcripts
    ) as bar:
        for tx_data in bar:
            #################### Get the correct refseq identifier ####################
            # We need to decide one refseq identifier for each transcript, if there are any to
            # choose from. The algorithm is as follows:
            # If there is ONE mrna this is choosen
            # If there are several mrna the one that is in 'primary_transcripts' is choosen
            # Else one is choosen at random
            # The same follows for the other categories where nc_rna has precedense over mrna_predicted
            # We will store all refseq identifiers in a "refseq_identifiers" list as well
            tx_data["is_primary"] = False
            primary_transcripts = tx_data["primary_transcripts"]
            refseq_identifier = None
            refseq_identifiers = []
            for category in TRANSCRIPT_CATEGORIES:
                identifiers = tx_data[category]
                if not identifiers:
                    continue

                for refseq_id in identifiers:
                    # Add all refseq identifiers to refseq_identifiers
                    refseq_identifiers.append(refseq_id)
                    ref_seq_transcripts += 1

                    if refseq_id in primary_transcripts:
                        refseq_identifier = refseq_id
                        tx_data["is_primary"] = True
                        nr_primary_transcripts += 1

                    if not refseq_identifier:
                        refseq_identifier = refseq_id

            if refseq_identifier:
                tx_data["refseq_id"] = refseq_identifier
            if refseq_identifiers:
                tx_data["refseq_identifiers"] = refseq_identifiers

            ####################  ####################  ####################
            # Build the transcript object
            tx_obj = build_transcript(tx_data, build)
            transcript_objs.append(tx_obj)

    # Load all transcripts
    LOG.info("Loading transcripts...")
    if len(transcript_objs) > 0:
        adapter.load_transcript_bulk(transcript_objs)

    LOG.info("Number of transcripts in build %s: %s", build, nr_transcripts)
    LOG.info("Number of transcripts with refseq identifier: %s", ref_seq_transcripts)
    LOG.info("Number of primary transcripts: %s", nr_primary_transcripts)

    return transcript_objs
