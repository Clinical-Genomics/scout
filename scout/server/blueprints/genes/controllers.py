# -*- coding: utf-8 -*-
from pprint import pprint as pp

from scout.server.links import add_gene_links, add_tx_links, omim


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


def genes_to_json(store, query):
    """Fetch matching genes and convert to JSON."""
    gene_query = store.hgnc_genes(query, search=True)
    json_terms = [
        {
            "name": "{} | {} ({})".format(
                gene["hgnc_id"], gene["hgnc_symbol"], ", ".join(gene["aliases"])
            ),
            "id": gene["hgnc_id"],
        }
        for gene in gene_query
    ]
    return json_terms
