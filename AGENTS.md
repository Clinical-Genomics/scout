# Scout AI Coding Agent Guide

## Architecture and navigation

Scout is a Flask application for genomic variant and multiomics analysis, backed by MongoDB.
The app factory is `create_app` in `scout/server/app.py`; the Click/Flask CLI entry point is
`scout/commands/base.py` (`scout.commands:cli` in `pyproject.toml`).

The usual ingestion flow is CLI -> parsing/validation -> building MongoDB documents -> loading
through the adapter. Follow the existing implementation and corresponding tests for the data type
being changed.

- `scout/commands/`: CLI commands for setup, loading, updating, exporting, viewing, and indexing.
- `scout/parse/`: Parsers for case configs, VCF annotations, genes, and phenotype resources.
- `scout/build/`: Converts parsed data into documents for storage.
- `scout/load/`: Ingestion pipelines for cases, variants, gene panels, and reference resources.
- `scout/adapter/mongo/`: MongoDB operations and queries; `MongoAdapter` also serves as the Flask
  `store` extension. Keep database query logic in the adapter.
- `scout/models/`: Mostly dictionary schema descriptions, including `case/case.py` and
  `variant/variant.py`. Pydantic v2 is used in specific validation models, notably
  `case/case_loading_models.py`; follow the model used by the relevant code path.
- `scout/server/blueprints/`: UI and API features, split into `views.py`, `controllers.py`,
  `forms.py`, `utils.py`, templates, and static assets. `variants/` handles lists and filters;
  `variant/` handles variant details. Check `omics_variants/` and `dark_regions/` when relevant.
- `scout/constants/`: Shared categories, file mappings, and index definitions.
- `scout/utils/`: Shared helpers; ACMG and cancer classification logic is in `acmg.py` and `ccv.py`.
- `tests/`: Generally mirrors the source layout; shared fixtures are in `tests/conftest.py` and
  more specific `conftest.py` files.
- `docs/`: MkDocs user and admin guides; case loading is described in
  `docs/admin-guide/load-config.md` and `docs/admin-guide/loading-case.md`.

## Environment and checks

Use `uv` and the committed `uv.lock`. `pyproject.toml` declares supported Python versions and
dependency groups; `.python-version` selects the development/CI interpreter.

```bash
uv sync --frozen --dev
uv run --frozen --dev pytest tests/path/to/test_file.py
```

Run tests relevant to the changed behavior first. For wider validation, CI uses
`uv run --frozen --dev pytest --cov`, split into eight groups. `pytest.ini` adds `-v -x`, so the
default run stops at the first failure; add `-o addopts=` to report every failure.

- Tests use both `mongomock` and real MongoDB. Fixtures such as `real_adapter`,
  `real_populated_database`, and the server `app` fixture require MongoDB on localhost:27017.
  CI uses MongoDB 7. Inspect fixture dependencies before assuming a test needs no external service.
  The tests create and drop `realtestdb` and `testdb` (suffixed per worker, e.g. `realtestdb_gw0`),
  so never point them at a MongoDB holding data worth keeping.
- PDF report tests need the system executable `wkhtmltopdf`; Python dependencies alone are
  insufficient. See `.github/workflows/tests_and_cov.yml` for CI setup.
- `pytest-xdist` is in the dev group. For larger runs, parallelize with `-n auto`
  (e.g. `uv run --frozen --dev pytest -o addopts= -n auto tests`); for a few test files, a serial
  run is usually faster because starting the workers takes a few seconds.
- When MongoDB or `wkhtmltopdf` is not available locally, `make test` (needs only Docker) runs the
  suite in a test image against a throwaway, unpublished MongoDB 7. Use `TESTS=<pytest path or id>`
  for a subset and `WORKERS=0` for a serial run; the default is `auto`. The test image is amd64-only
  (emulated on Apple Silicon), so prefer `uv` when the services are available.
  See "Running the tests" in `CONTRIBUTING.md`.
- Reuse fixtures and the existing HTTP mocks (`responses` or `mocker`) for integration tests.
  Add regression tests for behavior changes; report unavailable services or tools when checks
  cannot run.

For changed Python files, use the `lint` dependency group (replace the placeholder with file paths):

```bash
uv run --frozen --group lint black --check <changed-python-files>
uv run --frozen --group lint isort --check-only --diff --line-length 100 <changed-python-files>
uv run --frozen --group lint flake8 --select=E9,F63,F7,F82 \
  --max-line-length 100 <changed-python-files>
```

Black uses 100-character lines and isort uses the Black profile. Ruff is available in the lint
group, but CI currently checks Black, isort, and selected Flake8 errors; see
`.github/workflows/linting_only.yml`. The pre-commit configuration runs Black.
For documentation changes, use `uv run --frozen --group docs mkdocs build --strict` when relevant.

## Configuration

- Flask defaults are in `scout/server/config.py`. Use a Python config file with uppercase settings
  via `scout --flask-config /absolute/path/scoutconfig.py ...`.
- `scout/utils/config.py` merges defaults < Python config < legacy YAML CLI config < non-None
  CLI options. `scout/commands/base.py` prepares these inputs; `create_app` overlays the result
  onto Flask defaults. Legacy `scout --config` YAML settings are deprecated but still supported.
- YAML **case load configs** remain supported by `scout load case`; they are separate from server
  configuration. Validate these through `scout/parse/case.py` and the case loading models.
- The MongoDB extension also reads `MONGO_*` environment variables, which override corresponding
  app config values. Check these when debugging connections or unexpected database selection.
- `--demo` selects `scout-demo`. The WSGI entry point `scout/server/auto.py` reads the Python
  config path from `SCOUT_CONFIG`.

## CLI workflows

Global options such as `--flask-config`, `--mongodb`, and `--demo` go before the subcommand.
Use `uv run --frozen scout ...` for commands in the project environment.

- Demo: `uv run --frozen scout setup demo`, then `uv run --frozen scout --demo serve`.
- Load a panel: `uv run --frozen scout load panel scout/demo/panel_1.txt`.
- Load a case: `uv run --frozen scout load case scout/demo/643594.config.yaml`.
- Inspect a case: `uv run --frozen scout view cases --case-id <case_id>`.
- Indexes: `uv run --frozen scout index --update` adds missing indexes; without `--update`,
  configured indexes are rebuilt. `--collection` limits the affected collections. Setup already
  creates indexes; indexing is not a required step after every case load.
- `scout setup database` loads reference resources and initializes the database, **deleting
  existing collections**. `setup demo` also resets its target collections. Use a disposable
  development database for setup; do not bypass confirmation prompts on an existing database
  unless resetting it is explicitly intended.
- `scout serve` still works but is deprecated. Flask's development server can use the WSGI entry
  point with a Python config:

```bash
SCOUT_CONFIG=/absolute/path/scoutconfig.py \
  uv run --frozen flask --app scout.server.auto:app run --debug
```

## Integrations and conventions

Check `configure_extensions` in `scout/server/app.py` and the relevant extension before changing
integration behavior. Enablement depends on config, including:

- Coverage: `SQLALCHEMY_DATABASE_URI` for Chanjo; `CHANJO2_URL` for Chanjo2.
- Local frequencies and copy number visualization: `LOQUSDB_SETTINGS` and `GENS_HOST`.
- Matchmaker Exchange: `MME_URL`, `MME_ACCEPTS`, and `MME_TOKEN` are all required.
- Beacon: `BEACON_URL` and `BEACON_TOKEN`.
- ClinVar: the in-repository client is `scout/server/extensions/clinvar_extension.py`.
- IGV: `CUSTOM_IGV_TRACKS`, `CLOUD_IGV_TRACKS`, or `CUSTOM_REFERENCE`;
  see `AlignTrackHandler` in `scout/utils/track_resources.py`.
- Authentication: `LDAP_HOST`, `GOOGLE`, or `KEYCLOAK`; follow existing login and access checks.
  Other optional services are also registered in `configure_extensions`.

Follow nearby import and docstring conventions: the code uses both absolute `scout.*` imports
and relative imports, with Args/Returns-style docstrings. Add type hints for new and changed
functions. Include docstrings for functions/classes.
Use `logging.getLogger(__name__)`; logging setup and handlers are in `scout/log/`.
Preserve genome build and clinical/research distinctions when changing parsers, queries, and UI.

Target `main` for feature branches and PRs, as configured in current workflows; the `master`
references in `CONTRIBUTING.md` are stale. Include tests and an entry in the top `CHANGELOG.md`
section for new functionality or bug fixes, and update user/admin docs for changed behavior.
Use `.github/pull_request_template.md` for validation details. Consult the current source and
workflow files when older documentation disagrees with them.
