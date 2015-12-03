from scout.ext.backend.utils import get_omim_phenotype_ids

def test_get_omim_phenotype_ids():
    variant = {
        'info_dict':{'Phenotypic_disease_model': [
                "POLG:157640>AD|258450>AR|607459>AR|203700>AR|613662>AR"
            ]
        }
    }
    phenotypes = get_omim_phenotype_ids(variant)
    for phenotype_term in phenotypes['POLG']:
        if phenotype_term.phenotype_id == '157640':
            assert phenotype_term.disease_models == ['AD']
