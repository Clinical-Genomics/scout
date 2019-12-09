#!/bin/bash

scout --port $MONGO_PORT --host $MONGO_HOST delete case -c $SAMPLEID -i $INSTID
