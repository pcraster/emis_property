#!/usr/bin/env bash
set -e


docker build -t test/property .
docker run --env ENV=TEST -p5000:5000 test/property
