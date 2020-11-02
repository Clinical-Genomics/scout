FROM python:3.8-alpine3.12

LABEL base_image="python:3.8-alpine3.12"
LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="http://www.clinicalgenomics.se/scout"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,SNP,Next generation sequencing"
LABEL about.license="MIT License (MIT)"

# Install required libs
RUN apk update
RUN apk --no-cache add make automake gcc g++ linux-headers libffi-dev zlib-dev \
   jpeg-dev libressl-dev
RUN pip install numpy Cython

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install scout app
RUN pip install -r requirements.txt
RUN pip install -e .

# Run commands as non-root user
RUN adduser -D worker
RUN chown worker:worker -R /home/worker
USER worker
