#!/usr/bin/env bash
set -e


docker build -t test/property .
docker run -p9090:9090 test/property
