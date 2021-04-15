from pprint import pprint as pp

import click


@click.command()
@click.argument("gene-list", type=click.File("r"))
@click.option("--panel-name", "-n", required=True)
@click.pass_context
def cli(ctx, gene_list, panel_name):
    # Dictionary with panel_id as key
    panel_metadata = {}
    header = []
    panel_genes = {}
    for line in gene_list:
        line = line.rstrip()
        if line.startswith("#"):
            if line.startswith("##"):
                # These headers include metainformation about the panels or
                # contig information which we are not interested in.
                # They allways start with Database=<ID=<some_name> and are
                # ',' separated.
                if not "contig" in line:
                    panel_info = {}
                    line = line.split(",")
                    panel_info["institute"] = line[0][15:22]
                    for entry in line[1:]:
                        splitted_entry = entry.split("=")
                        key = splitted_entry[0]
                        value = splitted_entry[1]
                        if key == "Version":
                            panel_info["version"] = float(value)
                        elif key == "Date":
                            year = value[0:4]
                            month = value[4:6]
                            day = value[6:]
                            panel_info["date"] = "{0}-{1}-{2}".format(year, month, day)
                        elif key == "Acronym":
                            panel_id = value
                            panel_info["panel_id"] = panel_id
                        elif key == "Complete_name":
                            panel_info["display_name"] = value

                    panel_metadata[panel_id] = panel_info
            else:
                # The header line starts with only one '#'
                header = line[1:].split("\t")
                # Check if the given panel name was found
                if not panel_name in panel_metadata:
                    click.echo("Panel {0} could not be found in gene list".format(panel_name))
                    ctx.abort()
        # These lines hold information about genes
        else:
            # Dictionary with information in gene list
            gene_info = dict(zip(header, line.split("\t")))
            # Dictionary with information in correct format:
            panel_gene_info = {}
            # Check if the gene belongs to the panel of interest
            panels = gene_info.get("Clinical_db_gene_annotation", "").split(",")
            if panel_name in panels:
                # Get the hgnc symbol
                hgnc_symbol = gene_info["HGNC_symbol"]
                panel_gene_info["hgnc_symbol"] = hgnc_symbol

                # Parse the manually annotated disease associated transcripts
                transcripts_info = gene_info.get("Disease_associated_transcript")
                transcripts = set()
                if transcripts_info:
                    for entry in transcripts_info.split(","):
                        transcripts.add(entry.split(":")[1])
                panel_gene_info["transcripts"] = ",".join(transcripts)

                # Check manually annotated reduced penetrance
                penetrance = gene_info.get("Reduced_penetrance")
                panel_gene_info["penetrance"] = ""
                if penetrance:
                    panel_gene_info["penetrance"] = "Yes"

                # Check manually annotated mosaicism
                mosaicism = gene_info.get("Mosaicism")
                panel_gene_info["mosaicism"] = ""
                if mosaicism:
                    panel_gene_info["mosaicism"] = "Yes"

                # Check manually annotated disease models
                panel_gene_info["inheritance"] = gene_info.get("Genetic_disease_model", "")

                # Parse database entry version
                panel_gene_info["entry_version"] = gene_info.get("Database_entry_version", "")

                if hgnc_symbol in panel_genes:
                    # If we have multiple entries we update the information
                    pass
                else:
                    panel_genes[hgnc_symbol] = panel_gene_info

    # Print the headers
    click.echo("##panel_id={}".format(panel_metadata[panel_name]["panel_id"]))
    click.echo("##institute={}".format(panel_metadata[panel_name]["institute"]))
    click.echo("##version={}".format(panel_metadata[panel_name]["version"]))
    click.echo("##date={}".format(panel_metadata[panel_name]["date"]))
    click.echo("##institute={}".format(panel_metadata[panel_name]["institute"]))
    click.echo("##display_name={}".format(panel_metadata[panel_name]["display_name"]))

    new_headers = [
        "hgnc_symbol",
        "disease_associated_transcripts",
        "reduced_penetrance",
        "genetic_disease_models",
        "mosaicism",
        "database_entry_version",
    ]
    click.echo("#" + "\t".join(new_headers))

    for hgnc_symbol in panel_genes:
        panel_gene_info = panel_genes[hgnc_symbol]
        click.echo(
            "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(
                panel_gene_info["hgnc_symbol"],
                panel_gene_info["transcripts"],
                panel_gene_info["penetrance"],
                panel_gene_info["inheritance"],
                panel_gene_info["mosaicism"],
                panel_gene_info["entry_version"],
            )
        )


if __name__ == "__main__":
    cli()
