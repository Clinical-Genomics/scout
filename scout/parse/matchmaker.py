# -*- coding: utf-8 -*-
import datetime
import logging
import json
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
    LOG.info('Collecting phenotype terms for case {}'.format(case_obj.get('display_name')))
    features = []
    case_features = case_obj.get('phenotype_terms')
    if case_features:
        # re-structure case features to mirror matchmaker feature fields:
        for feature in case_features:
            feature_obj = {
                "id" : feature.get('phenotype_id'),
                "label" : feature.get('feature'),
                "observed" : "yes"
            }
            features.append(feature_obj)
    return features


def omim_terms(case_obj):
    """Extract all OMIM phenotypes available for the case
    Args:
        case_obj(dict): a scout case object
    Returns:
        disorders(list): a list of OMIM disorder objects
    """
    LOG.info("Collecting OMIM disorders for case {}".format(case_obj.get('display_name')))
    disorders = []

    case_disorders = case_obj.get('diagnosis_phenotypes') # array of OMIM terms
    if case_disorders:
        for disorder in case_disorders:
            disorder_obj = {
                "id" : ':'.join([ 'MIM', str(disorder)])
            }
            disorders.append(disorder_obj)
    return disorders


def genomic_features(store, case_obj, sample_name, genes_only):
    """Extract and parse matchmaker-like genomic features from pinned variants
        of a patient
    Args:
        store(MongoAdapter) : connection to the database
        case_obj(dict): a scout case object
        sample_name(str): sample display name
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
    # genome build is required
    build = case_obj['genome_build']
    if not build in ['37', '38']:
        build = 'GRCh37'
    else:
        build = 'GRCh'+build

    individual_pinned_snvs = list(store.sample_variants( variants=case_obj.get('suspects'),
        sample_name=sample_name))

    # if genes_only is True don't add duplicated genes
    gene_set = set()
    for var in individual_pinned_snvs:
        # a variant could hit one or several genes so create a genomic feature for each of these genes
        hgnc_genes = var.get('hgnc_ids')
        # Looks like MatchMaker Exchange API accepts only variants that hit genes :(
        if not hgnc_genes:
            continue
        for hgnc_id in hgnc_genes:
            gene_obj = store.hgnc_gene(hgnc_id)
            if not gene_obj:
                continue
            g_feature = {
                'gene': {'id': gene_obj.get('hgnc_symbol')}
            }
            if genes_only and not hgnc_id in gene_set: # if only gene names should be shared
                gene_set.add(hgnc_id)
                g_features.append(g_feature)
                continue

            # if also variants should be shared:
            g_feature['variant'] = {
                'referenceName' : var['chromosome'],
                'start' : var['position'],
                'end' : var['end'],
                'assembly' : build,
                'referenceBases' :var['reference'],
                'alternateBases' : var['alternative'],
                'shareVariantLevelData' : True
            }
            zygosity = None
            # collect zygosity for the given sample
            zygosities = var['samples'] # it's a list with zygosity situation for each sample of the case
            for zyg in zygosities:
                if zyg.get('display_name') == sample_name: # sample of interest
                    zygosity = zyg['genotype_call'].count('1')
            g_feature['zygosity'] = zygosity
            g_features.append(g_feature)

    return g_features


def parse_matches(patient_id, match_objs):
    """Parse a list of matchmaker matches objects and returns
       a readable list of matches to display in matchmaker matches view.

    Args:
        patient_id(str): id of a mme patient
        match_objs(list): list of match objs returned by MME server for the patient

    Return:
        matching_patients(list): a list of dictionaries like this:
        [
            {
                'match_oid' : '5c628537b79502057784777b',
                'match_date' : datetime,
                'match_type' : 'internal' or 'external',
                'patient_id' : patient_id,
                'score' : match scores (dict),
                'patient' : patient_obj
            },
        ]
    """
    LOG.info('Parsing MatchMaker matches for patient {}'.format(patient_id))
    matching_patients = []

    for match_obj in match_objs:
        # save match object ID
        match_oid = match_obj['_id']['$oid']
        # convert match date from millisecond to readable date
        milliseconds_date = match_obj['created']['$date']
        mdate = datetime.datetime.fromtimestamp(milliseconds_date/1000.0)

        # if patient was used as query patient:
        if match_obj['data']['patient']['id'] == patient_id:
            match_results = match_obj['results'] # List of matching patients
            for m_result in match_results:
                match_type = 'external'
                contact_institution = m_result['patient']['contact'].get('institution')
                if contact_institution and 'Scout software user' in contact_institution:
                    match_type = 'internal'

                match_patient = {
                    'match_oid' : match_oid,
                    'match_date' : mdate,
                    'match_type' : match_type,
                    'patient_id' : m_result['patient']['id'],
                    'score' : m_result['score'],
                    'patient' : m_result['patient']
                }
                matching_patients.append(match_patient)

        else: # else if patient was returned as a match result for another patient
            m_patient = match_obj['data']['patient']
            match_type = 'external'
            contact_institution = m_patient['contact'].get('institution')
            if contact_institution and 'Scout software user' in contact_institution:
                match_type = 'internal'

            # loop over match results to capture score for matching
            score = None
            for res in match_obj['results']:
                if res['patient']['id'] == patient_id:
                    score = res['score']

            match_patient = {
                'match_oid' : match_oid,
                'match_date' : mdate,
                'match_type' : match_type,
                'patient_id' : m_patient['id'],
                'score' : score,
                'patient' : m_patient
            }
            matching_patients.append(match_patient)

    # sort results by descending score
    matching_patients = sorted(matching_patients, key=lambda k: k['score']['patient'], reverse=True)
    return matching_patients
