###########
# BUILDER #
###########
FROM clinicalgenomics/python3.11-venv:1.0 AS python-builder

ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# Install Scout dependencies
COPY requirements.txt .
# No wheel for indirect pycairo dependency so need build env for it to install
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends gcc libcairo2-dev pkg-config python3-dev
RUN pip install --no-cache-dir -r requirements.txt

#########
# FINAL #
#########
FROM python:3.11-slim-bullseye

LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="https://clinical-genomics.github.io/scout"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,SNP,Next generation sequencing"
LABEL about.license="MIT License (MIT)"

# Install base dependencies
RUN apt-get update && \
     apt-get -y upgrade && \
     apt-get -y install -y --no-install-recommends wkhtmltopdf libpango-1.0-0 libpangocairo-1.0-0 && \
     apt-get clean && \
     rm -rf /var/lib/apt/lists/*

# Do not upgrade to the latest pip version to ensure more reproducible builds
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/venv/bin:$PATH"
RUN echo export PATH="/venv/bin:\$PATH" > /etc/profile.d/venv.sh

# Create a non-root user to run commands
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --shell /usr/sbin/nologin --create-home worker

# Copy virtual environment from builder
COPY --chown=worker:worker --from=python-builder /venv /venv

WORKDIR /home/worker/app
COPY --chown=worker:worker . /home/worker/app

# Install only Scout app
RUN pip install --no-cache-dir --editable .[coverage]

# Run the app as non-root user
USER worker
