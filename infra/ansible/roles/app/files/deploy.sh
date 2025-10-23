#!/bin/bash
set -e

cd /Users/kate/pdris/infra/

docker network create foodgram_network || true
docker-compose down
docker-compose build
docker-compose up -d
