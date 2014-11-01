FROM dockerfile/python
ADD . /code
WORKDIR /code
RUN pip install git+https://github.com/tomchristie/mkdocs.git

EXPOSE 8000
CMD ["mkdocs", "serve"]
