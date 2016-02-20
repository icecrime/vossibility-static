#!/bin/bash
set -e

while true
do
    echo $(date --rfc-3339=seconds) 'Exporting dashboards...'
    python main.py $*
    sleep 3600
done
