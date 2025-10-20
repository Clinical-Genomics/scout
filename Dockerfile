###########
# BUILDER #
###########
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS python-builder

WORKDIR /app

COPY --chmod=644 pyproject.toml uv.lock README.md ./

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends build-essential libffi-dev

RUN uv venv --relocatable
RUN uv sync --frozen --no-install-project --no-editable

#########
# FINAL #
#########
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="https://clinical-genomics.github.io/scout"
LABEL about.tags="Clinical,Variant triage,WGS,WES,Rare diseases,VCF,variants,SNV,Massively parallel sequencing,Next generation sequencing"
LABEL about.license="MIT License (MIT)"

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends git wkhtmltopdf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --shell /usr/sbin/nologin --create-home worker

ENV PATH="/home/worker/app/.venv/bin:$PATH"
WORKDIR /home/worker/app

COPY --chown=root:root --chmod=755 . /home/worker/app
COPY --from=python-builder /app/.venv /home/worker/app/.venv
RUN chown -R worker:worker /home/worker/app/.venv

USER worker
RUN uv pip install --no-cache-dir --editable .[coverage]

ENTRYPOINT ["uv", "run", "scout"]
