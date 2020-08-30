#!/bin/bash

set -e
cd systemd
mkdir -p rewritten
for i in scout*service; do
    cat $i | sed 's/\[Service\]/[Service]\nUser=core\nGroup=core/g' > "rewritten/${i}"
done
