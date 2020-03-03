#!/bin/bash

scout --port $MONGO_PORT --host $MONGO_HOST load panel --panel-id $ID --institute $INSTID panels/$PANEL
