# -*- coding: utf-8 -*-
import datetime
import logging

LOG = logging.getLogger(__name__)


def hpo_terms(case_obj):
    """Extract all phenotype-associated terms for a case. Drawback of this method is that
    it returns the same phenotype terms for each affected individual
    of the case.
    Args:
        case_obj(dict): a scout case object
    Returns:
        features(list): a list of phenotype objects that looks like this:
        [
          {
            "id": "HP:0001644",
            "label": "Dilated cardiomyopathy",
            "observed": "yes"
          },
          ...
        ]
    """
    LOG.info("Collecting phenotype terms for case {}".format(case_obj.get("display_name")))
    features = []
    case_features = case_obj.get("phenotype_terms")
    if case_features:
        # re-structure case features to mirror matchmaker feature fields:
        for feature in case_features:
            feature_obj = {
                "id": feature.get("phenotype_id"),
                "label": feature.get("feature"),
                "observed": "yes",
            }
            features.append(feature_obj)
    return features


def omim_terms(store, case_obj):
    """Extract all OMIM phenotypes available for the case
    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(dict): a scout case object
    Returns:
        disorders(list): a list of OMIM disorder objects
    """
    LOG.info("Collecting OMIM disorders for case {}".format(case_obj.get("display_name")))
    disorders = []

    case_disorders = case_obj.get("diagnosis_phenotypes")  # array of OMIM terms
    if case_disorders:
        for disorder in case_disorders:
            if isinstance(disorder, dict):
                disorder = disorder.get("disease_id")
            # Historically diagnosis_phenotypes was saved as a list of id:s,
            # at that time no other coding systems were present in the database
            elif isinstance(disorder, int):
                disorder = f"OMIM:{disorder}"
            disease_term = store.disease_term(disorder)
            if disease_term is None:
                LOG.warning(f"Disease term {disorder} could not be found in database.")
                continue
            if disease_term["source"] == "OMIM":
                disorder_obj = {
                    "id": disorder.replace("OMIM", "MIM"),
                    "label": disease_term.get("description"),
                }
                disorders.append(disorder_obj)
    return disorders


def genomic_features(store, case_obj, sample_name, candidate_vars, genes_only):
    """Extract and parse matchmaker-like genomic features from pinned variants
        of a patient
    Args:
        store(MongoAdapter) : connection to the database
        case_obj(dict): a scout case object
        sample_name(str): sample display name
        candidate_vars(list): a list of variants/genes chosen from the user. Example: ["4c7d5c70d955875504db72ef8e1abe77", "77d69d4d78a8e272365bdabe4f607327|TIPIN"]
        genes_only(bool): if True only gene names will be included in genomic features

    Returns:
        g_features(list): a list of genomic feature objects that looks like this:
            [
              {
                "gene": {
                  "id": "LIMS2"
                },
                "variant": {
                  "alternateBases": "C",
                  "assembly": "GRCh37",
                  "end": 128412081,
                  "referenceBases": "G",
                  "referenceName": "2",
                  "start": 128412080
                },
                "zygosity": 1
              },
              ....
            ]

    """
    g_features = []

    for var in candidate_vars:
        vari_id = var.split("|")[0]
        var_obj = store.sample_variant(vari_id, sample_name)
        if var_obj is None:
            continue

        selected_gene: str = var.split("|")[1] if "|" in var else None

        if var_obj["category"] not in ["snv", "snv_research", "cancer", "cancer_research"]:
            g_features.append({"gene": {"id": selected_gene}})
            continue

        # "snv", "snv_research", "cancer", "cancer_research" variants
        hgnc_genes = var_obj.get("hgnc_ids")
        if not hgnc_genes:
            continue
        for hgnc_id in hgnc_genes:
            gene_caption = store.hgnc_gene_caption(hgnc_id, case_obj["genome_build"])
            if not gene_caption:
                continue

            gene_symbol: str = gene_caption.get("hgnc_symbol")
            if selected_gene and gene_symbol != selected_gene:
                continue

            g_feature = {"gene": {"id": gene_symbol}}
            if genes_only is True:  # Disclose only gene info
                g_features.append(g_feature)
                continue

            # share Variant-level information
            g_feature["variant"] = {
                "referenceName": var_obj["chromosome"],
                "start": var_obj["position"],
                "end": var_obj["end"],
                "assembly": "GRCh38" if "38" in str(case_obj.get("genome_build", "")) else "GRCh37",
                "referenceBases": var_obj["reference"],
                "alternateBases": var_obj["alternative"],
                "shareVariantLevelData": True,
            }

            zygosity = None
            # collect zygosity for the given sample
            zygosities = var_obj[
                "samples"
            ]  # it's a list with zygosity situation for each sample of the case
            for zyg in zygosities:
                if zyg.get("display_name") == sample_name:  # sample of interest
                    zygosity = zyg["genotype_call"].count("1") + zyg["genotype_call"].count("2")
            g_feature["zygosity"] = zygosity
            g_features.append(g_feature)

    return g_features


def parse_matches(patient_id, match_objs):
    """Parse a list of matchmaker matches objects and returns
       a readable list of matches to display in matchmaker matches view.

    Args:
        patient_id(str): id of a mme patient
        match_objs(list): list of match objs returned by MME server for the patient
                # match_objs looks like this:
                    [
                        {
                            'node' : { id : node_id , label: node_label},
                            'patients' : [
                                { 'patient': {patient1_data} },
                                { 'patient': {patient2_data} },
                                ..
                            ]
                        },
                        ..
                    ]

    Returns:
        parsed_matches(list): a list of parsed match objects

    """
    LOG.info("Parsing MatchMaker matches for patient {}".format(patient_id))
    parsed_matches = []

    for match_obj in match_objs:
        match_date = match_obj["created"]["$date"]
        try:  # Patientmatcher < 4.5 returns dates in milliseconds
            mdate = datetime.datetime.fromtimestamp(match_date / 1000.0)
        except TypeError:  # Patientmatcher >= 4.5 returns dates in isoformat
            mdate = datetime.datetime.strptime(match_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        match_type = "external"
        matching_patients = []

        parsed_match = {
            "match_oid": match_obj["_id"]["$oid"],  # save match object ID
            "match_date": mdate,
        }

        # if patient was used as query patient:
        if match_obj["data"]["patient"]["id"] == patient_id:
            match_results = match_obj["results"]  # List of matching patients
            for node_result in match_results:
                if match_obj["match_type"] == "internal":
                    match_type = "internal"

                for patient in node_result["patients"]:
                    match_patient = {
                        "patient_id": patient["patient"]["id"],
                        "score": patient["score"],
                        "patient": patient["patient"],
                        "node": node_result["node"],
                    }
                    matching_patients.append(match_patient)

        else:  # else if patient was returned as a match result for another patient
            m_patient = match_obj["data"]["patient"]
            contact_institution = m_patient["contact"].get("institution")
            if contact_institution and "Scout software user" in contact_institution:
                match_type = "internal"

            # loop over match results to capture score for matching
            score = None
            for res in match_obj["results"]:
                for patient in res["patients"]:
                    LOG.info("Looping in else, patient:{}".format(patient["patient"]["id"]))
                    if patient["patient"]["id"] == patient_id:
                        score = patient["score"]
                        match_patient = {
                            "patient_id": m_patient["id"],
                            "score": score,
                            "patient": m_patient,
                            "node": res["node"],
                        }
                        matching_patients.append(match_patient)

        parsed_match["match_type"] = match_type
        parsed_match["patients"] = matching_patients
        parsed_matches.append(parsed_match)

    # sort results by descending score
    parsed_matches = sorted(parsed_matches, key=lambda k: k["match_date"], reverse=True)
    return parsed_matches
