from scout.parse import get_omim_gene_ids

def test_get_omim_gene_ids():
    variant = {
        'info_dict':{'OMIM_morbid': [
                "POLG:174763"
            ]
        }
    }
    mim_ids = get_omim_gene_ids(variant)
    assert mim_ids['POLG'] == '174763'
