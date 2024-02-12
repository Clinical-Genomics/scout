"""scout/load/setup.py

Sets up a scout database.
This means add a default institute, a user and the internal definitions such as gene objects,
transcripts, hpo terms etc

"""
import logging

import yaml

from scout.build import build_institute

# Case files
# Gene panel
from scout.demo import cancer_load_path, load_path, panel_path, rnafusion_load_path

### Import demo files ###
from scout.demo.resources import demo_files
from scout.load import load_cytobands, load_hgnc_genes, load_transcripts
from scout.load.disease import load_disease_terms
from scout.load.hpo import load_hpo_terms

# Resources
from scout.parse.case import parse_case_data
from scout.parse.panel import parse_gene_panel
from scout.resources import cytoband_files
from scout.utils.ensembl_biomart_clients import EnsemblBiomartHandler
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import (
    fetch_constraint,
    fetch_genes_to_hpo_to_disease,
    fetch_hgnc,
    fetch_mim_files,
)

LOG = logging.getLogger(__name__)


def setup_scout(
    adapter,
    institute_id="cust000",
    user_name="Clark Kent",
    user_mail="clark.kent@mail.com",
    api_key=None,
    demo=False,
    resource_files=None,
):
    """Function to setup a working scout instance.

    WARNING: If the instance is populated all collections will be deleted

    Build insert a institute and an admin user.
    There are multiple sources of information that is used by scout and that needs to exist for
    scout to work proper.

    Genes:
         Scout uses HGNC as the source for gene identifiers en ensembl as source for coordinates.
         Additional information of disease connections for genes if fetched from OMIM.
         Link between hpo terms and genes is fetched from HPO
         For more details check the documentation.

    """

    LOG.info("Check if there was a database, delete if existing")
    existing_database = False
    for collection_name in adapter.db.list_collection_names():
        if collection_name.startswith("system"):
            continue
        LOG.info("Deleting collection %s", collection_name)
        adapter.db.drop_collection(collection_name)
        existing_database = True

    if existing_database:
        LOG.info("Database deleted")

    institute_obj = build_institute(
        internal_id=institute_id,
        display_name=institute_id,
        sanger_recipients=[user_mail],
    )
    adapter.add_institute(institute_obj)

    user_obj = dict(
        _id=user_mail,
        email=user_mail,
        name=user_name,
        roles=["admin"],
        institutes=[institute_id],
    )

    adapter.add_user(user_obj)

    resource_files = resource_files or {}
    if demo:
        resource_files = demo_files

    # Load diseases
    mim2gene_lines = None
    genemap_lines = None
    mim2gene_path = resource_files.get("mim2gene_path")
    genemap_path = resource_files.get("genemap2_path")

    if genemap_path and mim2gene_path:
        mim2gene_lines = [line for line in get_file_handle(mim2gene_path)]
        genemap_lines = [line for line in get_file_handle(genemap_path)]

    if (genemap_lines is None) and api_key:
        try:
            mim_files = fetch_mim_files(api_key, mim2genes=True, genemap2=True)
        except Exception as err:
            LOG.warning(err)
            raise err
        mim2gene_lines = mim_files["mim2genes"]
        genemap_lines = mim_files["genemap2"]

    if resource_files.get("hpogenes_path"):
        hpo_gene_lines = [line for line in get_file_handle(resource_files.get("hpogenes_path"))]
    else:
        hpo_gene_lines = fetch_genes_to_hpo_to_disease()

    if resource_files.get("hgnc_path"):
        hgnc_lines = [line for line in get_file_handle(resource_files.get("hgnc_path"))]
    else:
        hgnc_lines = fetch_hgnc()

    if resource_files.get("constraint_path"):
        exac_lines = [line for line in get_file_handle(resource_files.get("constraint_path"))]
    else:
        exac_lines = fetch_constraint()

    # Load cytobands into cytoband collection
    for genome_build, cytobands_path in cytoband_files.items():
        load_cytobands(cytobands_path, genome_build, adapter)

    # Load genes
    builds = ["37", "38"]
    for build in builds:
        genes_path = "genes{}_path".format(build)
        ensembl_client = EnsemblBiomartHandler(build=build)
        if resource_files.get(genes_path):
            ensembl_genes = get_file_handle(resource_files[genes_path])
        else:
            ensembl_genes = ensembl_client.stream_resource(interval_type="genes")

        hgnc_genes = load_hgnc_genes(
            adapter=adapter,
            ensembl_lines=ensembl_genes,
            hgnc_lines=hgnc_lines,
            exac_lines=exac_lines,
            mim2gene_lines=mim2gene_lines,
            genemap_lines=genemap_lines,
            hpo_lines=hpo_gene_lines,
            build=build,
        )

        # Create a map from ensembl ids to gene objects
        ensembl_genes = {}
        for gene_obj in hgnc_genes:
            ensembl_id = gene_obj["ensembl_id"]
            ensembl_genes[ensembl_id] = gene_obj

        # Load transcripts
        tx_path = "transcripts{}_path".format(build)
        if resource_files.get(tx_path):
            ensembl_transcripts = get_file_handle(resource_files[tx_path])
        else:
            ensembl_transcripts = ensembl_client.stream_resource(interval_type="transcripts")
        # Load the transcripts for a certain build
        load_transcripts(adapter, ensembl_transcripts, build, ensembl_genes)

    hpo_terms_handle = None
    if resource_files.get("hpoterms_path"):
        hpo_terms_handle = get_file_handle(resource_files["hpoterms_path"])

    hpo_to_genes_handle = None
    if resource_files.get("hpo_to_genes_path"):
        hpo_to_genes_handle = get_file_handle(resource_files["hpo_to_genes_path"])

    hpo_annotation_handle = None
    if resource_files.get("hpo_phenotype_annotation_path"):
        hpo_annotation_handle = get_file_handle(resource_files["hpo_phenotype_annotation_path"])

    orpha_to_hpo_handle = None
    if resource_files.get("orpha_to_genes_path"):
        orpha_to_hpo_handle = get_file_handle(resource_files["orpha_to_hpo_path"])

    orpha_to_genes_handle = None
    if resource_files.get("orpha_to_genes_path"):
        orpha_to_genes_handle = get_file_handle(resource_files["orpha_to_genes_path"])

    orpha_inheritance_handle = None
    if resource_files.get("orpha_inheritance_path"):
        orpha_inheritance_handle = get_file_handle(resource_files["orpha_inheritance_path"])

    alias_genes = adapter.genes_by_alias()
    # Load HPO terms
    load_hpo_terms(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        hpo_gene_lines=hpo_to_genes_handle,
        alias_genes=alias_genes,
    )
    # Load diseases
    load_disease_terms(
        adapter=adapter,
        genemap_lines=genemap_lines,
        genes=alias_genes,
        hpo_annotation_lines=hpo_annotation_handle,
        orpha_to_hpo_lines=orpha_to_hpo_handle,
        orpha_to_genes_lines=orpha_to_genes_handle,
        orpha_inheritance_lines=orpha_inheritance_handle,
    )

    # If demo we load a gene panel and some case information
    if demo:
        load_demo_panel(adapter)
        load_demo_cases(adapter)

    LOG.info("Creating indexes")
    adapter.load_indexes()
    LOG.info("Scout instance setup successful")


def load_demo_panel(adapter):
    """Load demo gene panel
    Args:
        adapter(scout.adapter.MongoAdapter)
    """
    parsed_panel = parse_gene_panel(
        path=panel_path,
        institute="cust000",
        panel_id="panel1",
        version=1.0,
        display_name="Test panel",
    )
    adapter.load_panel(parsed_panel)


def load_demo_cases(adapter):
    """Load one RD case and one cancer case for ad demo data for demo cust000
    Args:
        adapter(scout.adapter.MongoAdapter)
    """
    for path in [load_path, cancer_load_path, rnafusion_load_path]:
        case_handle = get_file_handle(path)
        case_data = yaml.load(case_handle, Loader=yaml.SafeLoader)
        config_data = parse_case_data(config=case_data)
        adapter.load_case(config_data)
