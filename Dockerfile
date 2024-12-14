###########
# BUILDER #
###########
FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS python-builder

WORKDIR /app

# Copy the project files needed to configure dependencies build into the image
COPY pyproject.toml uv.lock README.md .

# No wheel for indirect pycairo dependency so need build env for it to install
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends gcc libcairo2-dev pkg-config python3-dev

RUN uv sync --frozen

#########
# FINAL #
#########
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

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
COPY --chown=worker:worker . /home/worker/app

# Copy virtual environment from builder
COPY --chown=worker:worker --from=python-builder /app/.venv /home/worker/app/.venv

# Install only Scout app
RUN uv pip install --no-cache-dir --editable .[coverage]

# Run the app as non-root user
USER worker

ENTRYPOINT ["uv", "run", "scout"]

