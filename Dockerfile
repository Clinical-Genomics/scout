###########
# BUILDER #
###########
FROM clinicalgenomics/python3.12-venv:1.0 AS python-builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the project files needed to configure dependencies build into the image
COPY --chmod=644 pyproject.toml uv.lock README.md ./

# No wheel for indirect pycairo dependency so need build env for it to install
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends gcc libcairo2-dev pkg-config python3-dev

RUN uv venv --relocatable
RUN uv sync --frozen --no-install-project --no-editable

#########
# FINAL #
#########
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="https://clinical-genomics.github.io/scout"
LABEL about.tags="Clinical,Variant triage,WGS,WES,Rare diseases,VCF,variants,SNV,Massively parallel sequencing,Next generation sequencing"
LABEL about.license="MIT License (MIT)"

# Install base dependencies
RUN apt-get update && \
     apt-get -y upgrade && \
     apt-get -y install -y --no-install-recommends wkhtmltopdf libpango-1.0-0 libpangocairo-1.0-0 && \
     apt-get clean && \
     rm -rf /var/lib/apt/lists/*

# Do not upgrade to the latest pip version to ensure more reproducible builds
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Create a non-root user to run commands
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --shell /usr/sbin/nologin --create-home worker

WORKDIR /home/worker/app

# Copy current app code to app dir
COPY --chown=root:root --chmod=755 . /home/worker/app

# Copy virtual environment from builder
COPY --chown=root:root --chmod=755 --from=python-builder /app/.venv /home/worker/app/.venv

# Install only Scout app
RUN uv pip install --no-cache-dir --editable .[coverage]

# Run the app as non-root user
USER worker

ENTRYPOINT ["uv", "run", "scout"]

