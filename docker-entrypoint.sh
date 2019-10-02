#!/bin/bash

SCOUT_CONFIG="/scout/vault/flask.config.py" \
gunicorn \
   --workers=4 \
   --bind=$HOST:$PORT \
   --keyfile="vault/key.pem" \
   --certfile="vault/cert.pem" \
   scout.server.auto:app
