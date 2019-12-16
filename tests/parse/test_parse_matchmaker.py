# -*- coding: utf-8 -*-
from scout.parse.matchmaker import parse_matches, genomic_features

def test_genomic_features_sv_variant(gene_database, case_obj, parsed_sv_variant):
    """ Test parsing genomic features for a case with one sv variant """

    adapter = gene_database

    # GIVEN a SV variant hitting at least a gene:
    a_gene = adapter.hgnc_collection.find_one()
    assert parsed_sv_variant.get('hgnc_ids') == []
    parsed_sv_variant['hgnc_ids'] = [a_gene['hgnc_id']]
    # In the proband individual
    parsed_sv_variant['samples'] = [{
        'sample_id' : case_obj['individuals'][0]['individual_id'],
        'display_name' : case_obj['individuals'][0]['display_name'],
        'genotype_call' : "0/1"
    }]
    adapter.variant_collection.insert_one(parsed_sv_variant)

    # WHEN a case has the above variant pinned
    case_obj['suspects'] = [parsed_sv_variant['_id']]
    adapter.case_collection.insert_one(case_obj)

    # AND the genomic_features parser is called:
    g_features = genomic_features(adapter, case_obj,
        case_obj['individuals'][0]['display_name'], False)

    # Then the returned genomic feature should contain only gene info:
    assert len(g_features) == 1
    assert g_features[0]['gene']['id'] == a_gene['hgnc_symbol']
    assert g_features[0].get('variant') is None


def test_genomic_features_sv_many_genes(gene_database, case_obj, parsed_sv_variant):
    """ Test parsing genomic features for a case with a sv variant hitting more than 3 genes """

    adapter = gene_database

    # GIVEN a SV variant hitting more than 3 genes
    parsed_sv_variant['hgnc_ids'] == [3337, 1711, 1226, 9405]
    # In the proband individual
    parsed_sv_variant['samples'] = [{
        'sample_id' : case_obj['individuals'][0]['individual_id'],
        'display_name' : case_obj['individuals'][0]['display_name'],
        'genotype_call' : "0/1"
    }]

    adapter.variant_collection.insert_one(parsed_sv_variant)

    # WHEN a case has the above variant pinned
    case_obj['suspects'] = [parsed_sv_variant['_id']]
    adapter.case_collection.insert_one(case_obj)

    # AND the genomic_features parser is called:
    g_features = genomic_features(adapter, case_obj,
        case_obj['individuals'][0]['display_name'], False)

    # Then the returned genomic feature should be an empty array
    assert len(g_features) == 0


def test_parse_matches(case_obj, match_objs):
    """ tests that a list of MatchMaker matches returned by the server is interpreted
        as it should
    """
    case_id = case_obj['_id']
    affected_id = ''

    for individual in case_obj['individuals']:
        if individual['phenotype'] == 'affected':
            affected_id = individual['individual_id']
            assert affected_id

    # scout patient's id in matchmaker database is composed like this
    # scout_case_id.affected_individual_id
    mme_patient_id = '.'.join([case_id, affected_id])

    # make sure that results are returned by parsing matching object
    parsed_obj = parse_matches(mme_patient_id, match_objs)

    assert isinstance(parsed_obj, list)
    # mme_patient_id has matches in match_objs:
    assert len(parsed_obj) == 2

    for match in parsed_obj:
        # make sure that all important fields are available in match results
        assert match['match_oid']
        assert match['match_date']
        matching_patients = match['patients']
        for m_patient in matching_patients:
            assert m_patient['patient_id']
            assert m_patient['node']
            assert m_patient['score']
            assert m_patient['patient']
