FROM python:3.6.8

RUN mkdir /scout

COPY . /scout/

WORKDIR /scout/

RUN apt-get update && apt-get install -y libffi-dev && apt-get clean autoclean

#RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org Cython
#RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy
#RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org pytest-runner
#RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org cffi
#RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org cairocffi==1.0.2

RUN pip install -r /scout/requirements.txt --editable .

EXPOSE 443

RUN chmod +x /scout/docker-entrypoint.sh

CMD ["/scout/docker-entrypoint.sh"]
