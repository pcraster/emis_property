#!/usr/bin/env bash
set -e


docker build -t test/property .
docker run --env ENV=DEVELOPMENT -p5000:5000 -v$(pwd)/property:/property test/property
