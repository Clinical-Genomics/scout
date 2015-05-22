# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import Gene


def setup_gene(**kwargs):
  """
  Setup an Gene object
  """
  hgnc_symbol = kwargs.get('hgnc_symbol', 'NOCL1')
  ensembl_gene_id = kwargs.get('ensembl_gene_id', 'ENSG001')
  transcripts = kwargs.get('transcripts', [])
  functional_annotation = kwargs.get('functional_annotation', 'transcript_ablation')
  region_annotation = kwargs.get('region_annotation', 'exonic')
  sift_prediction = kwargs.get('sift_prediction', 'deleterious')
  polyphen_prediction = kwargs.get('polyphen_prediction', 'deleterious')
  omim_gene_entry = kwargs.get('omim_gene_entry', 1234)
  omim_phenotypes = kwargs.get('omim_phenotypes', [])
  description = kwargs.get('omim_phenotypes', "Description of gene")

  gene = Gene(
    hgnc_symbol = hgnc_symbol,
    ensembl_gene_id = ensembl_gene_id,
    transcripts = transcripts,
    functional_annotation = functional_annotation,
    region_annotation = region_annotation,
    sift_prediction = sift_prediction,
    polyphen_prediction = polyphen_prediction,
    omim_gene_entry = omim_gene_entry,
    omim_phenotypes = omim_phenotypes,
    description = description
  )
  return gene
  
def test_gene():
  """
  Test the Gene class
  """
  gene = setup_gene()
  
  assert gene.hgnc_symbol == "NOCL1"
  assert gene.ensembl_gene_id == "ENSG001"
  assert gene.transcripts == []
  assert gene.functional_annotation == "transcript_ablation"
  assert gene.region_annotation == "exonic"
  assert gene.sift_prediction == "deleterious"
  assert gene.polyphen_prediction == "deleterious"
  assert gene.omim_gene_entry == 1234
  assert gene.omim_phenotypes == []
  assert gene.description == "Description of gene"
  
  assert gene.reactome_link == ("http://www.reactome.org/content/query?q=ENSG001&"
                    "species=Homo+sapiens&species=Entries+without+species&"
                    "cluster=true")
  assert gene.ensembl_link == "http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG001"
  assert gene.hpa_link == "http://www.proteinatlas.org/search/ENSG001"
  assert gene.string_link == ("http://string-db.org/newstring_cgi/show_network_section."
            "pl?identifier=ENSG001")
  assert gene.entrez_link == "http://www.ncbi.nlm.nih.gov/sites/gquery/?term=NOCL1"
  
  
  
  
  
  
  
