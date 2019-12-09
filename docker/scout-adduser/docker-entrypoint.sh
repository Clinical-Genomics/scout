#!/bin/bash

scout --port $MONGO_PORT --host $MONGO_HOST load user -i $INSTID -u $NAME -id $ADID -m $USERMAIL $ADMIN

