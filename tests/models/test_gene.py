# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .setup_objects import (setup_gene, setup_transcript, setup_phenotype_term)


def test_gene():
  """
  Test the Gene class
  """
  gene = setup_gene()
  
  assert gene.hgnc_symbol == "NOCL1"
  assert gene.ensembl_gene_id == "ENSG001"
  assert gene.transcripts == [setup_transcript()]
  assert gene.functional_annotation == "transcript_ablation"
  assert gene.region_annotation == "exonic"
  assert gene.sift_prediction == "deleterious"
  assert gene.polyphen_prediction == "deleterious"
  assert gene.omim_gene_entry == 1234
  assert gene.omim_phenotypes == [setup_phenotype_term()]
  assert gene.description == "Description of gene"
  
  assert gene.reactome_link == ("http://www.reactome.org/content/query?q=ENSG001&"
                    "species=Homo+sapiens&species=Entries+without+species&"
                    "cluster=true")
  assert gene.ensembl_link == "http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG001"
  assert gene.hpa_link == "http://www.proteinatlas.org/search/ENSG001"
  assert gene.string_link == ("http://string-db.org/newstring_cgi/show_network_section."
            "pl?identifier=ENSG001")
  assert gene.entrez_link == "http://www.ncbi.nlm.nih.gov/sites/gquery/?term=NOCL1"
  
  
  
  
  
  
  
