#!/bin/bash

SCOUT_CONFIG="/scout/vault/flask.config.py" \
gunicorn \
   --workers=4 \
   --bind=$HOST:$PORT \
   --keyfile="/scout/vault/key.pem" \
   --certfile="/scout/vault/cert.pem" \
   scout.server.auto:app
