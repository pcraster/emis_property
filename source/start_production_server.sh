#!/usr/bin/env bash
set -e


docker build -t test/property .
docker run -p3031:3031 test/property
