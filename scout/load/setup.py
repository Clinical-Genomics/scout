"""scout/load/setup.py

Sets up a scout database.
This means add a default institute, a user and the internal definitions such as gene objects,
transcripts, hpo terms etc

"""
import logging
import datetime
import yaml

from pprint import pprint as pp

from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError)

### Import demo files ###
# Resources
from scout.demo.resources import (
    hgnc_reduced_path, exac_reduced_path, transcripts37_reduced_path, transcripts38_reduced_path,
    mim2gene_reduced_path, genemap2_reduced_path, hpogenes_reduced_path, hpo_to_genes_reduced_path,
    hpoterms_reduced_path, hpo_phenotype_to_terms_reduced_path, madeline_path,
    genes37_reduced_path, genes38_reduced_path)

# Gene panel
from scout.demo import panel_path

# Case files
from scout.demo import load_path

# Import the functions to setup scout
from scout.parse.panel import parse_gene_panel

from scout.build import build_institute

from scout.load import (load_hgnc_genes, load_hpo, load_transcripts)

from scout.utils.handle import get_file_handle

from scout.utils.requests import (fetch_mim_files, fetch_hpo_genes, fetch_ensembl_genes,
                                  fetch_ensembl_transcripts, fetch_hgnc, fetch_exac_constraint)


LOG = logging.getLogger(__name__)


def setup_scout(adapter, institute_id='cust000', user_name='Clark Kent',
                user_mail='clark.kent@mail.com', api_key=None, demo=False):
    """docstring for setup_scout"""
    ########################## Delete previous information ##########################
    LOG.info("Deleting previous database")
    for collection_name in adapter.db.collection_names():
        if not collection_name.startswith('system'):
            LOG.info("Deleting collection %s", collection_name)
            adapter.db.drop_collection(collection_name)
    LOG.info("Database deleted")

    ########################## Add a institute ##########################
    #####################################################################
    # Build a institute with id institute_name
    institute_obj = build_institute(
        internal_id=institute_id,
        display_name=institute_id,
        sanger_recipients=[user_mail]
    )

    # Add the institute to database
    adapter.add_institute(institute_obj)

    ########################## Add a User ###############################
    #####################################################################
    # Build a user obj
    user_obj = dict(
                _id=user_mail,
                email=user_mail,
                name=user_name,
                roles=['admin'],
                institutes=[institute_id]
            )

    adapter.add_user(user_obj)

    ### Get the mim information ###

    if not demo:
        # Fetch the mim files
        try:
            mim_files = fetch_mim_files(api_key, mim2genes=True, morbidmap=True, genemap2=True)
        except Exception as err:
            LOG.warning(err)
            raise err
        mim2gene_lines = mim_files['mim2genes']
        genemap_lines = mim_files['genemap2']

        # Fetch the genes to hpo information
        hpo_gene_lines = fetch_hpo_genes()
        # Fetch the latest version of the hgnc information
        hgnc_lines = fetch_hgnc()
        # Fetch the latest exac pli score information
        exac_lines = fetch_exac_constraint()


    else:
        mim2gene_lines = [line for line in get_file_handle(mim2gene_reduced_path)]
        genemap_lines = [line for line in get_file_handle(genemap2_reduced_path)]

        # Fetch the genes to hpo information
        hpo_gene_lines = [line for line in get_file_handle(hpogenes_reduced_path)]
        # Fetch the reduced hgnc information
        hgnc_lines = [line for line in get_file_handle(hgnc_reduced_path)]
        # Fetch the latest exac pli score information
        exac_lines = [line for line in get_file_handle(exac_reduced_path)]


    builds = ['37', '38']
    ################## Load Genes and transcripts #######################
    #####################################################################
    for build in builds:
        # Fetch the ensembl information
        if not demo:
            ensembl_genes = fetch_ensembl_genes(build=build)
        else:
            ensembl_genes = get_file_handle(genes37_reduced_path)
        # load the genes
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
            ensembl_id = gene_obj['ensembl_id']
            ensembl_genes[ensembl_id] = gene_obj

        # Fetch the transcripts from ensembl
        if not demo:
            ensembl_transcripts = fetch_ensembl_transcripts(build=build)
        else:
            ensembl_transcripts = get_file_handle(transcripts37_reduced_path)
        # Load the transcripts for a certain build
        transcripts = load_transcripts(adapter, ensembl_transcripts, build, ensembl_genes)

    hpo_terms_handle = None
    hpo_to_genes_handle = None
    hpo_disease_handle = None
    if demo:
        hpo_terms_handle = get_file_handle(hpoterms_reduced_path)
        hpo_to_genes_handle = get_file_handle(hpo_to_genes_reduced_path)
        hpo_disease_handle = get_file_handle(hpo_phenotype_to_terms_reduced_path)

    load_hpo(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        hpo_gene_lines=hpo_to_genes_handle,
        disease_lines=genemap_lines,
        hpo_disease_lines=hpo_disease_handle
    )

    # If demo we load a gene panel and some case information
    if demo:
        parsed_panel = parse_gene_panel(
            path=panel_path,
            institute='cust000',
            panel_id='panel1',
            version=1.0,
            display_name='Test panel'
        )
        adapter.load_panel(parsed_panel)

        case_handle = get_file_handle(load_path)
        case_data = yaml.load(case_handle)

        adapter.load_case(case_data)

    LOG.info("Creating indexes")
    adapter.load_indexes()
    LOG.info("Scout instance setup successful")
