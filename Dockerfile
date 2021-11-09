###########
# BUILDER #
###########
FROM python:3.8.1-slim as builder

WORKDIR /usr/src/app

# Set build variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update &&                                               \
    apt-get upgrade -y &&                                           \
    apt-get install -y --no-install-recommends autoconf automake    \
	build-essential gcc libbz2-dev libcairo2 libcurl4-gnutls-dev    \
	libffi-dev libgdk-pixbuf2.0-0 liblzma-dev libpango-1.0-0        \
	libpangocairo-1.0-0 libssl-dev make python3-cffi python3-dev    \
	python3-pip python3-wheel shared-mime-info zlib1g-dev           \
	openssl ca-certificates gcc wget git

# Copy app
COPY . /usr/src/app
RUN pip install --no-cache-dir --upgrade pip &&           \
    pip wheel --no-cache-dir --no-deps     \
        --wheel-dir /usr/src/app/wheels    \
		Cython gunicorn  &&                \
    pip wheel --no-cache-dir               \
        --wheel-dir /usr/src/app/wheels    \
        --editable .[coverage]


#########
# FINAL #
#########

FROM python:3.8.1-slim

LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="https://clinical-genomics.github.io/scout"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,SNP,Next generation sequencing"
LABEL about.license="MIT License (MIT)"

# Run app on non-root user
RUN useradd -m worker && mkdir -p /home/worker/app
WORKDIR /home/worker/app

# Copy pyhon wheels and install scout
COPY --from=builder /usr/src/app/wheels /wheels
RUN apt-get update &&                                     \
    apt-get install -y --no-install-recommends libgdk-pixbuf2.0-0 libpango-1.0-0  \
	libcairo2 libpangocairo-1.0-0 ssh sshfs &&            \
    pip install --no-cache-dir --upgrade pip &&           \
    pip install --no-cache-dir /wheels/* &&               \
    rm -rf /var/lib/apt/lists/* /wheels

COPY . /home/worker/app

# Run app on non-root user
RUN chown -R worker:worker /home/worker/app
USER worker
