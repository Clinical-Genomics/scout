"""
CLI functions to setup scout

There are two options.
`scout setup demo` will setup a database that are loaded with more example
data but the gene definitions etc are reduced.

`scout setup database` will create a full scale instance of scout. There will not be any cases
and one admin user is added.

"""

import logging
import pathlib

import click
from flask.cli import current_app, with_appcontext
from pymongo.errors import ServerSelectionTimeoutError

# Adapter stuff
from scout.adapter import MongoAdapter
from scout.load.setup import setup_scout

LOG = logging.getLogger(__name__)


def abort_if_false(ctx, param, value):
    """Small function to quit if flag is not used"""
    if not value:
        ctx.abort()


@click.command("database", short_help="Setup a basic scout instance")
@click.option("-i", "--institute-name", type=str)
@click.option("-u", "--user-name", type=str)
@click.option("-m", "--user-mail", type=str)
@click.option("--api-key", help="Specify the api key")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="This will delete existing database, do you wish to continue?",
)
@click.option(
    "--files",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to directory with resource files",
)
@click.option("--hgnc", type=click.Path(exists=True))
@click.option(
    "--exac",
    type=click.Path(exists=True),
    help="Path to file with EXaC / GnomAD pLi constraint scores",
)
@click.option(
    "--ensgenes37",
    type=click.Path(exists=True),
    help="Path to file with ENSEMBL genes, build 37",
)
@click.option(
    "--ensgenes38",
    type=click.Path(exists=True),
    help="Path to file with ENSEMBL genes, build 38",
)
@click.option(
    "--enstx37",
    type=click.Path(exists=True),
    help="Path to file with ENSEMBL transcripts, build 37",
)
@click.option(
    "--enstx38",
    type=click.Path(exists=True),
    help="Path to file with ENSEMBL transcripts, build 38",
)
@click.option("--mim2gene", type=click.Path(exists=True))
@click.option("--genemap", type=click.Path(exists=True))
@click.option(
    "--hpogenes",
    type=click.Path(exists=True),
    help=(
        "Path to file with HPO to gene information. This is the file called"
        "genes_to_phenotype.txt"
    ),
)
@click.option(
    "--hpoterms",
    type=click.Path(exists=True),
    help="Path to file with HPO terms. This is the file called hpo.obo",
)
@click.option(
    "--hpo_to_genes",
    type=click.Path(exists=True),
    help=(
        "Path to file with map from HPO terms to genes. This is the file called "
        "phenotype_to_genes.txt"
    ),
)
@click.option(
    "--hpo-phenotype-annotation",
    type=click.Path(exists=True),
    help=(
        "Path to file with map from HPO disease (OMIM and ORPHA) to phenotype term with annotation. This is the file  called phenotype.hpoa"
    ),
)
@click.option(
    "--orpha-to-hpo",
    type=click.Path(exists=True),
    help=(
        "Path to file mapping ORPHA codes to HPO terms. This is the file called "
        "orphadata_en_product4.xml"
    ),
)
@click.option(
    "--orpha-to-genes",
    type=click.Path(exists=True),
    help=(
        "Path to file mapping ORPHA codes to genes. This is the file called "
        "orphadata_en_product6.xml"
    ),
)
@with_appcontext
@click.pass_context
def database(
    context,
    institute_name,
    user_name,
    user_mail,
    api_key,
    mim2gene,
    genemap,
    hgnc,
    exac,
    ensgenes37,
    ensgenes38,
    enstx37,
    enstx38,
    hpogenes,
    hpoterms,
    hpo_to_genes,
    hpo_phenotype_annotation,
    orpha_to_hpo,
    orpha_to_genes,
    files,
):
    """Setup a scout database."""

    LOG.info("Running scout setup database")
    # Fetch the omim information
    api_key = api_key or current_app.config.get("OMIM_API_KEY")
    if not api_key:
        LOG.warning("No omim api key provided. This means information will be lost in scout")
        LOG.info("Please request an OMIM api key and run scout update genes")

    institute_name = institute_name or context.obj["institute_name"]
    user_name = user_name or context.obj["user_name"]
    user_mail = user_mail or context.obj["user_mail"]

    adapter = context.obj["adapter"]

    # Populate resource_files with the paths specified for each resource
    resource_files = {
        "mim2gene_path": mim2gene,
        "genemap_path": genemap,
        "hgnc_path": hgnc,
        "constaints_path": exac,
        "genes37_path": ensgenes37,
        "genes38_path": ensgenes38,
        "transcripts37_path": enstx37,
        "transcripts38_path": enstx38,
        "hpogenes_path": hpogenes,
        "hpoterms_path": hpoterms,
        "hpo_to_genes_path": hpo_to_genes,
        "hpo_phenotype_annotation_path": hpo_phenotype_annotation,
        "orpha_to_hpo_path": orpha_to_hpo,
        "orpha_to_genes_path": orpha_to_genes,
    }
    LOG.info("Setting up database %s", context.obj["mongodb"])

    # If a folder was supplied, populate resource_files with paths to the contents
    if files:
        for path in pathlib.Path(files).glob("**/*"):
            if path.stem == "mim2genes":
                resource_files["mim2gene_path"] = str(path.resolve())
            if path.stem == "genemap2":
                resource_files["genemap_path"] = str(path.resolve())
            if path.stem == "hgnc":
                resource_files["hgnc_path"] = str(path.resolve())
            if path.stem == "gnomad.v4.0.constraint_metrics":
                resource_files["constraint_path"] = str(path.resolve())
            if path.stem == "ensembl_genes_37":
                resource_files["genes37_path"] = str(path.resolve())
            if path.stem == "ensembl_genes_38":
                resource_files["genes38_path"] = str(path.resolve())
            if path.stem == "ensembl_transcripts_37":
                resource_files["transcripts37_path"] = str(path.resolve())
            if path.stem == "ensembl_transcripts_38":
                resource_files["transcripts38_path"] = str(path.resolve())
            if path.stem == "genes_to_phenotype":
                resource_files["hpogenes_path"] = str(path.resolve())
            if path.stem == "hpo":
                resource_files["hpoterms_path"] = str(path.resolve())
            if path.stem == "phenotype_to_genes":
                resource_files["hpo_to_genes_path"] = str(path.resolve())
            if path.stem == "phenotype":
                resource_files["hpo_phenotype_annotation_path"] = str(path.resolve())
            if path.stem == "orphadata_en_product4":
                resource_files["orpha_to_hpo_path"] = str(path.resolve())
            if path.stem == "orphadata_en_product6":
                resource_files["orpha_to_genes_path"] = str(path.resolve())

    setup_scout(
        adapter=adapter,
        institute_id=institute_name,
        user_name=user_name,
        user_mail=user_mail,
        api_key=api_key,
        resource_files=resource_files,
    )


@click.command("demo", short_help="Setup a scout demo instance")
@click.pass_context
def demo(context):
    """Setup a scout demo instance. This instance will be populated with a
    case, a gene panel and some variants.
    """
    LOG.info("Running scout setup demo")
    institute_name = context.obj["institute_name"]
    user_name = context.obj["user_name"]
    user_mail = context.obj["user_mail"]

    adapter = context.obj["adapter"]
    setup_scout(
        adapter=adapter,
        institute_id=institute_name,
        user_name=user_name,
        user_mail=user_mail,
        demo=True,
    )


@click.group()
@click.option(
    "-i",
    "--institute",
    default="cust000",
    show_default=True,
    help="Name of initial institute",
)
@click.option(
    "-e",
    "--user-mail",
    default="clark.kent@mail.com",
    show_default=True,
    help="Mail of initial user",
)
@click.option(
    "-n",
    "--user-name",
    default="Clark Kent",
    show_default=True,
    help="Name of initial user",
)
@with_appcontext
@click.pass_context
def setup(context, institute, user_mail, user_name):
    """
    Setup scout instances: a demo database or a production database, according to the
    according to the subcommand specified by user.
    """
    setup_config = {
        "institute_name": institute,
        "user_name": user_name,
        "user_mail": user_mail,
    }

    mongodb_name = current_app.config["MONGO_DBNAME"]
    client = current_app.config["MONGO_CLIENT"]

    if context.invoked_subcommand == "demo":
        # Modify the name of the database that will be created
        LOG.debug("Change database name to scout-demo")
        mongodb_name = "scout-demo"

    mongo_database = client[mongodb_name]
    LOG.info("Test if mongod is running")
    try:
        mongo_database.test.find_one()
    except ServerSelectionTimeoutError as err:
        LOG.warning("Connection could not be established")
        LOG.warning("Please check if mongod is running")
        LOG.warning(err)
        raise click.Abort()

    setup_config["mongodb"] = mongodb_name
    setup_config["adapter"] = MongoAdapter(mongo_database)
    context.obj = setup_config


setup.add_command(database)
setup.add_command(demo)
