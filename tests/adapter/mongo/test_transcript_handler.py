import pytest

from scout.models.hgnc_map import HgncGene

from scout.exceptions import IntegrityError

#################### HGNC transcript tests ####################


def test_insert_transcript(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for i in adapter.transcripts()) == 0

    ##WHEN inserting a transcript
    transcript_obj = {
        "ensembl_transcript_id": "ENST01",  # required
        "refseq_id": "NM_1",
        "start": 1,  # required
        "end": 10,  # required
        "is_primary": False,
        "build": "37",
    }
    obj_id = adapter.load_hgnc_transcript(transcript_obj)

    ##THEN assert that the transcript is there
    assert sum(1 for i in adapter.transcripts()) == 1
    ##THEN assert that no transcripts are in the '38' build
    assert sum(1 for i in adapter.transcripts(build="38")) == 0


def test_insert_many_transcripts(adapter):
    adapter = adapter
    ##GIVEN a empty adapter
    assert sum(1 for i in adapter.transcripts()) == 0

    transcript_objs = []
    ##WHEN inserting a bulk of transcripts
    for i in range(300):
        transcript_objs.append(
            {
                "ensembl_transcript_id": "ENST01",  # required
                "refseq_id": "NM_1",
                "start": 1,  # required
                "end": i,  # required
                "is_primary": False,
                "build": "37",
            }
        )

    result = adapter.load_transcript_bulk(transcript_objs)

    ##THEN assert that the transcripts are loaded
    assert sum(1 for i in adapter.transcripts()) == 300
    ##THEN assert that no transcripts are in the '38' build
    assert sum(1 for i in adapter.transcripts(build="38")) == 0


def test_insert_many_transcripts_duplicate(adapter):
    adapter = adapter
    ##GIVEN a empty adapter

    transcript_objs = []
    transcript_obj = {
        "_id": 1,
        "ensembl_transcript_id": "ENST01",  # required
        "refseq_id": "NM_1",
        "start": 1,  # required
        "end": 10,  # required
        "is_primary": False,
        "build": "37",
    }

    ##WHEN inserting a bulk of transcripts with same _id
    for i in range(300):
        transcript_objs.append(transcript_obj)

    ##THEN assert that IntegrityError is raised
    with pytest.raises(IntegrityError):
        result = adapter.load_transcript_bulk(transcript_objs)


def test_insert_transcripts(adapter, transcript_objs):
    adapter = adapter
    ##GIVEN a empty adapter
    assert sum(1 for i in adapter.transcripts()) == 0

    ##WHEN inserting a bulk of transcripts
    result = adapter.load_transcript_bulk(transcript_objs)

    ##THEN assert that the transcripts are loaded
    assert sum(1 for i in adapter.transcripts()) == len(transcript_objs)
    ##THEN assert that no transcripts are in the '38' build
    assert sum(1 for i in adapter.transcripts(build="38")) == 0


#################### Combined transcript/gene tests ####################


def test_insert_transcript(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for i in adapter.transcripts()) == 0
    assert sum(1 for i in adapter.all_genes()) == 0

    ##WHEN inserting a gene and some transcripts
    hgnc_id = 257
    hgnc_symbol = "ADK"
    ens_gene_id = "ENSG00000156110"
    chrom = "10"
    build = "37"

    gene_obj = dict(
        hgnc_id=hgnc_id,
        hgnc_symbol=hgnc_symbol,
        ensembl_id=ens_gene_id,
        chromosome=chrom,
        start=74151185,
        end=74709303,
        build="37",
    )

    refseq_id = "NM_006721"
    transcript_obj = {
        "hgnc_id": hgnc_id,
        "ensembl_transcript_id": "ENST01",  # required
        "refseq_id": refseq_id,
        "start": 74151185,  # required
        "end": 74709303,  # required
        "is_primary": True,
        "build": build,
    }
    gene_res = adapter.load_hgnc_gene(gene_obj)
    obj_id = adapter.load_hgnc_transcript(transcript_obj)

    ##THEN assert that when fetching the gene the transcript is added

    gene_res = adapter.hgnc_gene(hgnc_id, build=build)

    assert gene_res["hgnc_id"] == hgnc_id
    assert len(gene_res["transcripts"]) == 1
    assert gene_res["transcripts"][0]["refseq_id"] == refseq_id


def test_id_transcripts_one_nm(adapter):
    ##GIVEN a adapter with a gene and transcript
    hgnc_id = 257
    hgnc_symbol = "ADK"
    ens_gene_id = "ENSG00000156110"
    chrom = "10"
    build = "37"

    gene_obj = dict(
        hgnc_id=hgnc_id,
        hgnc_symbol=hgnc_symbol,
        ensembl_id=ens_gene_id,
        chromosome=chrom,
        start=74151185,
        end=74709303,
        build="37",
    )

    refseq_id = "NM_006721"
    transcript_obj = {
        "hgnc_id": hgnc_id,
        "ensembl_transcript_id": "ENST01",  # required
        "refseq_id": refseq_id,
        "start": 74151185,  # required
        "end": 74709303,  # required
        "is_primary": True,
        "build": build,
    }
    gene_res = adapter.load_hgnc_gene(gene_obj)
    obj_id = adapter.load_hgnc_transcript(transcript_obj)

    ##WHEN fetching the id transcript
    id_tx = list(adapter.get_id_transcripts(hgnc_id))[0]

    ##THEN assert that the transcripts are loaded
    assert id_tx == transcript_obj["ensembl_transcript_id"]


def test_id_transcripts_two_nm(adapter):
    ##GIVEN a adapter with a gene and transcript
    hgnc_id = 257
    hgnc_symbol = "ADK"
    ens_gene_id = "ENSG00000156110"
    chrom = "10"
    build = "37"

    gene_obj = dict(
        hgnc_id=hgnc_id,
        hgnc_symbol=hgnc_symbol,
        ensembl_id=ens_gene_id,
        chromosome=chrom,
        start=74151185,
        end=74709303,
        build="37",
    )

    refseq_id = "NM_006721"
    transcript_obj = {
        "hgnc_id": hgnc_id,
        "ensembl_transcript_id": "ENST01",  # required
        "refseq_id": refseq_id,
        "start": 74151185,  # required
        "end": 74709303,  # required
        "is_primary": True,
        "build": build,
    }
    gene_res = adapter.load_hgnc_gene(gene_obj)
    obj_id = adapter.load_hgnc_transcript(transcript_obj)

    refseq_id_2 = "NM_001123"
    transcript_obj_2 = {
        "hgnc_id": hgnc_id,
        "ensembl_transcript_id": "ENST02",  # required
        "refseq_id": refseq_id_2,
        "start": 75936444,  # required
        "end": 76469061,  # required
        "is_primary": False,
        "build": build,
    }
    obj_id = adapter.load_hgnc_transcript(transcript_obj_2)

    ##WHEN fetching the id transcripts
    id_tx = adapter.get_id_transcripts(hgnc_id)

    ##THEN assert that both transcripts are returned
    assert len(id_tx) == 2


def test_id_transcripts_no_refseq(adapter):
    ##GIVEN a adapter with a gene and transcripts without refseqid
    hgnc_id = 257
    hgnc_symbol = "ADK"
    ens_gene_id = "ENSG00000156110"
    chrom = "10"
    build = "37"

    gene_obj = dict(
        hgnc_id=hgnc_id,
        hgnc_symbol=hgnc_symbol,
        ensembl_id=ens_gene_id,
        chromosome=chrom,
        start=74151185,
        end=74709303,
        build="37",
    )

    # Length = 10000
    transcript_obj = {
        "hgnc_id": hgnc_id,
        "ensembl_transcript_id": "ENST01",  # required
        "refseq_id": None,
        "start": 74150000,  # required
        "end": 74160000,  # required
        "is_primary": True,
        "build": build,
    }
    gene_res = adapter.load_hgnc_gene(gene_obj)
    obj_id = adapter.load_hgnc_transcript(transcript_obj)

    # Length = 20000
    transcript_obj_2 = {
        "hgnc_id": hgnc_id,
        "ensembl_transcript_id": "ENST02",  # required
        "refseq_id": None,
        "start": 74150000,  # required
        "end": 74170000,  # required
        "is_primary": False,
        "build": build,
    }
    obj_id = adapter.load_hgnc_transcript(transcript_obj_2)

    ##WHEN fetching the id transcripts
    id_tx = list(adapter.get_id_transcripts(hgnc_id))[0]

    ##THEN assert that the longest transcript is returned
    assert id_tx == transcript_obj_2["ensembl_transcript_id"]


#################### HGNC exon tests ####################


def test_insert_exon(adapter):
    ##GIVEN a empty adapter
    assert adapter.exon(build="37") is None

    ##WHEN inserting an exon
    exon_obj = {
        "exon_id": "1-1-100",  # str(chrom-start-end)
        "chrom": "1",
        "start": 1,
        "end": 100,
        "transcript": "enst1",  # ENST ID
        "hgnc_id": 1,  # HGNC_id
        "rank": 1,  # Order of exon in transcript
        "build": "37",  # Genome build
    }
    obj_id = adapter.load_exon(exon_obj)

    ##THEN assert that there is an exon in build 37
    assert adapter.exon(build="37")
    ##THEN assert that there are no exons build 38
    assert adapter.exon(build="38") is None


def test_insert_exon_bulk(adapter):
    ##GIVEN a empty adapter
    assert adapter.exon(build="37") is None

    ##WHEN inserting a bulk of exons
    exon_bulk = []
    for i in range(1, 300):
        exon_obj = {
            "exon_id": "1-1-" + str(i),  # str(chrom-start-end)
            "chrom": "1",
            "start": 1,
            "end": i,
            "transcript": "enst1",  # ENST ID
            "hgnc_id": 1,  # HGNC_id
            "rank": i,  # Order of exon in transcript
            "build": "37",  # Genome build
        }
        exon_bulk.append(exon_obj)
    adapter.load_exon_bulk(exon_bulk)

    ##THEN assert that the transcript is there
    assert sum(1 for i in adapter.exons(build="37")) == 299
    ##THEN assert that no transcripts are in the '38' build
    assert sum(1 for i in adapter.exons(build="38")) == 0
