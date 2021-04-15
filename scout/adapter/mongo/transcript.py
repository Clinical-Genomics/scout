import logging
from pprint import pprint as pp

from pymongo.errors import BulkWriteError, DuplicateKeyError

from scout.build.genes.exon import build_exon
from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class TranscriptHandler(object):
    def load_hgnc_transcript(self, transcript_obj):
        """Add a transcript object to the database

        Arguments:
            transcript_obj(dict)

        """
        res = self.transcript_collection.insert_one(transcript_obj)
        return res

    def load_transcript_bulk(self, transcript_objs):
        """Load a bulk of transcript objects to the database

        Arguments:
            transcript_objs(iterable(scout.models.hgnc_transcript))

        """
        LOG.info("Loading transcript bulk")
        try:
            result = self.transcript_collection.insert_many(transcript_objs)
        except (DuplicateKeyError, BulkWriteError) as err:
            raise IntegrityError(err)

        return result

    def drop_transcripts(self, build=None):
        """Delete the transcripts collection"""
        if build:
            LOG.info("Dropping the transcripts collection, build %s", build)
            self.transcript_collection.delete_many({"build": str(build)})
        else:
            LOG.info("Dropping the transcripts collection")
            self.transcript_collection.drop()

    def drop_exons(self, build=None):
        """Delete the exons collection"""
        if build:
            LOG.info("Dropping the exons collection, build %s", build)
            self.exon_collection.delete_many({"build": str(build)})
        else:
            LOG.info("Dropping the exons collection")
            self.exon_collection.drop()

    def ensembl_transcripts(self, build="37"):
        """Return a dictionary with ensembl ids as keys and transcripts as value.

        Args:
            build(str)

        Returns:
            ensembl_transcripts(dict): {<enst_id>: transcripts_obj, ...}
        """
        ensembl_transcripts = {}
        LOG.info("Fetching all transcripts")
        for transcript_obj in self.transcripts(str(build)):
            enst_id = transcript_obj["ensembl_transcript_id"]
            ensembl_transcripts[enst_id] = transcript_obj
        LOG.info("Ensembl transcripts fetched")

        return ensembl_transcripts

    def get_id_transcripts(self, hgnc_id=None, build="37", transcripts=None):
        """Return a set with identifier transcript(s)

        Choose all refseq transcripts with NM symbols, if none where found choose ONE with NR,
        if no NR choose ONE with XM. If there are no RefSeq transcripts identifiers choose the
        longest ensembl transcript.

        Args:
            hgnc_id(int)
            build(str)

        Returns:
            identifier_transcripts(set)

        """
        if not transcripts:
            LOG.debug("Fetching the id transcripts for gene %s", hgnc_id)
            if not hgnc_id:
                raise SyntaxError("Need hgnc id to fetch transcripts")
            transcripts = self.transcripts(build=str(build), hgnc_id=hgnc_id)

        identifier_transcripts = set()

        refseq_tx = None
        longest = None
        longest_length = 0
        nr = []
        xm = []
        for tx in transcripts:
            enst_id = tx["ensembl_transcript_id"]
            refseq_id = tx.get("refseq_id")
            if refseq_id:
                refseq_tx = True
                if "NM" in refseq_id:
                    identifier_transcripts.add(enst_id)
                elif "NR" in refseq_id:
                    nr.append(enst_id)
                elif "XM" in refseq_id:
                    xm.append(enst_id)
                continue

            if refseq_tx:
                continue

            tx_length = tx["end"] - tx["start"]
            if not longest:
                longest = enst_id
                longest_length = tx_length
                continue
            if tx_length > longest_length:
                longest = enst_id
                longest_length = tx_length

        if identifier_transcripts:
            return identifier_transcripts

        if nr:
            return set([nr[0]])

        if xm:
            return set([xm[0]])

        return set([longest])

    def transcripts_by_gene(self, build="37"):
        """Return a dictionary with hgnc_id as keys and a list of transcripts as value

        Args:
            build(str)

        Returns:
            hgnc_transcripts(dict)

        """
        hgnc_transcripts = {}
        LOG.info("Fetching all transcripts")
        for transcript in self.transcript_collection.find({"build": str(build)}):
            hgnc_id = transcript["hgnc_id"]
            if not hgnc_id in hgnc_transcripts:
                hgnc_transcripts[hgnc_id] = []

            hgnc_transcripts[hgnc_id].append(transcript)

        return hgnc_transcripts

    def id_transcripts_by_gene(self, build="37"):
        """Return a dictionary with hgnc_id as keys and a set of id transcripts as value

        Args:
            build(str)

        Returns:
            hgnc_id_transcripts(dict)
        """
        hgnc_id_transcripts = {}
        LOG.info("Fetching all id transcripts")
        for gene_obj in self.hgnc_collection.find({"build": str(build)}):
            hgnc_id = gene_obj["hgnc_id"]
            id_transcripts = self.get_id_transcripts(hgnc_id=hgnc_id, build=str(build))
            hgnc_id_transcripts[hgnc_id] = id_transcripts

        return hgnc_id_transcripts

    def transcripts(self, build="37", hgnc_id=None):
        """Return all transcripts.

            If a gene is specified return all transcripts for the gene

        Args:
            build(str)
            hgnc_id(int)

        Returns:
            iterable(transcript)
        """

        query = {"build": str(build)}
        if hgnc_id:
            query["hgnc_id"] = hgnc_id

        return self.transcript_collection.find(query)

    def load_exon(self, exon_obj):
        """Add a exon object to the database

        Arguments:
            exon_obj(dict)

        """
        res = self.exon_collection.insert_one(exon_obj)
        return res

    def load_exon_bulk(self, exon_objs):
        """Load a bulk of exon objects to the database

        Arguments:
            exon_objs(iterable(scout.models.hgnc_exon))

        """
        try:
            LOG.debug("Loading exon bulk")
            result = self.exon_collection.insert_many(exon_objs)
        except (DuplicateKeyError, BulkWriteError) as err:
            raise IntegrityError(err)

        return result

    def exons(self, hgnc_id=None, transcript_id=None, build=None):
        """Return all exons

        Args:
            hgnc_id(int)
            transcript_id(str)
            build(str)

        Returns:
            exons(iterable(dict))
        """
        query = {}
        if build:
            query["build"] = str(build)
        if hgnc_id:
            query["hgnc_id"] = hgnc_id
        if transcript_id:
            query["transcript_id"] = transcript_id

        return self.exon_collection.find(query)

    def exon(self, build=None):
        """Return one exon

        Args:
            build(str)

        Returns:
            exons(iterable(dict))
        """
        query = {}
        if build:
            query["build"] = str(build)

        return self.exon_collection.find_one(query)
