# -*- coding: utf-8 -*-
import logging

LOG = logging.getLogger(__name__)

def phenotype_features(adapter, case_obj):
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


def genomic_features(adapter, scout_variants):
    """Exports all scout variants into matchmaker genotype feature format

        Args:
            scout_variants(list): a list of scout variants

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
    for variant in scout_variants:
        g_feature = {}
        # if a variant hits several genes then create more than one genomic features
        for gene in variant.get('hgnc_ids'):
            gene_obj = adapter.hgnc_gene(hgnc_identifier = gene['hgnc_id'])
            g_feature['gene'] = {"id" : gene_obj.get('hgnc_symbol')}
            #g_feature
