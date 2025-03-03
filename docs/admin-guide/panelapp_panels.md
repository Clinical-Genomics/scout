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

Also note that **if you don't specify any confidence level with the `--panel-app-confidence option`, then only the `HighEvidence` (green) genes will be included in the panels**.

To **create/update only one** PanelApp panel, use the following command:

`scout load panel --panel-app  --institute <inst-id> --panel-id <panel-id> (--panel-app-confidence green|amber|red)`.

For instance to create the `CAKUT` (id: 234) gene panel, containing amber + green genes, for an institute named cust000, the command would be:

`scout load panel --panel-app  --institute cust000 --panel-id 234 --panel-app-confidence amber`

When loading a panel from PanelApp, Scout is parsing the latest version of it that is present in the API. The document is a json file like this one:

https://panelapp.genomicsengland.co.uk/api/v1/panels/234/?format=api

Since the Panelapp gene panels import functionality in Scout is only supporting loading of genes, all eventual **`regions` or `strs` present in the PanelApp json document will not be saved in the created panel**.

PanelApp panels in Scout can be **updated any time by running the same command used for creating them**.  When panels are already present in Scout, running the command will update panels that are not up-to-date with PanelApp and just overwrite those that already present with the newest version.


# PanelApp green genes panel

As an admin, it is possible to create/update a gene panel **containing green genes from PanelApp panels**. The basic command to achieve this is the following:

`scout update panelapp-green -i <institute> (--signed-off) --force`


### Command Line Step: Selecting Panel Types

During this step, the command line will prompt you to select one or more panel types to filter the panels retrieved from the API.

#### Available Panel Types
At the time of writing, the following panel types are available:

1. **Actionable**
2. **Additional Findings**
3. **Cancer Germline 100k**
4. **ClinGen Curated Genes**
5. **Component of Super Panel**
6. **GMS Cancer Germline Virtual**
7. **GMS Rare Disease**
8. **GMS Rare Disease Virtual**
9. **GMS Signed-Off**
10. **Rare Disease 100k**
11. **Reference**
12. **Research**
13. **Submitted List**
14. **Superpanel**
15. **all** - all types above

#### Default Behavior
If no panel type is selected (i.e., the user presses Enter without input), Green Genes will be selected from the following default panel types: `3`, `4`, `6`, `7`, `8`, `9`, `10`.

### Include all available panels
By typing `all` at the prompt, green genes will be collected from any panel available in PanelApp

#### Important Note
The `--force` or (`-f`) parameter is required to create a new version of the gene panel if the number of green genes retrieved from the PanelApp server is lower than the number of genes in the older version of the panel. This ensures the panel is updated despite the reduction in gene count.

If specified, the `--signed-off` (or simply `-s`) parameter will restrict the download of green genes to include only signed-off panels.

