# Importing gene panels from PanelApp

Gene panels can be imported from [PanelApp](https://panelapp.genomicsengland.co.uk/) using the command line.

The command to **import/update all gene panels from PanelApp** is the following:

`scout load panel --panel-app  --institute <inst-id> (--panel-app-confidence green|amber|red)`

Please note that **if you don't specify any confidence level with the --panel-app-confidence option, then only the `HighEvidence` (green) genes will be included in the panels**.

To **create/update only one** PanelApp panel, use the following command:

`scout load panel --panel-app  --institute <inst-id> --panel-id <panel-id> (--panel-app-confidence green|amber|red)`.

For instance to create the `CAKUT` (id: 234) gene panel, containing amber genes, for an institute named cust000, the command would be:

`scout load panel --panel-app  --institute cust000 --panel-id 234 --panel-app-confidence amber`

When loading a panel from PanelApp, Scout is parsing the latest version of it that is present in the API. The document is a json file like this one:

https://panelapp.genomicsengland.co.uk/api/v1/panels/234/?format=api

Please note that since the gene panel functionality in Scout is only supporting loading of genes, all eventual **`regions` or `strs` present in the PanelApp json document will not be saved in the created panel**.

PanelApp panels in Scout can be **updated any time by running the same command used for creating them**.  When panels are already present in Scout, running the command will update panels that are not up-to-date with PanelApp and just overwrite those that already present with the newest version.
