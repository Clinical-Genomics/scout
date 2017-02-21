from datetime import datetime
from scout.models.panel import GenePanel, Gene


def test_add_panel(adapter):
    ## GIVEN a adapter without gene panels
    
    assert GenePanel.objects.count() == 0
    
    insert_date = datetime.now()
    gene_1 = Gene(
        hgnc_id = 1,
        symbol = 'gene1',

        disease_associated_transcripts = ['NM1'],
    )
    
    test_panel = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 1.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )
    
    ## WHEN inserting a gene panel object
    
    adapter.add_gene_panel(test_panel)
    
    ## THEN assert the panel has been inserted in a correct way
    
    panel_obj = GenePanel.objects.get()
    
    assert panel_obj['panel_name'] == test_panel['panel_name']

def test_get_panel(adapter):
    ## GIVEN a adapter without gene panels
    
    assert GenePanel.objects.count() == 0
    
    insert_date = datetime.now()
    gene_1 = Gene(
        hgnc_id = 1,
        symbol = 'gene1',

        disease_associated_transcripts = ['NM1'],
    )
    
    test_panel = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 1.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )
    
    ## WHEN inserting a gene panel object
    
    adapter.add_gene_panel(test_panel)
    
    ## THEN assert the panel has been inserted in a correct way
    
    panel_obj = adapter.gene_panel(panel_id='test')
    
    assert panel_obj['panel_name'] == test_panel['panel_name']

def test_get_panel_multiple(adapter):
    ## GIVEN a adapter without gene panels
    
    assert GenePanel.objects.count() == 0
    
    insert_date = datetime.now()
    gene_1 = Gene(
        hgnc_id = 1,
        symbol = 'gene1',

        disease_associated_transcripts = ['NM1'],
    )
    
    test_panel = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 1.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )

    adapter.add_gene_panel(test_panel)

    test_panel_2 = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 2.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )
    
    ## WHEN inserting a gene panel object
    
    adapter.add_gene_panel(test_panel_2)
    
    ## THEN assert the panel has been inserted in a correct way
    
    panel_obj = adapter.gene_panel(panel_id='test')
    
    assert panel_obj['version'] == test_panel_2['version']

def test_get_panel_version(adapter):
    ## GIVEN a adapter without gene panels
    
    assert GenePanel.objects.count() == 0
    
    insert_date = datetime.now()
    gene_1 = Gene(
        hgnc_id = 1,
        symbol = 'gene1',

        disease_associated_transcripts = ['NM1'],
    )
    
    test_panel = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 1.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )

    adapter.add_gene_panel(test_panel)

    test_panel_2 = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 2.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )
    
    ## WHEN inserting a gene panel object
    
    adapter.add_gene_panel(test_panel_2)
    
    ## THEN assert the panel has been inserted in a correct way
    
    panel_obj = adapter.gene_panel(panel_id='test', version=test_panel['version'])
    
    assert panel_obj['version'] == test_panel['version']

def test_update_panel_add(adapter):
    ## GIVEN a adapter without gene panels
    
    assert GenePanel.objects.count() == 0
    
    insert_date = datetime.now()
    gene_1 = Gene(
        hgnc_id = 1,
        symbol = 'gene1',

        disease_associated_transcripts = ['NM1'],
    )
    
    gene_2 = Gene(
        hgnc_id = 2,
        symbol = 'gene2',
        disease_associated_transcripts = ['NM2'],
        action='add'
    )
    
    test_panel = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 1.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )

    adapter.add_gene_panel(test_panel)
    
    updated_panel = {
        'panel_name': 'test',
        'institute': 'test_institute',
        'version': 1.0,
        'display_name': 'test_panel',
        'genes': [gene_1],
        'pending_genes': [gene_2],
    }
    
    ## WHEN inserting a gene panel object
    
    adapter.update_panel(updated_panel)
    
    ## THEN assert the panel has been inserted in a correct way
    
    panel_obj = adapter.gene_panel(panel_id='test')
    
    assert panel_obj['version'] == 2.0
    assert len(panel_obj['genes']) == 2

def test_update_panel_delete(adapter):
    ## GIVEN a adapter without gene panels
    
    assert GenePanel.objects.count() == 0
    
    insert_date = datetime.now()
    gene_1 = Gene(
        hgnc_id = 1,
        symbol = 'gene1',

        disease_associated_transcripts = ['NM1'],
    )
    
    gene_2 = Gene(
        hgnc_id = 1,
        symbol = 'gene1',
        disease_associated_transcripts = ['NM2'],
        action='delete'
    )
    
    test_panel = GenePanel(
        panel_name = 'test',
        institute = 'test_institute',
        version = 1.0,
        date = insert_date,
        display_name = 'test_panel',
        
        genes = [gene_1]
    )

    adapter.add_gene_panel(test_panel)
    
    updated_panel = {
        'panel_name': 'test',
        'institute': 'test_institute',
        'version': 1.0,
        'display_name': 'test_panel',
        'genes': [gene_1],
        'pending_genes': [gene_2],
    }
    
    ## WHEN inserting a gene panel object
    
    adapter.update_panel(updated_panel)
    
    ## THEN assert the panel has been inserted in a correct way
    
    panel_obj = adapter.gene_panel(panel_id='test')
    
    assert panel_obj['version'] == 2.0
    assert len(panel_obj['genes']) == 0
    