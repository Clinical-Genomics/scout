"""
head develop/mip_references/grch37_scout_exons_-2017-01-.bed
13	22255179	22255286	13-22255181-22255284	NM_002010	3687	FGF9
1	154306977	154307069	1-154306979-154307067	NM_001005855,NM_020452	13534,13534	ATP8B2,ATP8B2
6	20739748	20739848	6-20739750-20739846	NM_017774,XM_005249202	21050,21050	CDKAL1,CDKAL1
2	228169699	228169801	2-228169701-228169799	NM_000091	2204	COL4A3
20	49557664	49557748	20-49557666-49557746	XM_005260600	3005	DPM1
10	79628885	79628957	10-79628887-79628955	NM_004747	2904	DLG5
1	228112962	228113222	1-228112964-228113220	NM_003395	12778	WNT9A
3	48488247	48488498	3-48488249-48488496	NM_130384,NM_032166	33499,33499	ATRIP,ATRIP
7	65413656	65413769	7-65413658-65413767	NM_173517	21492	VKORC1L1
5	159776172	159776790	5-159776174-159776788	NM_031908	14325	C1QTNF2
"""
import logging

LOG = logging.getLogger(__name__)


def export_gene_exons(adapter, hgnc_id, build="37"):
    """Export all exons from one gene

    Args:
        adapter(scout.adapter.MongoAdapter)
        hgnc_id(int): hgnc ID of a gene
        build(str): "37" or "38"

    Yields:
        printlines(str): formatted like this: Chrom\tStart\tEnd\tExonId\tTranscripts\tHgncIDs\tHgncSymbols

    """
    gene_caption = adapter.hgnc_gene_caption(hgnc_id, build)
    if gene_caption is None:
        LOG.warning(f"Could't find a gene with HGNC id '{hgnc_id}' in Scout database.")
        return
    query = {"hgnc_id": hgnc_id, "build": build}
    result = adapter.exon_collection.find(query)
    print_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}"

    for exon in result:
        yield print_line.format(
            exon["chrom"],
            exon["start"],
            exon["end"],
            exon["exon_id"],
            exon["transcript"],
            hgnc_id,
            gene_caption["hgnc_symbol"],
        )


def export_exons(adapter, build="37"):
    """Export all exons of a certain build from the database

    Args:
        adapter(scout.adapter.MongoAdapter)
        build(str): "37" or "38"

    Yields:
        transcript(scout.models.Transcript)
    """
    ens_transcripts = adapter.ensembl_transcripts(build=build)

    hgnc_genes = {}
    for gene_obj in adapter.all_genes(build=build):
        hgnc_genes[gene_obj["hgnc_id"]] = gene_obj

    exons = {}
    for exon_obj in adapter.exons(build=build):
        ens_tx_id = exon_obj["transcript"]
        exon_id = exon_obj["exon_id"]
        tx_obj = ens_transcripts[ens_tx_id]
        hgnc_id = tx_obj["hgnc_id"]

        if not exon_id in exons:
            exon_obj["exon_transcripts"] = []
            exon_obj["hgnc_ids"] = []
            exons[exon_id] = exon_obj

        tx_ids = []
        hgnc_ids = []

        tx_refseq = tx_obj.get("refseq_identifiers", [])
        for refseq_id in tx_refseq:
            exons[exon_id]["exon_transcripts"].append(refseq_id)
            exons[exon_id]["hgnc_ids"].append(hgnc_id)
        if not tx_refseq:
            exons[exon_id]["exon_transcripts"].append(ens_tx_id)
            exons[exon_id]["hgnc_ids"].append(hgnc_id)

    print_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}"
    for exon_id in exons:
        exon = exons[exon_id]
        hgnc_ids = exon["hgnc_ids"]
        hgnc_symbols = []
        for hgnc_id in hgnc_ids:
            hgnc_symbols.append(hgnc_genes.get(hgnc_id, {}).get("hgnc_symbol"))
        transcripts_str = ",".join(exon["exon_transcripts"])
        hgncids_str = ",".join([str(i) for i in hgnc_ids])
        hgncsymbols_str = ",".join(hgnc_symbols)

        yield print_line.format(
            exon["chrom"],
            exon["start"],
            exon["end"],
            exon_id,
            transcripts_str,
            hgncids_str,
            hgncsymbols_str,
        )
