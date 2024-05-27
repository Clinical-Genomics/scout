import logging

import intervaltree
from pymongo.errors import BulkWriteError, DuplicateKeyError

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class GeneHandler(object):
    def load_hgnc_gene(self, gene_obj):
        """Add a gene object with transcripts to the database

        Arguments:
            gene_obj(dict)

        """
        # LOG.debug("Loading gene %s, build %s into database" %
        #             (gene_obj['hgnc_symbol'], gene_obj['build']))
        res = self.hgnc_collection.insert_one(gene_obj)
        # LOG.debug("Gene saved")
        return res

    def load_hgnc_bulk(self, gene_objs):
        """Load a bulk of hgnc gene objects

        Raises IntegrityError if there are any write concerns

        Args:
            gene_objs(iterable(scout.models.hgnc_gene))

        Returns:
            result (pymongo.results.InsertManyResult)
        """

        LOG.info("Loading gene bulk with length %s", len(gene_objs))
        try:
            result = self.hgnc_collection.insert_many(gene_objs)
        except (DuplicateKeyError, BulkWriteError) as err:
            raise IntegrityError(err)

        return result

    def hgnc_gene_caption(self, hgnc_identifier, build=None):
        """Fetch the current hgnc gene symbol and similar caption info for a gene in a lightweight dict
        Avoid populating transcripts, exons etc that would be added on a full gene object. Use hgnc_gene() if
        you need to use those.

        Args:
            hgnc_identifier(int)
            build(str or None)

        Returns:
            gene_caption(dict): light pymongo document with keys "hgnc_symbol", "description", "chromosome", "start", "end".
        """

        query = {"hgnc_id": int(hgnc_identifier)}

        if build in ["37", "38"]:
            query["build"] = build

        projection = {}  # fields to return in query results
        for item in ["hgnc_id", "hgnc_symbol", "description", "chromosome", "start", "end"]:
            projection[item] = 1

        return self.hgnc_collection.find_one(query, projection)

    def hgnc_gene(self, hgnc_identifier, build="37"):
        """Fetch a hgnc gene

        Args:
            hgnc_identifier(int)
            build(str)

        Returns:
            gene_obj(HgncGene)
        """
        if build:
            build = str(build)
        if not build in ["37", "38"]:
            build = "37"
        query = {}
        try:
            # If the identifier is a integer we search for hgnc_id
            hgnc_identifier = int(hgnc_identifier)
            query["hgnc_id"] = hgnc_identifier
        except ValueError:
            # Else we seach for a hgnc_symbol
            query["hgnc_symbol"] = hgnc_identifier

        query["build"] = build
        gene_obj = self.hgnc_collection.find_one(query)
        if not gene_obj:
            return None

        # Add the transcripts:
        transcripts = []
        tx_objs = self.transcripts(build=build, hgnc_id=gene_obj["hgnc_id"])
        nr_tx = sum(1 for i in self.transcripts(build=build, hgnc_id=gene_obj["hgnc_id"]))
        if nr_tx > 0:
            for tx in tx_objs:
                transcripts.append(tx)
        gene_obj["transcripts"] = transcripts

        return gene_obj

    def hgnc_id(self, hgnc_symbol, build="37"):
        """Query the genes with a hgnc symbol and return the hgnc id

        Args:
            hgnc_symbol(str)
            build(str)

        Returns:
            hgnc_id(int)
        """
        # LOG.debug("Fetching gene %s", hgnc_symbol)
        query = {"hgnc_symbol": hgnc_symbol, "build": str(build)}
        projection = {"hgnc_id": 1, "_id": 0}
        res = self.hgnc_collection.find(query, projection)
        for gene in res:
            return gene["hgnc_id"]

        return None

    def hgnc_genes(self, hgnc_symbol, build="37", search=False):
        """Fetch all hgnc genes that match a hgnc symbol

        Check both hgnc_symbol and aliases

        Args:
            hgnc_symbol(str)
            build(str): The build in which to search
            search(bool): if partial searching should be used

        Returns:
            pymongo.cursor
        """
        LOG.debug("Fetching genes with symbol %s" % hgnc_symbol)
        build_query = {}
        if str(build) in ["37", "38"]:
            build_query["build"] = str(build)

        if search:
            # first search for a full match
            query_full_match = {
                **self.get_query_alias_or_id(hgnc_symbol, build),
                **build_query,
            }
            nr_genes = self.nr_genes(query=query_full_match)
            if nr_genes != 0:
                return self.hgnc_collection.find(query_full_match)

            return self.hgnc_collection.find(
                {"aliases": {"$regex": hgnc_symbol, "$options": "i"}, **build_query}
            )
        return self.hgnc_collection.find({"aliases": hgnc_symbol, **build_query})

    def get_query_alias_or_id(self, hgnc_symbol, build):
        """Return query to search for hgnc-symbol or aliases"""
        query = {
            "$or": [
                {"aliases": hgnc_symbol},
                {"hgnc_id": int(hgnc_symbol) if hgnc_symbol.isdigit() else None},
            ],
        }
        if build in ["37", "38"]:
            query["build"] = str(build)
        return query

    def all_genes(self, build=None, add_transcripts=False, limit=100000):
        """Fetch all hgnc genes

        Args:
            build(str)
            add_transcripts(bool): If tx information should be added
            limit(int): If only a part of the genes should be added


            Returns:
                genes(iterable):
                limit(int): Maximum number of returned
        """
        build = build or "37"
        if build == "GRCh38":
            build = "38"

        LOG.info("Fetching all genes")

        hgnc_tx = {}
        if add_transcripts:
            LOG.info("Adding transcripts")
            for tx in self.transcripts(build=str(build)):
                hgnc_id = tx["hgnc_id"]
                if not hgnc_id in hgnc_tx:
                    hgnc_tx[hgnc_id] = []
                hgnc_tx[hgnc_id].append(tx)

        for i, gene_obj in enumerate(self.hgnc_collection.find({"build": str(build)})):
            if i > limit:
                break
            if add_transcripts:
                hgnc_id = gene_obj["hgnc_id"]
                tx_objs = hgnc_tx.get(hgnc_id)
                gene_obj["ens_transcripts"] = tx_objs
            yield gene_obj

    def nr_genes(self, build=None, query=None):
        """Return the number of hgnc genes in collection

        If build is used, return the number of genes of a certain build

        Args:
            build(str): geneome build. '37' or '38'

        Returns:
            result()
        """
        query = query or {}
        if build:
            LOG.debug("Fetching all genes from build %s", build)
            query["build"] = str(build)
        else:
            LOG.debug("Fetching all genes")

        nr = 0
        for nr, gene in enumerate(self.hgnc_collection.find(query), 1):
            pass
        return nr

    def drop_genes(self, build=None):
        """Delete the genes collection"""
        if build:
            LOG.info("Dropping the hgnc_gene collection, build %s", build)
            self.hgnc_collection.delete_many({"build": str(build)})
        else:
            LOG.info("Dropping the hgnc_gene collection")
            self.hgnc_collection.drop()

    def hgncid_to_gene(self, build="37", genes=None):
        """Return a dictionary with hgnc_id as key and gene_obj as value

        The result will have ONE entry for each gene in the database.
        (For a specific build)

        Args:
            build(str):
            genes(iterable(scout.models.HgncGene)):

        Returns:
            hgnc_dict(dict): {<hgnc_id(int)>: <gene(dict)>}

        """
        hgnc_dict = {}
        LOG.info("Building hgncid_to_gene")
        if not genes:
            genes = self.hgnc_collection.find({"build": str(build)})

        for gene_obj in genes:
            hgnc_dict[gene_obj["hgnc_id"]] = gene_obj

        return hgnc_dict

    def hgncsymbol_to_gene(self, build="37", genes=None):
        """Return a dictionary with hgnc_symbol as key and gene_obj as value

        The result will have ONE entry for each gene in the database.
        (For a specific build)

        Args:
            build(str)
            genes(iterable(scout.models.HgncGene)):

        Returns:
            hgnc_dict(dict): {<hgnc_symbol(str)>: <gene(dict)>}

        """
        hgnc_dict = {}
        LOG.info("Building hgncsymbol_to_gene")
        if not genes:
            genes = self.hgnc_collection.find({"build": str(build)})

        for gene_obj in genes:
            hgnc_dict[gene_obj["hgnc_symbol"]] = gene_obj
        LOG.info("All genes fetched")
        return hgnc_dict

    def gene_by_symbol_or_aliases(self, symbol, build=None):
        """Return an iterable with only one gene when gene with a given symbol if found
           or a cursor with genes where the provided symbol is among the aliases.
        Args:
            symbol(str)
            build(str or None)

        Returns:
            res(list or pymongo.Cursor(dict)): return a list with one gene or a cursor with several gene dictionaries
        """
        query = {"hgnc_symbol": symbol}
        if build:
            query["build"] = str(build)

        res = self.hgnc_collection.find_one(query)
        if res:
            return [res]

        return self.gene_aliases(symbol, build=build)

    def gene_aliases(self, symbol, build="37"):
        """Return an iterable with hgnc_genes which have the provided symbol in the gene aliases
        Args:
            symbol(str)
            build(str)

        Returns:
            res(pymongo.Cursor(dict))
        """
        res = self.hgnc_collection.find({"aliases": symbol, "build": str(build)})
        return res

    def genes_by_alias(self, build="37", genes=None):
        """Return a dictionary with hgnc symbols as keys and a list of hgnc ids
             as value.

        If a gene symbol is listed as primary the list of ids will only consist
        of that entry if not the gene can not be determined so the result is a list
        of hgnc_ids

        Args:
            build(str)
            genes(iterable(scout.models.HgncGene)):

        Returns:
            alias_genes(dict): {<hgnc_alias>: {'true': <hgnc_id>, 'ids': {<hgnc_id_1>, <hgnc_id_2>, ...}}}
        """
        LOG.info("Fetching all genes by alias")
        # Collect one entry for each alias symbol that exists
        alias_genes = {}
        # Loop over all genes
        if not genes:
            genes = self.hgnc_collection.find({"build": str(build)})

        for gene in genes:
            # Collect the hgnc_id
            hgnc_id = gene["hgnc_id"]
            # Collect the true symbol given by hgnc
            hgnc_symbol = gene["hgnc_symbol"]
            # Loop aver all aliases
            for alias in gene["aliases"]:
                true_id = None
                # If the alias is the same as hgnc symbol we know the true id
                if alias == hgnc_symbol:
                    true_id = hgnc_id
                # If the alias is already in the list we add the id
                if alias in alias_genes:
                    alias_genes[alias]["ids"].add(hgnc_id)
                    if true_id:
                        alias_genes[alias]["true"] = hgnc_id
                else:
                    alias_genes[alias] = {"true": hgnc_id, "ids": set([hgnc_id])}

        return alias_genes

    def ensembl_to_hgnc_mapping(self):
        """Return a dictionary with Ensembl ids as keys and hgnc_ids as values

        Returns:
            mapping(dict): {"ENSG00000121410":"A1BG", ...}
        """
        pipeline = [{"$group": {"_id": {"ensembl_id": "$ensembl_id", "hgnc_id": "$hgnc_id"}}}]
        result = self.hgnc_collection.aggregate(pipeline)
        mapping = {res["_id"]["ensembl_id"]: res["_id"]["hgnc_id"] for res in result}
        return mapping

    def ensembl_genes(self, build=None, add_transcripts=False, id_transcripts=False):
        """Return a dictionary with ensembl ids as keys and gene objects as value.

        Args:
            build(str)
            transcripts(bool): If transcripts should be included

        Returns:
            genes(dict): {<ensg_id>: gene_obj, ...}
        """
        build = build or "37"
        genes = {}
        if id_transcripts:
            add_transcripts = True

        for gene_obj in self.all_genes(build=build, add_transcripts=add_transcripts):
            ensg_id = gene_obj["ensembl_id"]
            hgnc_id = gene_obj["hgnc_id"]
            transcript_objs = gene_obj.get("ens_transcripts")
            if id_transcripts and transcript_objs:
                gene_obj["id_transcripts"] = self.get_id_transcripts(
                    build=build, transcripts=transcript_objs
                )
            genes[ensg_id] = gene_obj

        LOG.info("Ensembl genes fetched")

        return genes

    def add_hgnc_id(self, genes):
        """Add the correct hgnc id to a set of genes with hgnc symbols

        Args:
            genes(list(dict)): A set of genes with hgnc symbols only

        """
        genes_by_alias = self.genes_by_alias()

        for gene in genes:
            id_info = genes_by_alias.get(gene["hgnc_symbol"])
            if not id_info:
                LOG.warning("Gene %s does not exist in scout", gene["hgnc_symbol"])
                continue
            gene["hgnc_id"] = id_info["true"]
            if not id_info["true"]:
                if len(id_info["ids"]) > 1:
                    LOG.warning(
                        "Gene %s has ambiguous value, please choose one hgnc id in result",
                        gene["hgnc_symbol"],
                    )
                gene["hgnc_id"] = ",".join([str(hgnc_id) for hgnc_id in id_info["ids"]])

    def get_coding_intervals(self, build="37", genes=None):
        """Return a dictionary with chromosomes as keys and interval trees as values

        Each interval represents a coding region of overlapping genes.

        Args:
            build(str): The genome build
            genes(iterable(scout.models.HgncGene)):

        Returns:
            intervals(dict): A dictionary with chromosomes as keys and overlapping genomic intervals as values
        """
        intervals = {}
        if not genes:
            genes = self.all_genes(build=build)
        LOG.info("Building interval trees...")
        for i, hgnc_obj in enumerate(genes):
            chrom = hgnc_obj["chromosome"]
            start = max((hgnc_obj["start"] - 5000), 1)
            end = hgnc_obj["end"] + 5000

            # If this is the first time a chromosome is seen we create a new
            # interval tree with current interval
            if chrom not in intervals:
                intervals[chrom] = intervaltree.IntervalTree()
                intervals[chrom].addi(start, end, i)
                continue

            res = intervals[chrom].overlap(start, end)

            # If the interval did not overlap any other intervals we insert it and continue
            if not res:
                intervals[chrom].addi(start, end, i)
                continue

            # Loop over the overlapping intervals
            for interval in res:
                # Update the positions to new max and mins
                if interval.begin < start:
                    start = interval.begin

                if interval.end > end:
                    end = interval.end

                # Delete the old interval
                intervals[chrom].remove(interval)

            # Add the new interval consisting och the overlapping ones
            intervals[chrom].addi(start, end, i)

        return intervals
