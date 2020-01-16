# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, jsonify, redirect, url_for, flash

from scout.server.extensions import store
from scout.server.utils import templated, public_endpoint
from . import controllers

genes_bp = Blueprint("genes", __name__, template_folder="templates")


@genes_bp.route("/genes")
@templated("genes/genes.html")
def genes():
    """Render seach box for genes."""
    query = request.args.get("query", "")
    hgnc_id = None
    if "|" in query:
        try:
            hgnc_id = int(query.split(" | ", 1)[0])
        except ValueError:
            flash("Provided gene info could not be parsed!", "warning")
    if hgnc_id:
        return redirect(url_for(".gene", hgnc_id=hgnc_id))
    gene_q = store.all_genes(limit=20)
    return dict(genes=gene_q)


@genes_bp.route("/genes/<int:hgnc_id>")
@genes_bp.route("/genes/<hgnc_symbol>")
@templated("genes/gene.html")
def gene(hgnc_id=None, hgnc_symbol=None):
    """Render information about a gene."""
    if hgnc_symbol:
        res = [gene for gene in store.hgnc_genes(hgnc_symbol)]
        if len(res) == 1:
            hgnc_id = res[0]["hgnc_id"]
        else:
            return redirect(url_for(".genes", query=hgnc_symbol))
    try:
        genes = controllers.gene(store, hgnc_id)
    except ValueError as error:
        return abort(404)

    return genes


@genes_bp.route("/api/v1/genes")
@public_endpoint
def api_genes():
    """Return JSON data about genes."""
    query = request.args.get("query")
    json_out = controllers.genes_to_json(store, query)
    return jsonify(json_out)
