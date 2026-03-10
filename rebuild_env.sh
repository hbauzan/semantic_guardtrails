#!/bin/bash
set -e
echo "⚠️ Destruyendo sg_env..."
rm -rf sg_env
echo "♻️ Reconstruyendo..."
./bootstrap.sh
