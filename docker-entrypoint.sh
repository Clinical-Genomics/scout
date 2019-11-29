#!/bin/bash

SCOUT_CONFIG=$CONF_FILE \
gunicorn \
   --workers=4 \
   --bind=$HOST:$PORT \
   --keyfile=$KEY_FILE \
   --certfile=$CERT_FILE \
   scout.server.auto:app

#scout --port $MONGO_PORT --host $MONGO_HOST --demo serve

