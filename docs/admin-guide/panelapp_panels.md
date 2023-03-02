# Importing gene panels from PanelApp

Gene panels can be imported from [PanelApp](https://panelapp.genomicsengland.co.uk/) using the command line.

The command to **import/update all gene panels from PanelApp** is the following:

`scout load panel --panel-app  --institute <inst-id> [--panel-app-confidence <green|amber|red>]`

The `--panel-app-confidence` option specifies the threshold of confidence for genes that should be added to the panel.

According to PanelApp, the levels of confidence for a gene are the following:
- Green = highest level of confidence; a gene from 3 or 4 sources.
- Amber = intermediate; a gene from 2 sources.
- Red = lowest level of confidence; 1 of the 4 sources or from other sources.

Please note that when you create a PanalApp panel in **Scout, the software uses the specified level as a threshold, and not as a filter**, so you'll get the following:

```
`--panel-app-confidence green` collects only green genes from PanelApp
`--panel-app-confidence amber` collects amber and green genes from PanelApp
`--panel-app-confidence red` collects all genes from PanelApp
```

Please note that **if you don't specify any confidence level with the `--panel-app-confidence option`, then only the `HighEvidence` (green) genes will be included in the panels**.

To **create/update only one** PanelApp panel, use the following command:

`scout load panel --panel-app  --institute <inst-id> --panel-id <panel-id> (--panel-app-confidence green|amber|red)`.

For instance to create the `CAKUT` (id: 234) gene panel, containing amber + green genes, for an institute named cust000, the command would be:

`scout load panel --panel-app  --institute cust000 --panel-id 234 --panel-app-confidence amber`

When loading a panel from PanelApp, Scout is parsing the latest version of it that is present in the API. The document is a json file like this one:

https://panelapp.genomicsengland.co.uk/api/v1/panels/234/?format=api

Please note that since the gene panel functionality in Scout is only supporting loading of genes, all eventual **`regions` or `strs` present in the PanelApp json document will not be saved in the created panel**.

PanelApp panels in Scout can be **updated any time by running the same command used for creating them**.  When panels are already present in Scout, running the command will update panels that are not up-to-date with PanelApp and just overwrite those that already present with the newest version.


# PanelApp green genes panel

As an admin, it is possible to create/update a gene panel **containing green genes from all available PanelApp panels**. You can create this panel for an institute by using the following syntax:

`scout update panelapp-green -i <custID> --force`

The feature will connect to PanelApp and retrieve all green genes available in any panel in that moment.
Note that the `--force` is required to force create a new version of the gene panel in the eventuality that the number of green genes found on the PanelApp server is lower than the number of genes contained in the old panel.
