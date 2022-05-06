# -*- coding: utf-8 -*-
from flask import flash, redirect, url_for

from scout.server.links import add_gene_links, add_tx_links, omim
from scout.server.utils import document_generated


def genes(store, query):
    """Creates content for the genes template

    Args:
        store (scout.adapter.MongoAdapter)
        query (string)
    Returns:
        data (dict)
    """
    hgnc_id = None
    if "|" in query:
        try:
            hgnc_id = int(query.split(" | ", 1)[0])
        except ValueError:
            flash("Provided gene info could not be parsed!", "warning")
    if hgnc_id:
        return redirect(url_for(".gene", hgnc_id=hgnc_id))

    nr_genes_37 = store.nr_genes(build="37")
    nr_genes_38 = store.nr_genes(build="38")
    genes_subset = list(store.all_genes(add_transcripts=False, limit=20))
    last_inserted_gene = store.hgnc_collection.find({}).sort("_id", -1).limit(1)
    last_updated = document_generated(last_inserted_gene[0]["_id"] if last_inserted_gene else None)
    return dict(genes=genes_subset, last_updated=last_updated, nr_genes=(nr_genes_37, nr_genes_38))


def gene(store, hgnc_id):
    """Parse information about a gene."""
    res = {
        "builds": {"37": None, "38": None},
        "symbol": None,
        "description": None,
        "ensembl_id": None,
        "record": None,
    }

    for build in res["builds"]:
        record = store.hgnc_gene(hgnc_id, build=build)
        if record:

            record["position"] = "{this[chromosome]}:{this[start]}-{this[end]}".format(this=record)
            res["aliases"] = record["aliases"]
            res["hgnc_id"] = record["hgnc_id"]
            res["description"] = record["description"]
            res["builds"][build] = record
            res["symbol"] = record["hgnc_symbol"]
            res["description"] = record["description"]
            res["entrez_id"] = record.get("entrez_id")
            res["pli_score"] = record.get("pli_score")

            add_gene_links(record, int(build))

            res["omim_id"] = record.get("omim_id")
            res["incomplete_penetrance"] = record.get("incomplete_penetrance", False)
            res["inheritance_models"] = record.get("inheritance_models", [])
            for transcript in record["transcripts"]:
                transcript["position"] = "{this[chrom]}:{this[start]}-{this[end]}".format(
                    this=transcript
                )
                add_tx_links(transcript, build, record["hgnc_symbol"])

            for phenotype in record.get("phenotypes", []):
                phenotype["omim_link"] = omim(phenotype.get("mim_number"))

            if not res["record"]:
                res["record"] = record

    # If none of the genes where found
    if not any(res.values()):
        raise ValueError

    return res


def genes_to_json(store, query, build):
    """Fetch matching genes and convert to JSON."""
    gene_query = store.hgnc_genes(query, build, search=True)
    json_terms = {
        gene["hgnc_id"]: {
            "name": "{} | {} ({})".format(
                gene["hgnc_id"], gene["hgnc_symbol"], ", ".join(gene["aliases"])
            ),
            "id": gene["hgnc_id"],
        }
        for gene in gene_query
    }
    return list(json_terms.values())
