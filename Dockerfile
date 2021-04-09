FROM python:3.8-alpine3.13

LABEL base_image="python:3.8-alpine3.13"
LABEL about.home="https://github.com/Clinical-Genomics/scout"
LABEL about.documentation="https://clinical-genomics.github.io/scout"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,SNP,Next generation sequencing"
LABEL about.license="MIT License (MIT)"

# Install required libs
RUN apk update
RUN apk --no-cache add make automake gcc g++ linux-headers libffi-dev zlib-dev \
   jpeg-dev libressl-dev cairo-dev pango-dev gdk-pixbuf ttf-freefont bash \
   autoconf musl-dev perl bzip2-dev xz-dev curl-dev
RUN pip install numpy Cython

# Install cyvcf2-master
RUN apk --no-cache add git
WORKDIR /tmp
RUN git clone --recursive https://github.com/brentp/cyvcf2
WORKDIR /tmp/cyvcf2/htslib
RUN autoheader
RUN autoconf
RUN ./configure --enable-libcurl
RUN make
WORKDIR /tmp/cyvcf2
RUN pip install -r requirements.txt
RUN CYTHONIZE=1 pip install -e .

# Install other Scout requirements
# do this first in order to have it cached when small changes happen..
WORKDIR /home/worker/app
COPY requirements.txt /home/worker/app
RUN pip install -r requirements.txt

# install Scout dev requirements if developer
#COPY requirements-dev.txt /home/worker/app
#RUN pip install -r requirements-dev.txt

COPY . /home/worker/app

# Install scout app
RUN pip install -e .

# Run commands as non-root user
RUN adduser -D worker
RUN chown worker:worker -R /home/worker
USER worker
