import pytest

from scout.exceptions import IntegrityError
from scout.models.hgnc_map import HgncGene


#################### HGNC gene tests ####################
def test_insert_gene(adapter, parsed_gene):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting a gene

    gene_obj = HgncGene(**parsed_gene).model_dump(exclude_none=True)

    obj_id = adapter.load_hgnc_gene(gene_obj)

    ##THEN assert that the gene is there
    assert sum(1 for _ in adapter.all_genes()) == 1
    ##THEN assert that no genes are in the '38' build
    assert sum(1 for _ in adapter.all_genes(build="38")) == 0


def test_insert_many_genes(adapter, parsed_gene):
    adapter = adapter
    gene_objs = []
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting a bulk of genes
    for i in range(300):
        parsed_gene["hgnc_id"] = i
        gene_objs.append(HgncGene(**parsed_gene).model_dump(exclude_none=True))

    result = adapter.load_hgnc_bulk(gene_objs)

    ##THEN assert that the genes are loaded
    assert sum(1 for _ in adapter.all_genes()) == 300
    ##THEN assert that no genes are in the '38' build
    assert sum(1 for _ in adapter.all_genes(build="38")) == 0


def test_insert_bulk(adapter, gene_bulk):
    ## GIVEN an empty adapter and a bulk of genes
    adapter = adapter

    assert sum(1 for _ in adapter.all_genes()) == 0
    assert len(gene_bulk) > 0

    ## WHEN inserting the gene objects
    result = adapter.load_hgnc_bulk(gene_bulk)

    ##THEN assert that the genes are loaded
    assert sum(1 for _ in adapter.all_genes()) == len(gene_bulk)


def test_insert_many_genes_duplicate(adapter):
    adapter = adapter
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    gene_objs = []
    gene_obj = {"_id": 1, "hgnc_id": 1, "hgnc_symbol": "AAA", "build": "37"}

    ##WHEN inserting a bulk of genes with same _id
    for i in range(300):
        gene_objs.append(gene_obj)

    ##THEN assert that IntegrityError is raised
    with pytest.raises(IntegrityError):
        result = adapter.load_hgnc_bulk(gene_objs)


def test_get_gene(adapter):
    # adapter = real_adapter
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting a gene and fetching it
    gene_obj = {"hgnc_id": 1, "hgnc_symbol": "AAA", "build": "37"}
    adapter.load_hgnc_gene(gene_obj)

    ##THEN assert that the correct gene was fetched
    res = adapter.hgnc_gene(hgnc_identifier=gene_obj["hgnc_id"], build=gene_obj["build"])

    assert res["hgnc_id"] == gene_obj["hgnc_id"]

    ##THEN assert that there are no genes in the 38 build
    res = adapter.hgnc_gene(hgnc_identifier=gene_obj["hgnc_id"], build="38")

    assert res is None


def test_get_genes(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "AAB"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }

    adapter.load_hgnc_gene(gene_obj2)

    res = adapter.hgnc_genes(hgnc_symbol=gene_obj["hgnc_symbol"])

    ##THEN assert that the correct gene was fetched

    for result in res:
        assert result["hgnc_id"] == gene_obj["hgnc_id"]


def test_get_genes_alias(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "AAB"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }

    adapter.load_hgnc_gene(gene_obj2)

    res = adapter.hgnc_genes(hgnc_symbol="AAB")

    ##THEN assert that the correct gene was fetched

    for result in res:
        assert result["hgnc_id"] == 1


def test_get_genes_regex(real_adapter):
    adapter = real_adapter
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "BCD"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }
    adapter.load_hgnc_gene(gene_obj2)

    gene_obj3 = {
        "hgnc_id": 3,
        "hgnc_symbol": "AB",
        "build": "37",
        "aliases": ["C", "AC"],
    }

    adapter.load_hgnc_gene(gene_obj3)

    ##THEN assert that only the correct gene was fetched for a full match
    res = adapter.hgnc_genes(hgnc_symbol="AA", search=True)
    assert sum(1 for _ in res) == 1

    ##THEN assert that the correct gene was fetched
    res = adapter.hgnc_genes(hgnc_symbol="AB", search=True)
    assert sum(1 for _ in res) == 1

    ##THEN assert that the correct gene was fetched
    res = adapter.hgnc_genes(hgnc_symbol="K", search=True)
    assert sum(1 for _ in res) == 0

    ##THEN assert that the correct gene was fetched
    res = adapter.hgnc_genes(hgnc_symbol="A", search=True)
    assert sum(1 for _ in res) == 3

    # This will only work with a real pymongo adapter
    ##THEN assert that the correct gene was fetched
    res = adapter.hgnc_genes(hgnc_symbol="a", search=True)
    assert sum(1 for _ in res) == 3


def test_get_genes_per_build(real_adapter):
    adapter = real_adapter
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "BCD"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }
    adapter.load_hgnc_gene(gene_obj2)

    gene_obj3 = {
        "hgnc_id": 3,
        "hgnc_symbol": "AB",
        "build": "38",
        "aliases": ["C", "AC"],
    }
    adapter.load_hgnc_gene(gene_obj3)

    ##THEN assert default genome build is 37
    res = adapter.hgnc_genes(hgnc_symbol="AA", search=True)
    assert sum(1 for _ in res) == 1

    ##THEN assert gene is excluded when using genome build is 38
    res = adapter.hgnc_genes(hgnc_symbol="AA", build="38", search=True)
    assert sum(1 for _ in res) == 0

    ##THEN assert that build==37 excludes 38 variants when using regex
    res = adapter.hgnc_genes(hgnc_symbol="A", build="37", search=True)
    assert sum(1 for _ in res) == 2

    ##THEN assert that build==38 excludes 37 variants when using regex
    res = adapter.hgnc_genes(hgnc_symbol="A", build="38", search=True)
    assert sum(1 for _ in res) == 1

    ##THEN assert that build==all includes both 37 and 38 variants when using regex
    res = adapter.hgnc_genes(hgnc_symbol="A", build="all", search=True)
    assert sum(1 for _ in res) == 3


def test_get_all_genes(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "AAB"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }

    adapter.load_hgnc_gene(gene_obj2)

    res = adapter.all_genes()

    ##THEN assert that the correct number of genes where fetched
    assert sum(1 for _ in res) == 2


def test_hgnc_gene_caption(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ## WHEN inserting a gene with all caption keys
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "AAB"],
        "start": 1,
        "end": 100,
        "chromosome": "X",
        "description": "An A-rich gene",
    }
    adapter.load_hgnc_gene(gene_obj)

    ## THEN a proper caption is returned
    caption = adapter.hgnc_gene_caption(1, "37")
    assert caption
    assert caption["hgnc_symbol"] == gene_obj["hgnc_symbol"]
    assert caption["chromosome"] == gene_obj["chromosome"]

    ### WHEN inserting a gene witout certain caption fields
    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }
    adapter.load_hgnc_gene(gene_obj2)

    caption = adapter.hgnc_gene_caption(2, "37")
    ## THEN a proper caption is returned, but not including
    ## fields that were missing
    assert caption
    assert caption["hgnc_symbol"] == gene_obj2["hgnc_symbol"]
    assert caption.get("chromosome") == None


def test_drop_genes(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "AAB"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }

    adapter.load_hgnc_gene(gene_obj2)

    res = adapter.all_genes()
    assert sum(1 for _ in res) == 2

    ##THEN assert that the correct number of genes where fetched
    adapter.drop_genes()
    res = adapter.all_genes()
    assert sum(1 for _ in res) == 0


def test_hgncid_to_gene(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "AAB"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }

    adapter.load_hgnc_gene(gene_obj2)

    res = adapter.all_genes()
    assert sum(1 for _ in res) == 2

    ##THEN assert that the correct number of genes where fetched
    res = adapter.hgncid_to_gene()
    assert gene_obj["hgnc_id"] in res
    assert gene_obj2["hgnc_id"] in res

    first_gene = res[gene_obj["hgnc_id"]]

    assert first_gene["hgnc_id"] == gene_obj["hgnc_id"]


def test_hgnc_symbol_to_gene(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting two genes and fetching one
    gene_obj = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "build": "37",
        "aliases": ["AAA", "AAB"],
    }
    adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        "hgnc_id": 2,
        "hgnc_symbol": "AA",
        "build": "37",
        "aliases": ["AA", "AB"],
    }

    adapter.load_hgnc_gene(gene_obj2)

    res = adapter.all_genes()
    assert sum(1 for _ in res) == 2

    ##THEN assert that the correct number of genes where fetched
    res = adapter.hgncsymbol_to_gene()
    assert gene_obj["hgnc_symbol"] in res
    assert gene_obj2["hgnc_symbol"] in res


def test_gene_by_symbol_or_aliases(adapter, parsed_gene):
    """Test the function that given a gene symbol returns either the official gene with that symbol
    or all genes that have the gene as alias"""

    # GIVEN a database containing a gene
    adapter.load_hgnc_gene(parsed_gene)

    # THEN using the function to search the gene by symbol should return a list with the gene
    result = adapter.gene_by_symbol_or_aliases(symbol=parsed_gene["hgnc_symbol"])
    assert type(result) == list
    assert len(result) == 1

    # GIVEN a gene symbol not found in "hgnc_symbol" field of any gene
    # The function should return a pymongo iterable (results of searching genes by alias)
    result = adapter.gene_by_symbol_or_aliases(symbol="FOO")
    assert type(result) != list


def test_ensembl_to_hgnc_id_mapping(adapter, parsed_gene):
    """Test the function that maps Ensembl gene IDs to HGNC gene IDs."""

    # GIVEN a database containing a gene
    adapter.load_hgnc_gene(parsed_gene)

    # WHEN using the mapping function
    result = adapter.ensembl_to_hgnc_id_mapping()

    # THEN it should return the expected result
    assert result == {parsed_gene["ensembl_id"]: parsed_gene["hgnc_id"]}


def test_hgnc_symbol_ensembl_id_mapping(adapter, parsed_gene):
    """Test the function that maps HGNC symbols to Ensembl gene IDs."""

    # GIVEN a database containing a gene
    adapter.load_hgnc_gene(parsed_gene)

    # WHEN using the mapping function
    result = adapter.hgnc_symbol_ensembl_id_mapping()

    # THEN it should return the expected result
    assert result == {parsed_gene["hgnc_symbol"]: parsed_gene["ensembl_id"]}


#################### HGNC transcript tests ####################


def test_insert_transcript(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

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
    assert sum(1 for _ in adapter.all_genes()) == 1
    ##THEN assert that no transcripts are in the '38' build
    assert sum(1 for _ in adapter.all_genes(build="38")) == 0


def test_insert_many_transcripts(adapter):
    adapter = adapter
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.all_genes()) == 0

    transcript_objs = []
    ##WHEN inserting a bulk of transcripts
    for i in range(300):
        transcript_objs.append(
            {
                "ensembl_transcript_id": "ENST01",  # required
                "refseq_id": "NM_1",
                "start": 1,  # required
                "end": 10,  # required
                "is_primary": False,
                "build": "37",
            }
        )

    result = adapter.load_transcript_bulk(transcript_objs)

    ##THEN assert that the transcripts are loaded
    assert sum(1 for _ in adapter.transcripts()) == 300
    ##THEN assert that no transcripts are in the '38' build
    assert sum(1 for _ in adapter.all_genes(build="38")) == 0


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
    assert sum(1 for _ in adapter.all_genes()) == 0

    ##WHEN inserting a bulk of transcripts
    result = adapter.load_transcript_bulk(transcript_objs)

    ##THEN assert that the transcripts are loaded
    assert sum(1 for _ in adapter.transcripts()) == len(transcript_objs)
    ##THEN assert that no transcripts are in the '38' build
    assert sum(1 for _ in adapter.all_genes(build="38")) == 0


#################### Combined transcript/gene tests ####################


def test_insert_transcript(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for _ in adapter.transcripts()) == 0
    assert sum(1 for _ in adapter.all_genes()) == 0

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
