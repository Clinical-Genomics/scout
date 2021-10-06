###########
# BUILDER #
###########

from northwestwitch/python3.8.1-slim_numpy AS builder

LABEL base_image="northwestwitch/python3.8.1-slim_numpy"
LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="https://clinical-genomics.github.io/scout"
LABEL about.tags="WGS, WES, rare diseases, cancer, VCF, variants, SNP, next generation sequencing"
LABEL about.license="MIT License (MIT)"

# Install the required libraries
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    zlib1g-dev libffi-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0

# Run app on non-root user
RUN useradd -m worker && mkdir -p /home/worker/app
WORKDIR /home/worker/app

# Activate a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the app to the container
COPY . /home/worker/app

# Install the app with its requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --editable .[coverage] && \
    pip install gunicorn


#########
# FINAL #
#########

FROM scratch
WORKDIR /home/worker/app
COPY --from=builder /home/worker/app /home/worker/app

# Run it as non-root user
RUN chown -R worker:worker /home/worker/app
USER worker
