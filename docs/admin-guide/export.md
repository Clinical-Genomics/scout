# Exporting Data from Scout

There are many scenarios where users may want to export information from Scout.
This document outlines the available export options and how to use them via the command line.

## Main `export` command:

```
scout export
```

## Available Export Commands

Scout provides the following subcommands for data export:

```
Options:
  --help  Show this message and exit.

Commands:
  cases        Export case data
  database     Export the Scout MongoDB database
  exons        Export exon regions
  genes        Export genes
  hpo_genes    Export HPO-associated genes
  managed      Export managed variants
  mt_report    Export a mitochondrial variants report
  panel        Export gene panels
  transcripts  Export transcripts
  variants     Export variants
  verified     Export verified variants
```

Each command is described in detail below.

---

## Exporting Cases (`cases`)

Export case information based on institute, status, or various filters. When exporting cases, it is possible to restrict the list of he exported data by adding optional parameters:

```
Options:
  --case-id TEXT                  Case ID to search for
  -i, --institute TEXT            Institute ID
  -r, --reruns                    Include rerun-requested cases
  -f, --finished                  Include archived or solved cases
  --causatives                    Include cases with causative variants
  --research-requested            Include cases with research requested
  --rerun-monitor                 Include cases with continuous rerun monitoring
  --is-research                   Include cases in research mode
  -s, --status [prioritized|inactive|active|solved|archived|ignored]
                                  Filter by case status
  --within-days INTEGER           Filter by event date (days ago)
  --json                          Output result in JSON format
```

The command's output is a list of case documents in the same format as they are saved into the database (dictionaries). By specifying the `--json`, documents are printed in json format.

---

## Exporting the Database (`database`)

Dump the entire Scout MongoDB database (or subsets).

```
Options:
  -o, --out PATH       Output directory for the dump [default: ./dump]
  --uri TEXT           MongoDB connection URI
  --all-collections    Include variant collections
  --help               Show this message and exit
```

---

## Exporting Exons (`exons`)

Export all exons or limit to a specific gene. Default format is a .bed file, but they can be exported as a json file by using the `--json` option.

```
Options:
  -b, --build [37|38]             Genome build version
  -hgnc, --hgnc-id INTEGER        Filter by HGNC ID
  --json                          Output in JSON format
```

**Output Format:**
A tab-delimited list with the following header:

```
#Chrom	Start	End	ExonId	Transcripts	HgncIDs	HgncSymbols
```

---

## Exporting Genes (`genes`)

Export all genes from the database. Default format is a .bed file, but they can be exported as a json file by using the `--json` option.

```
Options:
  -b, --build [37|38|GRCh38]      Genome build version [default: 37]
  --json                          Output in JSON format
```

**Output Format:**
A tab-delimited list with the following header:

```
#Chromosome	Start	End	Hgnc_id	Hgnc_symbol
```

---

## Exporting HPO-Associated Genes (`hpo_genes`)

Export HGNC IDs for all genes associated with a given HPO term.

**Example Usage:**

```
scout export hpo_genes HP:0000371
```

Result:

```
#Gene_id	Count
9986	1
9987	1
9988	1
6193	1
7067	1
```

---

## Exporting Managed Variants (`managed`)

Export managed variants in VCF format.

**Example Output (VCF):**

```
##fileformat=VCFv4.2
##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the variant">
##INFO=<ID=TYPE,Number=1,Type=String,Description="Type of variant">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	1295250	.	C	T	.	.	END=1295250;TYPE=SNV
..
```

---

## Exporting Mitochondrial Reports (`mt_report`)

Export a mitochondrial report for a given case.

```
Options:
  --case_id TEXT    Required case ID
  --outpath TEXT    Path to the output file
  --test            Run in test mode
```

---

## Exporting Gene Panels (`panel`)

Export gene panels with clinical annotation in BED format.

```
Options:
  -b, --build [37|38|GRCh38]      Genome build version [default: 37]
  --version FLOAT                 Specify panel version
  --bed                           Export in BED-like format
```

**Output Header (default format):**

```
#hgnc_id	symbol	disease_associated_transcripts	reduced_penetrance	mosaicism	database_entry_version	inheritance_models	custom_inheritance_models	comment
```

---

## Exporting Transcripts (`transcripts`)

Export a list of transcripts in BED format. Use the following command: `scout export transcripts`

```
Options:
  -b, --build [37|38|GRCh38]      Genome build version [default: 37]
```
---

## Exporting Causative Variants (`variants`)

Export causative variants for a case or an institute. Output is VCF by default, or JSON if specified.

```
Options:
  -c, --collaborator TEXT         Collaborator ID [default: cust000]
  -d, --document-id TEXT          Search for a specific variant
  --case-id TEXT                  Case ID to search for
  --json                          Output in JSON format
```

---

## Exporting Verified Variants (`verified`)

Similar to the `variants` export, but limited to verified variants. Output is VCF by default, or JSON if specified.

```
Options:
  -c, --collaborator TEXT         Collaborator ID [default: cust000]
  -d, --document-id TEXT          Search for a specific variant
  --case-id TEXT                  Case ID to search for
  --json                          Output in JSON format
```
