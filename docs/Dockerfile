FROM dockerfile/python
ADD . /code
WORKDIR /code
RUN pip install mkdocs

EXPOSE 8000
CMD ["mkdocs", "serve"]
