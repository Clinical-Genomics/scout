# -*- coding: utf-8 -*-
import logging
from pprint import pprint as pp

from scout.constants import SO_TERMS

LOG = logging.getLogger(__name__)


def parse_transcripts(raw_transcripts, allele=None):
    """Parse transcript information from VCF variants

    Args:
        raw_transcripts(iterable(dict)): An iterable with raw transcript
                                         information
    Yields:
        transcript(dict) A dictionary with transcript information
    """
    for entry in raw_transcripts:
        transcript = {}
        # There can be several functional annotations for one variant
        functional_annotations = entry.get("CONSEQUENCE", "").split("&")
        transcript["functional_annotations"] = functional_annotations
        # Get the transcript id (ensembl gene id)
        transcript_id = entry.get("FEATURE", "").split(":")[0]
        transcript["transcript_id"] = transcript_id

        # Add the hgnc gene identifiers
        # The HGNC ID is prefered and will be used if it exists
        hgnc_id = entry.get("HGNC_ID")
        if hgnc_id:
            hgnc_id = hgnc_id.split(":")[-1]
            transcript["hgnc_id"] = int(hgnc_id)
        else:
            transcript["hgnc_id"] = None

        hgnc_symbol = entry.get("SYMBOL")
        if hgnc_symbol:
            transcript["hgnc_symbol"] = hgnc_symbol
        else:
            transcript["hgnc_symbol"] = None

        ########### Fill it with the available information ###########

        ### Protein specific annotations ###

        ## Protein ID ##
        transcript["protein_id"] = entry.get("ENSP")

        ## Polyphen prediction ##
        polyphen_prediction = entry.get("POLYPHEN")
        # Default is 'unknown'
        prediction_term = "unknown"
        if polyphen_prediction:
            prediction_term = polyphen_prediction.split("(")[0]
        transcript["polyphen_prediction"] = prediction_term

        ## Sift prediction ##
        # Check with other key if it does not exist
        sift_prediction = entry.get("SIFT")
        # Default is 'unknown'
        prediction_term = "unknown"

        if not sift_prediction:
            sift_prediction = entry.get("SIFT_PRED")

        if sift_prediction:
            prediction_term = sift_prediction.split("(")[0]

        transcript["sift_prediction"] = prediction_term

        if entry.get("REVEL_RANKSCORE"):
            transcript["revel"] = float(entry.get("REVEL_RANKSCORE"))

        parse_transcripts_spliceai(transcript, entry)

        ##  SWISSPROT ##
        transcript["swiss_prot"] = entry.get("SWISSPROT") or "unknown"

        # Check for conservation annotations
        transcript["gerp"] = entry.get("GERP++_RS")
        transcript["phast"] = entry.get("PHASTCONS100WAY_VERTEBRATE")
        transcript["phylop"] = entry.get("PHYLOP100WAY_VERTEBRATE")

        if entry.get("DOMAINS", None):
            pfam_domains = entry["DOMAINS"].split("&")

            for annotation in pfam_domains:
                annotation = annotation.split(":")
                domain_name = annotation[0]
                domain_id = annotation[1]
                if domain_name == "Pfam_domain":
                    transcript["pfam_domain"] = domain_id
                elif domain_name == "PROSITE_profiles":
                    transcript["prosite_profile"] = domain_id
                elif domain_name == "SMART_domains":
                    transcript["smart_domain"] = domain_id

        coding_sequence_entry = entry.get("HGVSC", "").split(":")
        protein_sequence_entry = entry.get("HGVSP", "").split(":")

        coding_sequence_name = None
        if len(coding_sequence_entry) > 1:
            coding_sequence_name = coding_sequence_entry[-1]

        transcript["coding_sequence_name"] = coding_sequence_name

        protein_sequence_name = None
        if len(protein_sequence_entry) > 1:
            protein_sequence_name = protein_sequence_entry[-1]

        transcript["protein_sequence_name"] = protein_sequence_name

        transcript["biotype"] = entry.get("BIOTYPE")

        transcript["exon"] = entry.get("EXON")
        transcript["intron"] = entry.get("INTRON")

        if entry.get("STRAND"):
            if entry["STRAND"] == "1":
                transcript["strand"] = "+"
            elif entry["STRAND"] == "-1":
                transcript["strand"] = "-"
        else:
            transcript["strand"] = None

        functional = []
        regional = []
        for annotation in functional_annotations:
            functional.append(annotation)
            regional.append(SO_TERMS[annotation]["region"])

        transcript["functional_annotations"] = functional
        transcript["region_annotations"] = regional

        # Check if the transcript is marked cannonical by vep
        transcript["is_canonical"] = entry.get("CANONICAL") == "YES"

        # Get MANE transcripts (from VEP v103/MANE v0.92)
        if "MANE_SELECT" in entry:
            transcript["mane_select_transcript"] = entry.get("MANE_SELECT")
            transcript["mane_plus_clinical_transcript"] = entry.get("MANE_PLUS_CLINICAL")
        # Backwards compatibility with older versions of VEP/MANE
        elif "MANE" in entry:
            transcript["mane_select_transcript"] = entry.get("MANE")

        # Check if the CADD score is available on transcript level
        cadd_phred = entry.get("CADD_PHRED")
        if cadd_phred:
            transcript["cadd"] = float(cadd_phred)

        # check if mappability is available on transcript level
        # description: http://genome.ucsc.edu/cgi-bin/hgTrackUi?g=genomicSuperDups
        superdups_fractmatch = entry.get("GENOMIC_SUPERDUPS_FRAC_MATCH")
        if superdups_fractmatch:
            transcript["superdups_fracmatch"] = [
                float(fractmatch) for fractmatch in superdups_fractmatch.split("&")
            ]

        # Get mitochondrial gnomAD frequencies
        if entry.get("GNOMAD_MT_AF_HOM", "") != "":
            transcript["gnomad_mt_homoplasmic"] = float(entry.get("GNOMAD_MT_AF_HOM"))
        if entry.get("GNOMAD_MT_AF_HET", "") != "":
            transcript["gnomad_mt_heteroplasmic"] = float(entry.get("GNOMAD_MT_AF_HET"))

        # Check frequencies
        # There are different keys for different versions of VEP
        # We only support version 90+
        thousandg_freqs = []
        gnomad_freqs = []
        try:
            # The keys for VEP v90+:
            # 'AF' or '1000GAF' - 1000G all populations combined
            # 'xxx_AF' - 1000G (or NHLBI-ESP) individual populations
            # 'gnomAD_AF' - gnomAD exomes, all populations combined
            # 'gnomAD_xxx_AF' - gnomAD exomes, individual populations
            # 'MAX_AF' - Max of all populations (1000G, gnomAD exomes, ESP)
            # https://www.ensembl.org/info/docs/tools/vep/vep_formats.html

            # Loop over all keys to find frequency entries
            for key in entry:
                # All frequencies endswith AF
                if not key.endswith("AF"):
                    continue

                value = entry[key]
                if not value:
                    continue

                # This is the 1000G max af information
                if key == "AF" or key == "1000GAF":
                    transcript["thousand_g_maf"] = float(value)
                    continue

                if key == "GNOMAD_AF":
                    transcript["gnomad_maf"] = float(value)
                    continue

                if key == "EXAC_MAX_AF":
                    transcript["exac_max"] = float(value)
                    transcript["exac_maf"] = float(value)
                    continue

                if "GNOMAD" in key:
                    gnomad_freqs.append(float(value))

                else:
                    thousandg_freqs.append(float(value))

            if thousandg_freqs:
                transcript["thousandg_max"] = max(thousandg_freqs)

            if gnomad_freqs:
                transcript["gnomad_max"] = max(gnomad_freqs)

        except Exception as err:
            LOG.debug("Something went wrong when parsing frequencies")
            LOG.debug("Only splitted and normalised VEP v90+ is supported")

        if entry.get("CLINVAR_CLNVID"):
            transcript["clinvar_clnvid"] = entry["CLINVAR_CLNVID"]
            transcript["clinvar_clnsig"] = entry.get("CLINVAR_CLNSIG").lower()
            transcript["clinvar_revstat"] = entry.get("CLINVAR_CLNREVSTAT").lower()

        clnsig = entry.get("CLIN_SIG", entry.get("ClinVar_CLNSIG"))
        if clnsig:
            transcript["clnsig"] = clnsig.split("&")

        transcript["dbsnp"] = []
        transcript["cosmic"] = []
        variant_ids = entry.get("EXISTING_VARIATION")

        if variant_ids:
            for variant_id in variant_ids.split("&"):
                if variant_id.startswith("rs"):
                    transcript["dbsnp"].append(variant_id)
                elif variant_id.startswith("COSM") or variant_id.startswith("COSV"):
                    transcript["cosmic"].append(variant_id)

        cosmic_ids = entry.get("COSMIC")
        if cosmic_ids:
            for cosmic_id in cosmic_ids.split("&"):
                transcript["cosmic"].append(cosmic_id)

        yield transcript


def parse_transcripts_spliceai(transcript, entry):
    """
    Parse SpliceAI entries from raw transcripts VEP CSQ.
    Save the maximum delta score, as a candidate for the gene position max, its corresponding position and prediction.
    """

    ## SpliceAI ##
    spliceai_positions_csq = {
        "SPLICEAI_PRED_DP_AG": "spliceai_dp_ag",
        "SPLICEAI_PRED_DP_AL": "spliceai_dp_al",
        "SPLICEAI_PRED_DP_DG": "spliceai_dp_dg",
        "SPLICEAI_PRED_DP_DL": "spliceai_dp_dl",
    }
    spliceai_delta_scores_csq = {
        "SPLICEAI_PRED_DS_AG": "spliceai_ds_ag",
        "SPLICEAI_PRED_DS_AL": "spliceai_ds_al",
        "SPLICEAI_PRED_DS_DG": "spliceai_ds_dg",
        "SPLICEAI_PRED_DS_DL": "spliceai_ds_dl",
    }
    for spliceai_tag_csq, spliceai_annotation in spliceai_positions_csq.items():
        if entry.get(spliceai_tag_csq):
            transcript[spliceai_annotation] = int(entry.get(spliceai_tag_csq))

    for spliceai_tag_csq, spliceai_annotation in spliceai_delta_scores_csq.items():
        if entry.get(spliceai_tag_csq):
            transcript[spliceai_annotation] = float(entry.get(spliceai_tag_csq))

    spliceai_pairs = {
        "spliceai_ds_ag": "spliceai_dp_ag",
        "spliceai_ds_al": "spliceai_dp_al",
        "spliceai_ds_dg": "spliceai_dp_dg",
        "spliceai_ds_dl": "spliceai_dp_dl",
    }

    spliceai_delta_score = None
    spliceai_delta_position = None
    spliceai_prediction = None
    spliceai_delta_scores = [transcript.get(tag) for tag in spliceai_pairs.keys()]
    if any(spliceai_delta_scores):
        spliceai_delta_score = max(spliceai_delta_scores)
        index = spliceai_delta_scores.index(spliceai_delta_score)
        spliceai_delta_position = (
            transcript.get(list(spliceai_pairs.values())[index]) if index is not None else None
        )

        spliceai_delta_positions = [transcript.get(tag) for tag in spliceai_pairs.values()]
        spliceai_prediction = []
        for score_label, score, position_label, position in zip(
            spliceai_pairs.keys(),
            spliceai_delta_scores,
            spliceai_pairs.values(),
            spliceai_delta_positions,
        ):
            spliceai_prediction.append(
                " ".join([score_label, str(score or "-"), position_label, str(position or "-")])
            )

    transcript["spliceai_delta_score"] = spliceai_delta_score
    transcript["spliceai_delta_position"] = spliceai_delta_position
    transcript["spliceai_prediction"] = spliceai_prediction
