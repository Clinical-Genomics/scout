FROM python:3.6.8

RUN mkdir /scout

COPY . /scout/

WORKDIR /scout/

RUN apt-get update && apt-get install -y libffi-dev && apt-get clean autoclean

RUN pip install -r /scout/requirements.txt --editable .

EXPOSE 443

RUN chmod +x /scout/docker-entrypoint.sh

CMD ["/scout/docker-entrypoint.sh"]
