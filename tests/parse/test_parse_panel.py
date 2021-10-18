import datetime

from scout.parse.panel import get_panel_info, parse_gene, parse_gene_panel, parse_genes
from scout.utils.handle import get_file_handle


def test_parse_panel_info_no_info():
    ## GIVEN no information at all
    panel_lines = []
    ## WHEN parsing the information
    panel_info = get_panel_info(panel_lines)
    ## THEN assert that no information except a date is returned
    for key in panel_info:
        if key != "date":
            assert panel_info[key] is None
        else:
            assert type(panel_info[key]) is type(datetime.datetime.now())


def test_parse_panel_info_lines():
    ## GIVEN a panel with some info
    panel_lines = [
        "##panel_id=panel1",
        "##institute=cust000",
        "##version=1.0",
        "##date=2016-12-09",
        "##display_name=Test panel",
        "#hgnc_id\thgnc_symbol",
        "7481\tMT-TF",
    ]
    ## WHEN parsing the information
    panel_info = get_panel_info(panel_lines)
    ## THEN assert that no information except a date is returned
    for key in panel_info:
        if key == "panel_id":
            assert panel_info[key] == "panel1"
        elif key == "institute":
            assert panel_info[key] == "cust000"
        elif key == "version":
            assert panel_info[key] == "1.0"
        elif key == "display_name":
            assert panel_info[key] == "Test panel"
        elif key == "date":
            assert type(panel_info[key]) is type(datetime.datetime.now())


def test_parse_panel_file(panel_handle):
    ## GIVEN a panel with some info
    panel_lines = panel_handle
    ## WHEN parsing the information
    panel_info = get_panel_info(panel_lines)
    ## THEN assert that no information except a date is returned
    for key in panel_info:
        if key == "panel_id":
            assert panel_info[key] == "panel1"
        elif key == "institute":
            assert panel_info[key] == "cust000"
        elif key == "version":
            assert panel_info[key] == "1.0"
        elif key == "display_name":
            assert panel_info[key] == "Test panel"
        elif key == "date":
            assert type(panel_info[key]) is type(datetime.datetime.now())


def test_parse_minimal_gene():
    ## GIVEN minimal gene line and header
    header = ["hgnc_id"]
    gene_line = ["10"]
    gene_info = dict(zip(header, gene_line))
    ## WHEN parsing the genes
    gene = parse_gene(gene_info)
    ## THEN assert that the gene is correctly parsed

    assert gene["hgnc_id"] == 10


def test_parse_gene():
    ## GIVEN gene line and header
    header = [
        "hgnc_id",
        "hgnc_symbol",
        "disease_associated_transcripts",
        "reduced_penetrance",
        "genetic_disease_models",
        "mosaicism",
        "database_entry_version",
    ]
    hgnc_id = "10"
    hgnc_symbol = "hello"
    transcripts = "a,b,c"
    penetrance = "YES"
    models = "AR,AD"
    mosaicism = ""
    version = ""

    gene_line = [
        hgnc_id,
        hgnc_symbol,
        transcripts,
        penetrance,
        models,
        mosaicism,
        version,
    ]
    gene_info = dict(zip(header, gene_line))

    ## WHEN parsing the genes
    gene = parse_gene(gene_info)
    ## THEN assert that the gene is correctly parsed
    assert gene["hgnc_id"] == int(hgnc_id)
    assert gene["hgnc_symbol"] == hgnc_symbol
    assert gene["transcripts"] == transcripts.split(",")
    assert gene["inheritance_models"] == models.split(",")
    assert gene["reduced_penetrance"] is True if penetrance else False
    assert gene["mosaicism"] is False
    assert gene["database_entry_version"] == version

    ## WHEN alternative transcript index name
    gene_info.pop("disease_associated_transcripts")
    gene_info["disease_associated_transcript"] = transcripts
    ## THEN transcript asserts same
    gene = parse_gene(gene_info)
    assert gene["transcripts"] == transcripts.split(",")
    ## WHEN alternative transcript index name
    gene_info.pop("disease_associated_transcript")
    gene_info["transcripts"] = transcripts
    ## THEN transcript asserts same
    gene = parse_gene(gene_info)
    assert gene["transcripts"] == transcripts.split(",")


def test_parse_panel_lines():
    ## GIVEN a iterable with panel lines
    panel_lines = [
        "##panel_id=panel1",
        "##institute=cust000",
        "##version=1.0",
        "##date=2016-12-09",
        "##display_name=Test panel",
        "#hgnc_id\thgnc_symbol\tdisease_associated_transcripts\treduced_penet"
        "rance\tgenetic_disease_models\tmosaicism\tdatabase_entry_version\tor"
        "iginal_hgnc",
        "7481\tMT-TF\t\t\t\t\t\tMT-TF\n",
    ]
    nr_genes = len([line for line in panel_lines if not line.startswith("#")])

    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)

    ## THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes

    ## THEN assert that some genes exists in the panel
    for gene in genes:
        assert gene["hgnc_symbol"]
        assert gene["hgnc_id"]


def test_parse_panel_doublette():
    ## GIVEN a iterable with panel lines where one gene occurs twice
    panel_lines = [
        "#hgnc_id\thgnc_symbol\tdisease_associated_transcripts\treduced_penet"
        "rance\tgenetic_disease_models\tmosaicism\tdatabase_entry_version\tor"
        "iginal_hgnc",
        "7481\tMT-TF\t\t\t\t\t\tMT-TF\n" "7481\tMT-TF\t\t\t\t\t\tMT-TF\n",
    ]
    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)

    ## THEN that the gene is only occuring once
    assert len(genes) == 1


def test_parse_panel_genes(panel_1_file):
    # GIVEN a gene panel file
    nr_genes = 0
    with open(panel_1_file, "r") as f:
        for line in f:
            if not line.startswith("#"):
                nr_genes += 1

    # WHEN parsing the panel of genes
    f = get_file_handle(panel_1_file)
    genes = parse_genes(f)

    # THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes

    # THEN assert that some genes exists in the panek
    for gene in genes:
        assert gene["hgnc_symbol"]
        assert gene["hgnc_id"]


def test_get_full_list_panel(panel_info):
    panel_1_file = panel_info["file"]
    nr_genes = 0
    with open(panel_1_file, "r") as f:
        for line in f:
            if not line.startswith("#"):
                nr_genes += 1

    panel = parse_gene_panel(
        path=panel_info["file"],
        institute=panel_info["institute"],
        panel_id=panel_info["panel_name"],
        panel_type=panel_info["type"],
        date=panel_info["date"],
        version=panel_info["version"],
        display_name=panel_info["full_name"],
    )

    assert panel["panel_id"] == panel_info["panel_name"]
    assert len(panel["genes"]) == nr_genes
    assert panel["date"] == panel_info["date"]
    assert panel["institute"] == panel_info["institute"]


def test_parse_minimal_panel_lines_id():
    ## GIVEN a iterable with panel lines
    panel_lines = ["1"]
    nr_genes = len([line for line in panel_lines if not line.startswith("#")])

    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)

    ## THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes

    ## THEN assert that some genes exists in the panel
    for gene in genes:
        assert gene["hgnc_id"] == 1
        assert gene.get("hgnc_symbol") is None


def test_parse_minimal_panel_lines_symbol():
    ## GIVEN a iterable with panel lines
    panel_lines = ["ADK"]
    nr_genes = len([line for line in panel_lines if not line.startswith("#")])

    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)

    ## THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes

    ## THEN assert that some genes exists in the panel
    for gene in genes:
        assert gene.get("hgnc_id") is None
        assert gene.get("hgnc_symbol") == "ADK"


def test_parse_panel_lines_excel_export():
    ## GIVEN a iterable with panel lines
    panel_lines = ["hgnc_id;hgnc_symbol", "13666;AAAS", "16262;YAP1"]
    nr_genes = 2

    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)

    ## THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes

    ## THEN assert that some genes exists in the panel
    gene1 = genes[0]
    assert gene1.get("hgnc_id") == 13666
    assert gene1.get("hgnc_symbol") == "AAAS"

    gene2 = genes[1]
    assert gene2.get("hgnc_id") == 16262
    assert gene2.get("hgnc_symbol") == "YAP1"


def test_parse_panel_lines_excel_export_empty_line():
    ## GIVEN a iterable with panel lines
    panel_lines = ["hgnc_id;hgnc_symbol", "13666;AAAS", "16262;YAP1", ";", ""]
    nr_genes = 2

    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)

    ## THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes


def test_parse_panel_lines_modified_excel_export():
    ## GIVEN a iterable with panel lines
    panel_lines = ["HGNC_IDnumber;HGNC_symbol", "13666;AAAS"]
    nr_genes = 1

    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)

    ## THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes

    ## THEN assert that some genes exists in the panel
    for gene in genes:
        assert gene.get("hgnc_id") == 13666
        assert gene.get("hgnc_symbol") == "AAAS"
