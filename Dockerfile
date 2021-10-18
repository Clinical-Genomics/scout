###########
# BUILDER #
###########
FROM northwestwitch/python3.8-cyvcf2-venv:1.0 AS python-builder

ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# Install Scout dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


#########
# FINAL #
#########
FROM python:3.8-slim

LABEL base_image="python:3.8.1-slim"
LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="https://clinical-genomics.github.io/scout"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,SNP,Next generation sequencing"
LABEL about.license="MIT License (MIT)"

RUN apt-get update && \
     apt-get -y upgrade && \
     apt-get -y install -y --no-install-recommends libpango-1.0-0 libpangocairo-1.0-0

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/venv/bin:$PATH"
RUN echo export PATH="/venv/bin:\$PATH" > /etc/profile.d/venv.sh

RUN groupadd --gid 10001 worker && useradd -g worker --uid 10001 --shell /usr/sbin/nologin --create-home worker

COPY --chown=worker:worker --from=python-builder /venv /venv

WORKDIR /worker/app
COPY . /worker/app

RUN pip install --no-cache-dir --editable .[coverage]
USER worker
