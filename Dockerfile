FROM python:3.6.8

RUN mkdir /scout

COPY . /scout/

WORKDIR /scout/

RUN apt-get update && apt-get install -y libffi-dev ssl-cert ca-certificates && apt-get clean autoclean

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /scout/requirements.txt --editable .

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org werkzeug==0.16.0

RUN pip install gunicorn==19.9.0

COPY certs/vll.crt /usr/local/share/ca-certificates/vll.crt
RUN update-ca-certificates

WORKDIR /scout/

EXPOSE 443

RUN chmod +x /scout/docker-entrypoint.sh

CMD ["/scout/docker-entrypoint.sh"]
