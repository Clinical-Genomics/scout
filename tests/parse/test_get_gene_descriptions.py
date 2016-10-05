from scout.parse.gene import parse_gene_descriptions

def test_get_gene_descriptions():
    variant = {
        'info_dict':{'Gene_description': [
                "SIVA1:First description", 
                "AKT1:Second description"]
            }
    }
    descriptions = parse_gene_descriptions(variant)
    assert descriptions['SIVA1'] == "First description"
    assert descriptions['AKT1'] == 'Second description'