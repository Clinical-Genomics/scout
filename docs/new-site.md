# Setting up Scout at a new site

This page is a map for bioinformaticians and system administrators setting up Scout at a new site, from a first demo to a production instance.
Most topics are covered in more detail elsewhere in these docs, and this page links to them, roughly in the order you are likely to need them.

If you get stuck, or want to tell us about your pipeline, open a [GitHub issue][issues] or start a [GitHub discussion][discussions]. We are always happy to hear from new sites!

## 1. Try it out first

Before installing anything permanently, have a look at a running instance:

- **Containerised demo**: from a clone of the repository, run `docker-compose up -d` (or `make up`) and open <http://localhost:8000>. See the [main README][readme] and [Deploying Scout in containers](admin-guide/containers/container-deploy.md).
- **Local demo**: with a MongoDB running, `scout setup demo` followed by `scout --demo serve`. The demo user is `clark.kent@mail.com`. See [Install](install.md#demo-setup).

The demo case (`scout/demo/643594.config.yaml`) and the files next to it in [`scout/demo`][demo] are also good working examples of what Scout expects as input.

## 2. Choose a version to deploy

- Deploy a **tagged release**, not whatever is on `main`. `main` is the development branch: it is tested, but not always ready to deploy. Releases are made from release branches and tagged (e.g. `v4.116`), see [CONTRIBUTING][contributing].
- Releases are published on [GitHub][releases], on [PyPI][pypi] (`pip install scout-browser`), and as Docker images (`clinicalgenomics/scout` for the CLI and `clinicalgenomics/scout-server` for the web server).
- Read the release blog posts (under Blog in the menu) and the [CHANGELOG][changelog] before upgrading, and look at [Breaking](admin-guide/breaking.md) for releases that need manual migration steps.

## 3. Install and set up the database

1. Install and start [MongoDB][mongodb]. For production we recommend running MongoDB outside containers, for performance.
2. Install Scout, with `uv`, `pip` or containers: see [Install](install.md) and [Deploying Scout in containers](admin-guide/containers/container-deploy.md) ([Kubernetes](admin-guide/containers/kubernetes.md), [systemd with podman](admin-guide/containers/systemd.md)).
3. Initialise the database and fill it with genes, transcripts, diseases and phenotypes:
    ```bash
    scout setup database
    scout download everything --api-key YOUR_OMIM_API_KEY
    ```
    See [Install - full setup](install.md#full-setup), [Gene definitions](admin-guide/genes.md), [HPO terms](admin-guide/hpo.md) and [Indexes](admin-guide/indexes.md).
4. The server and the CLI need outbound network access to a number of external resources, both during setup and at runtime. If your site has a strict firewall, [External resources used by the server](admin-guide/download-resources.md) lists the URLs to allow.

## 4. API keys and accounts to apply for

Several features depend on keys or accounts from third parties. Apply for them early, since some take a while to arrive.

| Key / account | Used for | Config / where documented |
|---------------|----------|---------------------------|
| [OMIM API][omim-api] | Downloading OMIM disease definitions and gene-disease links (`genemap2`, `morbidmap`, `mimTitles`). | Pass `--api-key` to `scout download`, `scout setup database` and `scout update omim/genes/diseases`, or set `OMIM_API_KEY` in the Python config file (`scout --flask-config config.py ...`). See [External resources](admin-guide/download-resources.md). |
| Login provider | User authentication: Google OAuth, Keycloak (OIDC) or LDAP. | `GOOGLE`, `KEYCLOAK` or `LDAP_*`. See [Login system](admin-guide/login-system.md). |
| Phenomizer | Phenotype-based gene predictions on the case page (optional). | `PHENOMIZER_USERNAME`, `PHENOMIZER_PASSWORD`. See [Server](admin-guide/server.md#config). |
| Mail server | Sending Sanger verification orders and other emails (optional). | `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`. See [Server](admin-guide/server.md#config). |
| ClinVar submission API | Submitting variants to ClinVar directly from Scout (optional). The key is entered per submission. | `CLINVAR_API_URL`. See [Server](admin-guide/server.md#config). |
| Matchmaker Exchange | Sharing cases with Matchmaker Exchange, through a [PatientMatcher][patientmatcher] node (optional). | `MME_URL`, `MME_TOKEN`. See [Matchmaker Exchange integration](admin-guide/matchmaker_exchange_integration.md). |

## 5. Configure and run the server

- The server reads a Python config file. Start from the [minimal config](admin-guide/server.md#minimal-config) and add settings as you need them. The full list of settings is in [`scout/server/config.py`][config], and [Server](admin-guide/server.md) has an annotated example.
- Use a real `SECRET_KEY`, set up a [login system](admin-guide/login-system.md), and run the server with Gunicorn behind a reverse proxy such as NGINX that handles HTTPS. See [Server - production](admin-guide/server.md#production).
- Consider [logging users' activity](admin-guide/user_activity_monitoring.md) and plan [backups](admin-guide/backup.md) from the start.

## 6. Institutes, users and gene panels

- Create an institute for each group of users that should share cases by default: `scout load institute -i cust000 -d "My clinic"`. See [Creating a new institute](admin-guide/loading-institutes.md) and [Institutes](user-guide/institutes.md).
- Add users with `scout load user`, and give at least one person the `admin` role. Admins can then manage users from the web interface. See [Creating a new user](admin-guide/loading-users.md) and [Users](user-guide/users.md).
- Load gene panels with `scout load panel`, or let Scout build broad panels from OMIM and PanelApp. See [Install - full setup](install.md#full-setup), [Gene panels](user-guide/panels.md) and [PanelApp gene panels](admin-guide/panelapp_panels.md).
- Institute-level settings, such as which local frequency database to use or which cohorts and phenotype groups to show, can be edited by admins in the web interface. See [Institute settings](user-guide/institute_settings.md) and [Institutes (admin)](admin-guide/institute.md).

## 7. Getting your data into Scout

Scout loads one case at a time from a YAML load config that points to the VCFs and other files produced by your analysis pipeline.

- **Pick a well-supported pipeline if you can.** The [FAQ](faq.md#what-should-my-vcf-format-look-like-in-detail) lists the pipelines that work best with Scout, among them [nf-core/raredisease][raredisease], [Nallo][nallo] (long reads), [Balsamic][balsamic] (somatic) and [Tomte][tomte] (RNA). If you have your own pipeline, the main requirements are VEP annotation and, for ranking, [GENMOD][genmod] rank scores. Compatibility layers such as [scout-annotation][scout-annotation] can help.
- **Write a load config.** See [Load config](admin-guide/load-config.md) for all keys, and [Loading/updating a case](admin-guide/loading-case.md) for how to load it. Use [`scout/demo/643594.config.yaml`][demo-config] as a template. We strongly recommend automation for this step, adapted to your production. Either in the pipeline, in your LIMS, or other automation package - see e.g. [cg][cg] for inspiration.
- **Alignment files (BAM/CRAM).** Give the path for each sample under `alignment_path` in the load config. (`bam_file` and `bam_path` still work but will be removed.) The web server streams these files to the IGV viewer in the user's browser, so:
    - the paths must be readable by the **web server process**, not only by the machine that ran `scout load case`;
    - an index has to be next to each file (`file.bam.bai` or `file.bai`, `file.cram.crai` or `file.crai`);
    - CRAMs need a reference that matches the one they were aligned to. See [IGV browser settings](admin-guide/igv-settings.md) for configuring local references and extra tracks.

    The same applies to the other track files in the load config, such as STR, RNA, coverage and UPD files.
- To update cases after loading, see [Updating a case](admin-guide/updating-case.md), [Updating case individuals tracks](admin-guide/updating-individuals.md), [Loading variants](admin-guide/loading-variants.md) and [Removing variants](admin-guide/deleting-variants.md).

## 8. Integrations and related tools

Scout works on its own, but several features become available when it is connected to other services. Most are developed by the same community.

| Tool | What it adds | Scout docs |
|------|--------------|-----------|
| [loqusdb][loqusdb] | Local observation counts for variants. Very valuable for triage, especially of SVs. | [Loqusdb integration](admin-guide/loqusdb_integration.md) |
| [Chanjo2][chanjo2] | Coverage and coverage-completeness reports, using d4 files. Preferred over the original Chanjo. | [Chanjo and Chanjo2 integration](admin-guide/chanjo_coverage_integration.md) |
| [Gens][gens] | Interactive copy-number and B-allele frequency plots for CNV triage. | [Gens integration](admin-guide/gens_integration.md) |
| [Scout-REViewer-service][reviewer-service] | Read-level pileups of short tandem repeat (STR) loci, using [REViewer][reviewer]. | [Scout REViewer Service integration](admin-guide/reviewer_service.md) |
| [PatientMatcher][patientmatcher] | Matchmaker Exchange node for sharing cases. | [Matchmaker Exchange integration](admin-guide/matchmaker_exchange_integration.md) |
| [cgbeacon2][cgbeacon2] | GA4GH Beacon for sharing variants. | `BEACON_URL`, `BEACON_TOKEN` in [Server](admin-guide/server.md#config) |
| BioNano Access | Displays FSHD results from optical genome mapping. | [BioNano Genomics Access FSHD integration](admin-guide/bionano_access_integration.md) |
| [Schug][schug] | Proxy to Ensembl BioMart, used by `scout download ensembl`. You can use the public instance or run your own. | [External resources](admin-guide/download-resources.md) |

Tools that are commonly used to prepare data for Scout:

- [GENMOD][genmod]: annotates inheritance models and computes the rank scores Scout sorts variants by. Rank models used in Solna are in [reference-files][reference-files].
- [Stranger][stranger]: annotates STR calls from ExpansionHunter and TRGT with pathogenicity thresholds.
- [SVDB][svdb]: merges SV calls and annotates them with local frequencies.
- [scout_loader][scout_loader]: an experimental, faster Rust-based case loader.

## 9. Running the tests and contributing

- The test suite lives in [`tests/`][tests], organised to mirror the `scout/` package (`tests/adapter`, `tests/parse`, `tests/server`, and so on). The tests are a useful reference for how commands and parsers are meant to be used.
- To run the tests, including in containers with `make test`, see [Running the tests][running-tests] in CONTRIBUTING.
- Bug reports, feature requests and pull requests are very welcome. See [CONTRIBUTING][contributing] for the branching workflow and the review process.

## 10. Day-to-day operations

- [Scripts folder](admin-guide/scripts.md): useful maintenance scripts.
- [Export](admin-guide/export.md): getting data out of Scout.
- [Backup and restore](admin-guide/backup.md).
- Keep genes, transcripts, OMIM and HPO up to date by re-running the `scout update` and `scout download` commands regularly, for example from cron.

[issues]: https://github.com/Clinical-Genomics/scout/issues
[discussions]: https://github.com/Clinical-Genomics/scout/discussions
[readme]: https://github.com/Clinical-Genomics/scout/blob/main/README.md
[demo]: https://github.com/Clinical-Genomics/scout/tree/main/scout/demo
[demo-config]: https://github.com/Clinical-Genomics/scout/blob/main/scout/demo/643594.config.yaml
[config]: https://github.com/Clinical-Genomics/scout/blob/main/scout/server/config.py
[tests]: https://github.com/Clinical-Genomics/scout/tree/main/tests
[contributing]: https://github.com/Clinical-Genomics/scout/blob/main/CONTRIBUTING.md
[running-tests]: https://github.com/Clinical-Genomics/scout/blob/main/CONTRIBUTING.md#running-the-tests
[changelog]: https://github.com/Clinical-Genomics/scout/blob/main/CHANGELOG.md
[releases]: https://github.com/Clinical-Genomics/scout/releases
[pypi]: https://pypi.org/project/scout-browser/
[mongodb]: https://www.mongodb.com/docs/manual/installation/
[omim-api]: https://www.omim.org/api
[raredisease]: https://github.com/nf-core/raredisease
[nallo]: https://github.com/genomic-medicine-sweden/nallo
[balsamic]: https://github.com/Clinical-Genomics/BALSAMIC
[tomte]: https://github.com/genomic-medicine-sweden/tomte
[scout-annotation]: https://github.com/gmc-norr/scout-annotation
[genmod]: https://github.com/Clinical-Genomics/genmod
[loqusdb]: https://github.com/Clinical-Genomics/loqusdb
[chanjo2]: https://github.com/Clinical-Genomics/chanjo2
[gens]: https://github.com/SMD-Bioinformatics-Lund/gens
[reviewer-service]: https://github.com/Clinical-Genomics/Scout-REViewer-service
[reviewer]: https://github.com/Illumina/REViewer
[patientmatcher]: https://github.com/Clinical-Genomics/patientMatcher
[cgbeacon2]: https://github.com/Clinical-Genomics/cgbeacon2
[schug]: https://github.com/Clinical-Genomics/schug
[reference-files]: https://github.com/Clinical-Genomics/reference-files
[stranger]: https://github.com/Clinical-Genomics/stranger
[svdb]: https://github.com/J35P312/SVDB
[scout_loader]: https://github.com/Clinical-Genomics/scout_loader
[cg]: https://github.com/Clinical-Genomics/cg
