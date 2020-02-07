#!/bin/bash

echo $CMD

scout --port $MONGO_PORT --host $MONGO_HOST $CMD
