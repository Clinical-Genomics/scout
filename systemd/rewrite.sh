#!/bin/bash

set -e
cd systemd
mkdir -p rewritten
for i in scout*service; do
    cat $i | sed 's/podman run /podman run --user core:core /g' > "rewritten/${i}"
done
sed -i 's/# Activate-on-FedoraCoreOS //g' scout-create-datadir.service
