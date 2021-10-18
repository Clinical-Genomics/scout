FROM python:3.8-slim AS builder
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libc-dev libz-dev libpango-1.0-0 libpangocairo-1.0-0

COPY . .
# Install scout app
RUN pip install --no-cache-dir --upgrade pip && \
    pip install  --user -r requirements.txt && \
    pip install  --user --editable .[coverage]

FROM python:3.8-slim AS build-image

COPY --from=builder /root/.local /root/.local

# update PATH environment variable
ENV PATH=/root/.local:$PATH
