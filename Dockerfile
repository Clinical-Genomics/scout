FROM docker.io/library/fedora:32
RUN dnf -y update && dnf -y install gcc python3-pip python3-devel zlib-devel cairo pango && dnf clean all
WORKDIR /source
COPY . /source
RUN pip3 install --requirement requirements.txt .
