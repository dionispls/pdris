#!/bin/bash
set -e

cd "$(dirname "$0")/.."

docker network create foodgram_network || true
docker-compose down || true
docker-compose pull || true
docker-compose up -d
