# External resources used by the Scout server

## External resources fetched by `scout download`

The `scout download` commands fetch the following external resources. `scout download everything` runs all of them (OMIM only if `--api-key` is given). Access is needed, from where the CLI runs, during database update and initial setup.

| Command | Resource | URL | Defined in |
|---------|----------|-----|------------|
| `omim` | mim2gene | `https://omim.org/static/omim/data/mim2gene.txt` | `scout/utils/scout_requests.py` |
| `omim` | mimTitles, morbidmap, genemap2 (API key required) | `https://data.omim.org/downloads/<api_key>/{mimTitles,morbidmap,genemap2}.txt` | `scout/utils/scout_requests.py` |
| `hpo` | genes_to_phenotype, phenotype_to_genes, phenotype.hpoa | `http://purl.obolibrary.org/obo/hp/hpoa/{genes_to_phenotype.txt,phenotype_to_genes.txt,phenotype.hpoa}` | `scout/constants/phenotype.py` |
| `hpo` | HPO terms (hp.obo) | `https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo` | `scout/constants/phenotype.py` |
| `orpha` | Orpha to HPO | `https://www.orphadata.com/data/xml/en_product4.xml` | `scout/constants/phenotype.py` |
| `orpha` | Orpha to genes | `https://www.orphadata.com/data/xml/en_product6.xml` | `scout/constants/phenotype.py` |
| `orpha` | Orpha inheritance | `https://www.orphadata.com/data/xml/en_product9_ages.xml` | `scout/constants/phenotype.py` |
| `clingen` | Gene validity | `https://search.clinicalgenome.org/kb/gene-validity/download` | `scout/constants/phenotype.py` |
| `clingen` | Gene dosage | `https://search.clinicalgenome.org/kb/gene-dosage/downloadall` | `scout/constants/phenotype.py` |
| `hgnc` | HGNC complete set | `https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt` | `scout/utils/scout_requests.py` |
| `exac` | gnomAD v4.1.1 constraint metrics (tried in order, mirrors) | `https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1.1/constraint/gnomad.v4.1.1.constraint_metrics.tsv.bgz` <br> `https://gnomad-public-us-east-1.s3.amazonaws.com/release/4.1.1/constraint/gnomad.v4.1.1.constraint_metrics.tsv.bgz` <br> `https://datasetgnomad.blob.core.windows.net/dataset/release/4.1.1/constraint/gnomad.v4.1.1.constraint_metrics.tsv.bgz` | `scout/utils/scout_requests.py` |
| `ensembl` | Genes, transcripts, exons (Ensembl BioMart via [Schug](https://schug.scilifelab.se)) | `https://schug.scilifelab.se/genes/ensembl_genes/?build=<GRCh37\|GRCh38>` <br> `https://schug.scilifelab.se/transcripts/ensembl_transcripts/?build=<GRCh37\|GRCh38>` <br> `https://schug.scilifelab.se/exons/ensembl_exons/?build=<GRCh37\|GRCh38>` | `scout/utils/ensembl_biomart_clients.py` |
| `panelapp` | PanelApp panels (API) | `https://panelapp.genomicsengland.co.uk/api/v1/panels/` | `scout/server/extensions/panelapp_extension.py` |

Schug is a SciLifeLab Clinical Genomics Solna service that provides a proxy to Ensembl BioMart. You are welcome to use it, or deploy a copy of that service on a machine of your own. The proxy is used to fetch gene, transcript and exon data for the different genome builds.

## External resources contacted by the server at runtime

These are requested by the running Scout server (not by `scout download`), so the server needs outbound access to them.

| Purpose | URL | Defined in |
|---------|-----|------------|
| Genome build liftover (Broad Institute), used for alignment viewer coordinates and MARRVEL links | `https://liftover-xwkwwwxdwq-uc.a.run.app/liftover/` | `scout/utils/broad_liftover_client.py` |
| Refseq version lookup (NCBI Entrez), used in ClinVar submissions | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&term=<refseq>&idtype=acc` | `scout/utils/scout_requests.py` |
| ClinVar submissions (default) | `https://submit.ncbi.nlm.nih.gov/api/v1/submissions/` (test: `https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions/`, override with `CLINVAR_API_URL`) | `scout/constants/clinvar.py` |
| HGVS validation (VariantValidator) | `https://rest.variantvalidator.org/VariantValidator/variantvalidator/<build>/<descriptor>/select` | `scout/utils/hgvs.py` |
| LitVar2 publication lookup | `https://www.ncbi.nlm.nih.gov/research/litvar2-api/sensor/<rsid>` <br> `https://www.ncbi.nlm.nih.gov/research/litvar2-api/variant/autocomplete/` | `scout/server/blueprints/variant/views.py` |
| Rank model files (SNV and SV), old cases - likely other solution for KS | `https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/{rank_model,svrank_model}_-v<version>-.ini` (configurable via `RANK_MODEL_LINK_PREFIX` / `SV_RANK_MODEL_LINK_PREFIX`) | `scout/server/config.py`, `scout/adapter/mongo/rank_model.py` |
| PanelApp panels (panel updates from the UI) | `https://panelapp.genomicsengland.co.uk/api/v1/panels/` | `scout/server/extensions/panelapp_extension.py` |

Optional services configured by the admin (no fixed URL): Gens (`GENS_HOST`), Chanjo (`SQLALCHEMY_DATABASE_URI`) Chanjo2 (`CHANJO2_URL`), Scout Reviewer (`SCOUT_REVIEWER_URL`), tip2toe (`PHENOPACKET_API_URL`), Matchmaker Exchange (`MME_URL`), Beacon (`BEACON_URL`), Keycloak (`KEYCLOAK`), BioNano Access (`BIONANO_ACCESS`), rerunner (`RERUNNER_API_ENTRYPOINT`),.

Remote files used by the IGV browser (reference genomes, cytobands, public tracks) are fetched by the user's browser, not the server. They are defined in `scout/constants/igv_tracks.py`.
