#!/usr/bin/env bash
set -euo pipefail
mkdir -p evidencias
exec > >(tee evidencias/docker.log) 2>&1
docker version
docker build --progress=plain -t aclaraciones-ia:fase2 .
docker run -d --name aclaraciones-fase2 -p 127.0.0.1:8000:8000 aclaraciones-ia:fase2
trap 'docker logs aclaraciones-fase2; docker rm -f aclaraciones-fase2' EXIT
ready=0
for i in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8000/health; then ready=1; break; fi
  sleep 1
done
test "$ready" = 1
BASE_URL=http://127.0.0.1:8000 python3 tests/validar.py
docker inspect --format '{{.Image}} {{.State.Status}}' aclaraciones-fase2
