# Gene Panels

This page describes gene panels, how they are annotated and how they are used in scout.

## General

Scout is developed to be used in a clinical setting and therefore gene panels is a central concept. The gene panels describes a set of genes with additional information that is often associated with a disease or a disease group.
A case can then be associated with one or several gene panels.

### File format

The gene panel is a tab separated text file with a header that describes the columns and one line for each gene entry.

The columns that will be used by scout is the following:

- **hgnc_id(int)** This identifies the gene. *Mandatory*
- **hgnc_symbol(str)** This is used for sanity check when humans look at the file. *Optional*
- **disease_associated_transcripts(str)** ','-separated list of manually curated transcripts. *Optional*
- **genetic_disease_models(str)** ','-separated list of manually curated inheritance patterns that are followed for a gene. *Optional*
- **mosaicism(str)** If a gene is known to be associated with mosaicism this is annotated. *Optional*
- **reduced_penetrance(str)** If a gene is known to have reduced penetrance this is annotated. *Optional*
- **database_entry_version(str)** The database entry version is a way to track when a a gene was added or modified. *Optional*

Each gene in a gene panel have to be identified with a hgnc id

### File format 2

There is also an option to include all information about a panel in the header of the file. This could make uploading easier, just a matter of taste. In this case include a header with metadata, each of these lines are key-value separated by `=`. The meta data lines should start with `##`

Example:

```csv
##panel_id=panel1
##institute=cust000
##version=1.0
##date=2016-12-09
##display_name=Test panel
#hgnc_id	hgnc_symbol
7481	MT-TF
...
...
...
```

### Notes on entries

- **hgnc_id**: This one have to be a valid hgnc id that exists in scout
- **genetic_disease_models** can be anyone in [AR,AD,XR,XD,MT,X,Y]
- **mosaicism** Any entry here will be interpreted as true
- **reduced_penetrance** Any entry here will be interpreted as true
- **database_entry_version** This should refer to a earlier version of the panel

## Uploading a new gene panel version

You can upload a text file in Scout to update an existing gene panel. It should follow the format specified in this file: [panel-example](../static/scout-3-panel-file-example.csv). The file is `;` (semi-colon) separated, could also be tab separated.

You can also use this example [Excel template](../static/scout-3-panel-file-example.xlsx) as a starting point. When you are ready to update the gene panel simply:

1. choose **"Save as..."** in Excel and select **"Comma Separated Values (.csv)"** as the format
2. fill out the form in Scout and upload the "*.csv" file to update your gene panel

### Upload from interface

Choose the menu in top left corner, click `Gene Panel`. Then under 'new panel' the user can point to a csv file and fill in name and display name.

### Upload with CLI

When uploading from CLI there are more options. Use `scout load panel --help` for more information.