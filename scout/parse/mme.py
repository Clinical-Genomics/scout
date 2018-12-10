# -*- coding: utf-8 -*-
import logging
import json
LOG = logging.getLogger(__name__)

def mme_patients(json_patients_file):
    """Reads a json file containing MME patients
    and returns a list of patient dictionaries

        Args:
            json_patients_file(str) : string path to json patients file

        Returns:
            mme_patients(list) : a list of MME patient objects
    """
    with open(json_patients_file) as json_data:
        patients = json.load(json_data)
        return patients


def phenotype_features(case_obj):
    """Extract all phenotype-associated terms for a case. Drawback of this method is that
        it returns the same phenotype terms for each affected individual
        of the case. Customised phenotypes could be entered in Matchmaker
        using scout interface instead.

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


def omim_disorders( case_obj):
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


def genomic_features(adapter, scout_variants, sample_name, build):
    """Exports all scout variants into matchmaker genotype feature format

        Args:
            scout_variants(list): a list of scout variants
            sample_name(str): a name of a sample with the case
            build(str): genome build

        Returns:
            genomic_features(list): a list of genomic feature objects that looks like this:
            [
              {
                "gene": {
                  "id": "LIMS2"
                },
                "type": {
                  "id": "SO:0001583",
                  "label": "MISSENSE"
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
    genomic_features = []
    if not build in ['37', '38']:
        build = 'GRCh37'
    else:
        build = 'GRCh'+build

    for variant in scout_variants:
        # take into account that a variant can hit one or several genes.
        # in this case create a MME variant object for each of the genes
        hgnc_genes = variant.get('hgnc_ids')
        chrom = variant['chromosome']
        start = variant['position']
        stop = variant['end']
        ref = variant['reference']
        alt = variant['alternative']
        zygosity = None
        # collext zygosity for the given sample
        zygosities = variant['samples'] # it's list with zygosity situation for each sample of the case
        for zyg in zygosities:
            if zyg.get('display_name') == sample_name: # sample of interest
                zygosity = zyg['genotype_call'].count('1')

        if hgnc_genes:
            for hgnc_id in hgnc_genes:
                g_feature = {}
                gene_obj = adapter.hgnc_gene(hgnc_id, build)

                # Looks like MatchMaker Exchange API accepts only variants that hit genes :(
                if gene_obj:
                    g_feature['gene'] = {'id': gene_obj.get('hgnc_symbol') }
                    g_feature['variant'] = {
                        'referenceName' : chrom,
                        'start' : start,
                        'end' : stop,
                        'assembly' : build,
                        'referenceBases' : ref,
                        'alternateBases' : alt
                    }
                    g_feature['zygosity'] = zygosity
                    genomic_features.append(g_feature)

    return genomic_features
