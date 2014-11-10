FROM dockerfile/python
ADD . /code
WORKDIR /code
RUN pip install mkdocs

EXPOSE 3001
CMD ["mkdocs", "serve"]
