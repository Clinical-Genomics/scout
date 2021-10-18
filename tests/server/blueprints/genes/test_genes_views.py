# -*- coding: utf-8 -*-
from flask import url_for


def test_genes(client):
    # GIVEN an initialized database
    # WHEN accessing the genes overview page
    resp = client.get(url_for("genes.genes"))
    # THEN it should return 20 random genes and a search box
    assert resp.status_code == 200


def test_genes_query(client):
    # GIVEN an initialized database
    # WHEN accessing genes overview with a gene query
    hgnc_id = 1968
    resp = client.get(url_for("genes.genes", query="{} | LYST".format(hgnc_id)))
    # THEN it should redirect (302) to the specific gene page
    assert resp.status_code == 302
    assert resp.location.endswith(url_for("genes.gene", hgnc_id=hgnc_id))


def test_gene(client):
    # GIVEN an initialized database
    # WHEN accessing a specific gene (existing!)
    hgnc_id = 1968
    resp = client.get(url_for("genes.gene", hgnc_id=hgnc_id))
    # THEN it should display information about the gene
    assert resp.status_code == 200

    # GIVEN a non-existent HGNC id
    hgnc_id = 2132333
    # WHEN accessing the gene view
    resp = client.get(url_for("genes.gene", hgnc_id=hgnc_id))
    # THEN it should return a 404 page
    assert resp.status_code == 200


def test_api_genes(client):
    # GIVEN a partial search term for a gene
    query = "lys"
    hgnc_id = 1968
    # WHEN querying the genes api endpoint
    resp = client.get(url_for("genes.api_genes", query=query))
    # THEN it should JSON response with the target gene included
    assert len(resp.json) > 0
    matching_genes = [gene_info for gene_info in resp.json if gene_info["id"] == hgnc_id]
    assert len(matching_genes) == 1
    assert "LYST" in matching_genes[0]["name"]
