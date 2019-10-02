FROM python:3.6.9

MAINTAINER Nina Norgren <nina.karlsson.norgren@regionvasterbotten.se>

RUN mkdir /scout
COPY requirements.txt /scout/

RUN apt-get update && apt-get install -y libffi-dev ssl-cert ca-certificates && apt-get clean autoclean

RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org Cython
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org pytest-runner
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org cffi
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org cairocffi==1.0.2

RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /scout/requirements.txt

COPY . /scout/

COPY certs/vll.crt /usr/local/share/ca-certificates/vll.crt
RUN update-ca-certificates

WORKDIR /scout/

EXPOSE 443

RUN chmod +x /scout/docker-entrypoint.sh

CMD ["/scout/docker-entrypoint.sh"]
