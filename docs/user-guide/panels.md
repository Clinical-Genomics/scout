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
- **proxy_region(str)** A valid ISCA region, `ISCA-1234`, for which the gene is a proxy. This is used to flag variants in the region, when there is not sufficient evidence to link the specific gene to disease but the region is established haploinsufficient or triplosensitive. *Optional*

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
- **proxy_region** A valid ISCA region, `ISCA-1234`, for which the gene is a proxy. This is used to flag variants in the region, when there is not sufficient evidence to link the specific gene to disease but the region is established as haploinsufficient or triplosensitive. *Optional*
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

When uploading from CLI there are more options. Use `scout load panel --help` for more information, and see [Maintaining gene panels](../admin-guide/panels.md) in the admin guide.

## Panel maintainers and edit permissions

Each gene panel has a list of **maintainers**: the users allowed to change it. The panel page lists them under "Maintainers", and on the Gene Panels page a tool badge next to a panel name shows that you are one of its maintainers.

A user can change a panel if any of the following is true:

- the user is a Scout admin
- the user is one of the panel's maintainers
- the panel has no maintainer field at all (panels created by very old Scout versions)

A panel whose maintainer list exists but is empty can only be changed by admins. Panels loaded from the command line, including PanelApp panels, start out this way.

When you create a new panel from the Gene Panels page, you become its only maintainer. Maintainers can not be added or removed in the web interface; ask a Scout admin to do it from the command line (see [Panel maintainers](../admin-guide/panels.md#panel-maintainers) in the admin guide).

Maintainers are stored on each panel version. A new version made in Scout copies the maintainers of the version it was made from.

Users who are not allowed to change a panel get the message "Permission denied: please ask a panel maintainer or admin for help."

## Editing panels in the web interface

### Gene Panels page

The Gene Panels page lists the latest version of each panel for your institutes. For each panel you can:

- **History**: list the earlier versions of the panel, with links to each of them
- **Modify**: upload a gene file to either *add genes* to the panel (genes already in the panel get their information updated) or *replace genes*, removing all current genes and adding the ones in the file
- **Remove**: hide the panel. Removed panels are kept in the database. Untick "Hide removed panels" to show them, with a "Removed" badge, and use the restore button to bring one back

Modify, remove and restore need edit permission on the panel.

### Panel page

On the page of a single panel you can:

- edit the full (display) name and description of the panel
- add a gene, by searching for it and filling in its panel information (transcripts, inheritance models, mosaicism, reduced penetrance, proxy region, entry version and comment)
- edit the information for a gene already in the panel
- delete a gene from the panel

Gene additions, edits and deletions, including those from **Modify** on the Gene Panels page, are not applied at once. They are collected as **pending changes**, listed in the "Pending changes" box. Pending changes are stored on the panel, so other users see them too. From the pending changes box you can:

- **Update panel**: save the pending changes as a new panel version. The suggested version number is the current version plus one; the new version must not be lower than the current one and must not already exist. Saving the changes under the current version number updates that version in place instead of creating a new one.
- **Cancel pending actions**: discard all pending changes

Saving pending changes, and editing the name or description, need edit permission on the panel.

When a new version is saved, the previous version is archived. Archived versions can still be viewed and used, but their genes can not be edited.
