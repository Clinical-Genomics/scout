"""
Methods for parsing HPO terms extracted from the following file:
https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo
"""

import logging
from typing import Iterable

LOG = logging.getLogger(__name__)


def build_hpo_tree(hpo_lines):
    """Build a tree with all hpo terms

    A tree is a dictionary where all entries have children and parents

    """
    hpo_tree = {}
    hpo_tree = {term["hpo_id"]: term for term in parse_hpo_obo(hpo_lines)}
    for hpo_id in hpo_tree:
        term = hpo_tree[hpo_id]

        # Fill the children sections
        # Loop over all ancestors
        for ancestor_id in term.get("ancestors", []):
            if ancestor_id not in hpo_tree:
                LOG.debug("Term %s does not exist!", ancestor_id)
                continue
            # If there is a ancestor we collect that term
            ancestor_term = hpo_tree[ancestor_id]

            # Add a new 'children' field on the ancestor term
            if "children" not in ancestor_term:
                ancestor_term["children"] = set()

            ancestor_term["children"].add(hpo_id)

        all_ancestors = get_all_ancestors(hpo_tree, term, set())

        term["all_ancestors"] = all_ancestors

    return hpo_tree


def parse_hpo_obo(hpo_lines):
    """Parse a .obo formated hpo line"""
    term = {}
    in_term = False

    for line in hpo_lines:
        if len(line) == 0:
            continue
        line = line.rstrip()

        # [Typedef] entries are not parsed
        # Resume term parsing if a new [Term] is seen
        if line == "[Typedef]":
            in_term = False
            continue

        # New term starts with [Term]
        if line == "[Term]":
            in_term = True
            # Return previous term if it exists
            if term:
                yield term
            # Initialize empty term
            term = {}
            continue

        if not in_term:
            continue

        if line.startswith("id"):
            term["hpo_id"] = line[4:]

        elif line.startswith("name"):
            term["description"] = line[6:]

        elif line.startswith("alt_id"):
            if "aliases" not in term:
                term["aliases"] = []
            term["aliases"].append(line[8:])

        elif line.startswith("is_a"):
            if "ancestors" not in term:
                term["ancestors"] = []
            ancestor = line[6:16]
            if ancestor.startswith("HP:"):
                term["ancestors"].append(ancestor)

    if term:
        yield term


def get_all_ancestors(hpo_tree, term, res=set()):
    """Return a set with all ancestors in the tree"""

    # If we reach the top of the tree we return the result
    if term.get("ancestors", []) == []:
        return res

    if "HP:0000001" in term["ancestors"]:
        return res

    # Loop over all ancestor terms
    for ancestor_id in term["ancestors"]:
        # Add the ancestor to res
        res.add(ancestor_id)
        if ancestor_id not in hpo_tree:
            LOG.debug("Term %s does not exist!", ancestor_id)
            return res
        # If there is a ancestor we collect that term
        ancestor_term = hpo_tree[ancestor_id]
        return get_all_ancestors(hpo_tree, ancestor_term, res)


def parse_hpo_genes(hpo_lines: Iterable[str]) -> dict:
    """Parse HPO gene information.
    The first line in the genes_to_phenotype file is a header
    """
    genes = {}
    for index, line in enumerate(hpo_lines):
        if index == 0:
            continue
        if len(line) < 5:
            continue
        gene_info = parse_hpo_gene(line)
        hgnc_symbol = gene_info["hgnc_symbol"]
        description = gene_info["description"]
        hpo_term_id = gene_info["hpo_id"]

        if hgnc_symbol not in genes:
            genes[hgnc_symbol] = {"hgnc_symbol": hgnc_symbol}

        gene = genes[hgnc_symbol]
        if (
            description in ("Incomplete penetrance", "Typified by incomplete penetrance")
            or hpo_term_id == "HP:0003829"
        ):
            gene["incomplete_penetrance"] = True

    return genes


def parse_hpo_gene(hpo_line: str) -> dict:
    """Parse hpo gene information"""
    if not len(hpo_line) > 3:
        return {}
    hpo_line = hpo_line.rstrip().split("\t")
    hpo_info = {}
    hpo_info["hgnc_symbol"] = hpo_line[1]
    hpo_info["hpo_id"] = hpo_line[2]
    hpo_info["description"] = hpo_line[3]

    return hpo_info


def get_incomplete_penetrance_genes(hpo_lines: Iterable[str]) -> set:
    """Get a set with all genes that have incomplete penetrance according to HPO

    Returns a set with the hgnc symbols of all genes with incomplete penetrance
    """
    genes = parse_hpo_genes(hpo_lines)
    incomplete_penetrance_genes = set()
    for hgnc_symbol in genes:
        if genes[hgnc_symbol].get("incomplete_penetrance"):
            incomplete_penetrance_genes.add(hgnc_symbol)
    return incomplete_penetrance_genes
