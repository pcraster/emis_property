#!/usr/bin/env bash
set -e


docker build -t test/emis_property .
docker run \
    --env EMIS_CONFIGURATION=development \
    -p5000:5000 \
    -v$(pwd)/emis_property:/emis_property \
    test/emis_property
