from scout.ext.backend.utils.get_gene_panels import get_genes


gene_list_lines = [
    "##Database=<ID=gene_list_test.txt,Version=0.1,Date=20151120,Acronym="\
    "FullList,Complete_name=Test List,Clinical_db_genome_build=GRCh37.p13",
    "##Database=<ID=gene_list_test.txt,Version=0.1,Date=20151119,Acronym="\
    "Panel1,Complete_name=Panel1,Clinical_db_genome_build=GRCh37.p13",
    "##Database=<ID=gene_list_test.txt,Version=0.1,Date=20151119,Acronym="\
    "Panel2,Complete_name=Panel2,Clinical_db_genome_build=GRCh37.p13",
     "#Chromosome\tGene_start\tGene_stop\tHGNC_symbol\tProtein_name\tSymptoms"\
     "\tBiochemistry\tImaging\tDisease_trivial_name\tTrivial_name_short"\
     "\tPhenotypic_disease_model\tOMIM_morbid\tGene_locus\tUniProt_id"\
     "\tEnsembl_gene_id\tEnsemble_transcript_ID\tReduced_penetrance"\
     "\tClinical_db_gene_annotation\tDisease_associated_transcript\t"\
     "Ensembl_transcript_to_refseq_transcript\tGene_description"\
     "\tGenetic_disease_model",
    "19\t50887461\t50921273\tPOLD1\t\t\t\t\t\t\tPOLD1:615381>AD|612591\tPOLD1:174761"\
    "\t19q13.33\t\tENSG00000062822\t\t\tPanel1,FullList\t\tPOLD1:ENST00000440232"\
    ">NM_001256849/NM_002691|ENST00000593407|ENST00000593887|ENST00000593981|"\
    "ENST00000595904>XM_005259006/XM_005259007|ENST00000596221|ENST00000596425"\
    "|ENST00000596648|ENST00000597963|ENST00000599857|ENST00000600746|ENST00000600859"\
    "|ENST00000601098\tPOLD1:polymerase_(DNA_directed)__delta_1__catalytic_subunit\t",
    "X\t16857406\t16888537\tRBBP7\t\t\t\t\t\t\t\tRBBP7:300825"\
    "\tXp22.2\t\tENSG00000102054\t\t\tPanel2,FullList\t\tRBBP7:"\
    "ENST00000330735|ENST00000380084>NM_001198719|ENST00000380087|ENST00000404022>"\
    "NM_002893/XM_005274572|ENST00000416035|ENST00000425696|ENST00000444437"\
    "|ENST00000465244|ENST00000468092|ENST00000481586|ENST00000486166|"\
    "ENST00000493145\tRBBP7:retinoblastoma_binding_protein_7\t",
    "1\t245014468\t245027844\tHNRNPU\t\t\t\t\t\t\t\tHNRNPU:602869"\
    "\t1q44\t\tENSG00000153187\t\t\tFullList,Panel2\tHNRNPU:NM_031844"\
    "\tHNRNPU:ENST00000283179|ENST00000366525|ENST00000440865|ENST00000444376"\
    ">NM_004501/NM_031844|ENST00000465881|ENST00000468690|ENST00000476241"\
    "|ENST00000483966\tHNRNPU:heterogeneous_nuclear_ribonucleoprotein_U_(scaffold_attachment_factor_A)\t",
    "Y\t2654896\t2655740\tSRY\t\t\t\t\t\t\tSRY:400044|400045"\
    "\tSRY:480000\tYp11.2\t\tENSG00000184895\t\t\tFullList,Panel1"\
    "\t\tSRY:ENST00000383070>NM_003140|ENST00000525526|ENST00000534739"\
    "\tSRY:sex_determining_region_Y\t", 
    "1\t169433147\t169455241\tSLC19A2\t\t\t\t\t\t\tSLC19A2"\
    ":249270>AR\tSLC19A2:603941\t1q24.2\t\tENSG00000117479\t\t\tPanel1"\
    ",FullList,Panel2\tSLC19A2:NM_006996.2\tSLC19A2:ENST00000236137>NM_006996"\
    "|ENST00000367804>XM_005244840\tSLC19A2:solute_carrier_family_19_("\
    "thiamine_transporter)__member_2\t",
    "12\t58141510\t58149796\tCDK4\t\t\t\t\t\t\tCDK4"\
    ":609048\tCDK4:123829\t12q14.1\t\tENSG00000135446\t\t\tPanel2"\
    ",FullList\t\tCDK4:ENST00000257904>NM_000075|ENST00000312990|"\
    "ENST00000540325|ENST00000546489|ENST00000547281|ENST00000547853|"\
    "ENST00000549606|ENST00000550419|ENST00000551706|ENST00000551800|"\
    "ENST00000551888|ENST00000552254|ENST00000552388|ENST00000552713"\
    "|ENST00000552862|ENST00000553237\tCDK4:cyclin-dependent_kinase_4\t"
    
]


def test_get_full_list_genes():
    
    genes = get_genes(gene_list_lines, 'FullList')
    assert len(genes) == 6
    assert set(genes) == set(['POLD1', 'RBBP7', 'HNRNPU', 'SRY', 
                                        'SLC19A2', 'CDK4'])

def test_get_panel_1_genes():
    
    genes = get_genes(gene_list_lines, 'Panel1')
    assert len(genes) == 3
    assert set(genes) == set(['POLD1', 'SRY', 'SLC19A2'])

def test_get_panel_2_genes():
    
    genes = get_genes(gene_list_lines, 'Panel2')
    assert len(genes) == 4
    assert set(genes) == set(['RBBP7', 'HNRNPU', 'SLC19A2', 'CDK4'])
