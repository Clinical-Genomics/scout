import logging

from scout.constants import CLINSIG_MAP, CALLERS, ACMG_COMPLETE_MAP
from scout.server.links import add_gene_links, ensembl, add_tx_links

LOG = logging.getLogger(__name__)


def add_panel_specific_gene_info(panel_info):
    """Adds manualy curated information from a gene panel to a gene

    The panel info is a list of dictionaries since there can be multiple infos about a panel.

    Args:
        panel_info(list(dict)): List of panel information about a gene

    Returns:
        panel_specific(dict): A dictionary with a summary of the information from gene panels
    """
    panel_specific = {}
    # Manually annotated disease associated transcripts
    disease_associated = set()
    # We need to strip the version to compare against others
    disease_associated_no_version = set()
    manual_penetrance = False
    mosaicism = False
    manual_inheritance = set()

    # We need to loop since there can be information from multiple panels
    for gene_info in panel_info:
        # Check if there are manually annotated disease transcripts
        for tx in gene_info.get("disease_associated_transcripts", []):
            # We remove the version of transcript at this stage
            stripped = tx.split(".")[0]
            disease_associated_no_version.add(stripped)
            disease_associated.add(tx)

        if gene_info.get("reduced_penetrance"):
            manual_penetrance = True

        if gene_info.get("mosaicism"):
            mosaicism = True

        manual_inheritance.update(gene_info.get("inheritance_models", []))

    panel_specific["disease_associated_transcripts"] = list(disease_associated)
    panel_specific["disease_associated_no_version"] = disease_associated_no_version
    panel_specific["manual_penetrance"] = manual_penetrance
    panel_specific["mosaicism"] = mosaicism
    panel_specific["manual_inheritance"] = list(manual_inheritance)

    return panel_specific


def update_transcripts_information(variant_gene, hgnc_gene, variant_obj, genome_build=None):
    """Collect tx info from the hgnc gene and panels and update variant transcripts

    Since the hgnc information are continuously being updated we need to run this each time a
    variant is fetched.

    This function will:
        - Add a dictionary with tx_id -> tx_info to the hgnc variant
        - Add information from the panel
        - Adds a list of refseq transcripts

    Args:
        variant_gene(dict): the gene information from the variant
        hgnc_gene(dict): the hgnc gene information
        varaiant_obj(scout.models.Variant)
        genome_build(str): genome build

    """
    genome_build = genome_build or "37"
    disease_associated_no_version = variant_gene.get("disease_associated_no_version", set())
    # Create a dictionary with transcripts information
    # Use ensembl transcript id as keys
    transcripts_dict = {}
    # Add transcript information from the hgnc gene
    for transcript in hgnc_gene.get("transcripts", []):
        tx_id = transcript["ensembl_transcript_id"]
        transcripts_dict[tx_id] = transcript

    # Add the transcripts to the gene object
    hgnc_gene["transcripts_dict"] = transcripts_dict
    hgnc_symbol = hgnc_gene["hgnc_symbol"]

    # First loop over the variants transcripts
    for transcript in variant_gene.get("transcripts", []):
        tx_id = transcript["transcript_id"]
        hgnc_transcript = transcripts_dict.get(tx_id)
        # If the tx does not exist in ensembl anymore we skip it
        if not hgnc_transcript:
            continue

        # Check in the common information if it is a primary transcript
        if hgnc_transcript.get("is_primary"):
            transcript["is_primary"] = True

        # Add the transcript links
        add_tx_links(transcript, genome_build, hgnc_symbol)
        # If the transcript has a ref seq identifier we add that
        # to the variants transcript
        refseq_id = hgnc_transcript.get("refseq_id")
        if not refseq_id:
            continue
        transcript["refseq_id"] = refseq_id
        variant_obj["has_refseq"] = True

        # Check if the refseq id are disease associated
        if refseq_id in disease_associated_no_version:
            transcript["is_disease_associated"] = True

        # Since a ensemble transcript can have multiple refseq identifiers we add all of
        # those
        transcript["refseq_identifiers"] = hgnc_transcript.get("refseq_identifiers", [])
        transcript["change_str"] = transcript_str(transcript, hgnc_symbol)


def add_gene_info(store, variant_obj, gene_panels=None, genome_build=None):
    """Adds information to variant genes from hgnc genes and gene panels.

    Variants are annotated with gene and transcript information from VEP. In Scout the database
    keeps updated and extended information about genes and transcript. This function will compliment
     the VEP information with the updated database information.
    Also there is sometimes additional information that are manually curated in the gene panels.
    This information needs to be added to the variant before sending it to the template.

    This function will loop over all genes and add that extra information.

    Args:
        store(scout.adapter.MongoAdapter)
        variant_obj(dict): A variant from the database
        gene_panels(list(dict)): List of panels from database
        genome_build(str)

    Returns:
        variant_obj
    """
    gene_panels = gene_panels or []
    genome_build = genome_build or "37"

    # Add a variable that checks if there are any refseq transcripts

    # extra_info will hold information from gene panels
    extra_info = {}
    for panel_obj in gene_panels:
        for gene_info in panel_obj["genes"]:
            hgnc_id = gene_info["hgnc_id"]
            if hgnc_id not in extra_info:
                extra_info[hgnc_id] = []

            extra_info[hgnc_id].append(gene_info)

    # Loop over the genes in the variant object to add information
    # from hgnc_genes and panel genes to the variant object
    variant_obj["has_refseq"] = False
    variant_obj["disease_associated_transcripts"] = []
    all_models = set()
    for variant_gene in variant_obj.get("genes", []):
        hgnc_id = variant_gene["hgnc_id"]
        # Get the hgnc_gene
        hgnc_gene = store.hgnc_gene(hgnc_id, build=genome_build)

        if not hgnc_gene:
            continue
        hgnc_symbol = hgnc_gene["hgnc_symbol"]
        # Add omim information if gene is annotated to have incomplete penetrance
        if hgnc_gene.get("incomplete_penetrance"):
            variant_gene["omim_penetrance"] = True

        ############# PANEL SPECIFIC INFORMATION #############
        # Panels can have extra information about genes and transcripts
        panel_info = add_panel_specific_gene_info(extra_info.get(hgnc_id, []))
        variant_gene.update(panel_info)

        update_transcripts_information(variant_gene, hgnc_gene, variant_obj, genome_build)

        variant_gene["common"] = hgnc_gene

        add_gene_links(variant_gene, genome_build)

        # Add disease associated transcripts from panel to variant
        for refseq_id in panel_info.get("disease_associated_transcripts", []):
            transcript_str = "{}:{}".format(hgnc_symbol, refseq_id)
            variant_obj["disease_associated_transcripts"].append(transcript_str)

        # Add the associated disease terms
        disease_terms = store.disease_terms(hgnc_id)
        variant_gene["disease_terms"] = disease_terms

        all_models = all_models.union(set(variant_gene["manual_inheritance"]))
        omim_models = set()
        for disease_term in variant_gene.get("disease_terms", []):
            omim_models.update(disease_term.get("inheritance", []))
        variant_gene["omim_inheritance"] = list(omim_models)

        all_models = all_models.union(omim_models)

    variant_obj["all_models"] = all_models

    return variant_obj


def predictions(genes):
    """Adds information from variant specific genes to display.

    Args:
        genes(list[dict])

    Returns:
        data(dict)
    """
    data = {
        "sift_predictions": [],
        "polyphen_predictions": [],
        "region_annotations": [],
        "functional_annotations": [],
    }
    for gene_obj in genes:
        for pred_key in data:
            gene_key = pred_key[:-1]
            if len(genes) == 1:
                value = gene_obj.get(gene_key, "-")
            else:
                gene_id = gene_obj.get("hgnc_symbol") or str(gene_obj.get("hgnc_id", 0))
                value = ":".join([gene_id, gene_obj.get(gene_key, "-")])
            data[pred_key].append(value)

    return data


def frequencies(variant_obj):
    """Add frequencies in the correct way for the template

    This function converts the raw annotations to something better to visualize.
    GnomAD is mandatory and will always be shown.

    Args:
        variant_obj(scout.models.Variant)

    Returns:
        frequencies(list(tuple)): A list of frequencies to display
    """
    if variant_obj["category"] == "sv":
        freqs = {
            "gnomad_frequency": {"display_name": "GnomAD", "link": None},
            "clingen_cgh_benign": {
                "display_name": "ClinGen CGH (benign)",
                "link": None,
            },
            "clingen_cgh_pathogenic": {
                "display_name": "ClinGen CGH (pathogenic)",
                "link": None,
            },
            "clingen_ngi": {"display_name": "ClinGen NGI", "link": None},
            "clingen_mip": {"display_name": "ClinGen MIP", "link": None},
            "swegen": {"display_name": "SweGen", "link": None},
            "decipher": {"display_name": "Decipher", "link": None},
            "thousand_genomes_frequency": {"display_name": "1000G", "link": None},
            "thousand_genomes_frequency_left": {
                "display_name": "1000G(left)",
                "link": None,
            },
            "thousand_genomes_frequency_right": {
                "display_name": "1000G(right)",
                "link": None,
            },
        }
    else:
        freqs = {
            "gnomad_frequency": {
                "display_name": "GnomAD",
                "link": variant_obj.get("gnomad_link"),
            },
            "thousand_genomes_frequency": {
                "display_name": "1000G",
                "link": variant_obj.get("thousandg_link"),
            },
            "max_thousand_genomes_frequency": {
                "display_name": "1000G(max)",
                "link": variant_obj.get("thousandg_link"),
            },
            "exac_frequency": {
                "display_name": "ExAC",
                "link": variant_obj.get("exac_link"),
            },
            "max_exac_frequency": {
                "display_name": "ExAC(max)",
                "link": variant_obj.get("exac_link"),
            },
        }

    frequency_list = []
    for freq_key in freqs:
        display_name = freqs[freq_key]["display_name"]
        value = variant_obj.get(freq_key)
        link = freqs[freq_key]["link"]
        # Allways add gnomad
        if freq_key == "gnomad_frequency":
            # If gnomad not found search for exac
            if not value:
                value = variant_obj.get("exac_frequency")
            value = value or "NA"
            frequency_list.append((display_name, value, link))
            continue
        if value:
            frequency_list.append((display_name, value, link))

    return frequency_list


def frequency(variant_obj):
    """Returns a judgement on the overall frequency of the variant.

    Combines multiple metrics into a single call.

    Args:
        variant_obj(scout.models.Variant)

    Returns:
        str in ['common','uncommon','rare']
    """
    most_common_frequency = max(
        variant_obj.get("thousand_genomes_frequency") or 0,
        variant_obj.get("exac_frequency") or 0,
        variant_obj.get("gnomad_frequency") or 0,
    )

    if most_common_frequency > 0.05:
        return "common"
    if most_common_frequency > 0.01:
        return "uncommon"

    return "rare"


def is_affected(variant_obj, case_obj):
    """Adds information to show in view if sample is affected

    The views sometimes expect strings so we need to convert the raw data. This is an typical
    example of that situation

    Loop over the samples in a variant and add information from the case is they are affected

    Args:
        variant_obj(scout.models.Variant)
    """
    individuals = {
        individual["individual_id"]: individual for individual in case_obj["individuals"]
    }
    for sample_obj in variant_obj["samples"]:
        individual = individuals[sample_obj.get("sample_id")]
        if not individual:
            continue
        sample_obj["is_affected"] = False

        if individual["phenotype"] == 2:
            sample_obj["is_affected"] = True


def evaluation(store, evaluation_obj):
    """Fetch and fill-in evaluation object."""
    evaluation_obj["institute"] = store.institute(evaluation_obj["institute_id"])
    evaluation_obj["case"] = store.case(evaluation_obj["case_id"])
    evaluation_obj["variant"] = store.variant(evaluation_obj["variant_specific"])
    evaluation_obj["criteria"] = {
        criterion["term"]: criterion for criterion in evaluation_obj["criteria"]
    }
    evaluation_obj["classification"] = ACMG_COMPLETE_MAP.get(evaluation_obj["classification"])
    return evaluation_obj


def transcript_str(transcript_obj, gene_name=None):
    """Generate amino acid change as a string.

    Args:
        transcript_obj(dict)
        gene_name(str)

    Returns:
        change_str(str): A description of the transcript level change
    """
    # variant between genes
    gene_part = "intergenic"
    part_count_raw = "0"

    if transcript_obj.get("exon"):
        gene_part = "exon"
        part_count_raw = transcript_obj["exon"]
    elif transcript_obj.get("intron"):
        gene_part = "intron"
        part_count_raw = transcript_obj["intron"]

    part_count = part_count_raw.rpartition("/")[0]
    change_str = "{}:{}{}:{}:{}".format(
        transcript_obj.get("refseq_id", ""),
        gene_part,
        part_count,
        transcript_obj.get("coding_sequence_name", "NA"),
        transcript_obj.get("protein_sequence_name", "NA"),
    )
    if gene_name:
        change_str = "{}:".format(gene_name) + change_str

    return change_str


def end_position(variant_obj):
    """Calculate end position for a variant.

    Args:
        variant_obj(scout.models.Variant)

    Returns:
        end_position(int)
    """
    alt_len = len(variant_obj["alternative"])
    ref_len = len(variant_obj["reference"])
    if alt_len == ref_len:
        num_bases = alt_len
    else:
        num_bases = max(alt_len, ref_len)

    return variant_obj["position"] + (num_bases - 1)


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
    for panel in case_obj.get("panels", []):
        if not panel.get("is_default"):
            continue
        panel_obj = store.gene_panel(panel["panel_name"], panel.get("version"))
        if not panel_obj:
            LOG.warning(
                "Panel {0} version {1} could not be found".format(
                    panel["panel_name"], panel.get("version")
                )
            )
            continue
        default_panels.append(panel_obj)
    return default_panels


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
    for clinsig_obj in variant_obj.get("clnsig", []):
        # The clinsig objects allways have a accession
        if not "accession" in clinsig_obj:
            continue
        # Old version
        link = "https://www.ncbi.nlm.nih.gov/clinvar/{}"
        if isinstance(clinsig_obj["accession"], int):
            # New version
            link = "https://www.ncbi.nlm.nih.gov/clinvar/variation/{}"

        human_str = "not provided"
        clinsig_value = clinsig_obj.get("value")
        if clinsig_value is not None:
            try:
                int(clinsig_value)
                human_str = CLINSIG_MAP.get(clinsig_value, "not provided")
            except ValueError:
                # old version where clinsig value is a string
                human_str = clinsig_value

        clinsig_obj["human"] = human_str
        clinsig_obj["link"] = link.format(clinsig_obj["accession"])

        yield clinsig_obj


def callers(variant_obj, category="snv"):
    """Return info about callers.

    Args:
        variant_obj(scout.models.Variant)
        category(str)

    Returns:
        calls(list(str)): A list of the callers that identified the variant
    """
    calls = set()
    for caller in CALLERS[category]:
        if variant_obj.get(caller["id"]):
            calls.add((caller["name"], variant_obj[caller["id"]]))

    return list(calls)
