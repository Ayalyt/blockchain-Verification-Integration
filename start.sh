#!/bin/bash
echo "HOST_PROJECT_PATH=$(pwd)" > .env

docker-compose up -d compiler-verification cipher-verification smartifsyn-test compiler-testing

docker-compose run --rm orchestrator python3 orchestrator/main.py