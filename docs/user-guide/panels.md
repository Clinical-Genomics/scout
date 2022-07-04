# Gene Panels

This page describes gene panels, how they are annotated and how they are used in scout.

## General

Scout is developed to be used in a clinical setting and therefore gene panels is a central concept. The gene panels describes a set of genes with additional information that is often associated with a disease or a disease group.
A case can then be associated with one or several gene panels.

Gene panels containing custom genes can be directly created by Scout users in Scout's dedicated **Gene Panels page**. The following section describes how a user can create or update a gene panel from Scout.

Gene panels can additionally be imported from [PanelApp](https://panelapp.genomicsengland.co.uk/) using the command line. Since this task must be performed by a system admin, it will be described in the [admin section](../admin-guide/panelapp_panels.md) of the guide.


### Custom panels: file format

The gene panel is a tab or semicolon (;)-separated text file with an optional header that describes the columns and one line for each gene entry. You must use the same delimiter for the whole file. Ideally do not use the delimiter characters in other places in the file. Consult with an admin if you need to use the delimiter characters in other fields for help with escaping them or ensuring a higher priority separator is used on a previous line.

The columns that will be used by scout are the following. **Please note that if you do not include a header, the order of the columns can't be changed**

- **hgnc_id(int)** This identifies the gene. *Mandatory*
- **hgnc_symbol(str)** This is used for coherence check when humans look at the file. *Optional*
- **disease_associated_transcripts(str)** ','-separated list of manually curated transcripts. *Optional*
- **genetic_disease_models(str)** ','-separated list of manually curated inheritance patterns that are followed for a gene. *Optional*
- **mosaicism(str)** If a gene is known to be associated with mosaicism this is annotated. *Optional*
- **reduced_penetrance(str)** If a gene is known to have reduced penetrance this is annotated. *Optional*
- **database_entry_version(str)** The database entry version is a way to track when a a gene was added or modified. *Optional*

Each gene in a gene panel have to be identified with a [HGNC](https://www.genenames.org/) id.

### Custom panels: optional header

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

### Custom panels: notes on entries

- **hgnc_id**: has valid HGNC id. **Please check that a gene with the give HGNC ID exists in Scout in the available genome build**. If for instance Scout is using genome build GRCh37 and a user tries to save a gene only available in genome build GRCh38 the upload of the panel will fail.
- **genetic_disease_models** A comma-separated list of inheritance models. Any standard model (AR,AD,XR,XD,MT,X,Y) will be saved under `inheritance_models`. Models different from standard models will be saved as `custom_inheritance_models`.
- **mosaicism** Any entry here will be interpreted as true
- **reduced_penetrance** Any entry here will be interpreted as true
- **database_entry_version** This should refer to a earlier version of the panel

### Custom panels: uploading a new gene panel version

You can upload a text file in Scout to update an existing gene panel. It should follow the format specified in this file: [panel-example](../static/scout-3-panel-file-example.csv). This file is `;` (semicolon) separated. Tab is also an accepted file separator.

You can also use this example [Excel template](../static/scout-3-panel-file-example.xlsx) as a starting point. When you are ready to update the gene panel simply:

1. choose **"Save as..."** in Excel and select **"tab delimited Text"** as the format
2. fill out the form in Scout and upload the file to update your gene panel

**When creating a new panel it is very important that it does not contain blank lines.**

### Custom panels: upload from interface

Choose the menu in top left corner, click `Gene Panel`. Then under 'new panel' the user can point to a file and fill in name and display name.

### Custom panels: upload with CLI (admins only)

When uploading from CLI there are more options. Use `scout load panel --help` for more information.
