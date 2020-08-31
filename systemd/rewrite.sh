#!/bin/bash

set -e
cd systemd
mkdir -p rewritten
for i in scout*service; do
 #   cat $i | sed 's/podman run /podman run --user core:core /g' > "rewritten/${i}"
   cat $i  > "rewritten/${i}"
done
#cat scout-create-datadir.service | sed 's/# Activate-on-FedoraCoreOS //g' > rewritten/scout-create-datadir.service
