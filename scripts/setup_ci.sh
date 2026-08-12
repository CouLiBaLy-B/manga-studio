#!/usr/bin/env bash
# Script pour déployer les workflows CI/CD dans .github/workflows lorsque les permissions GitHub le permettent
set -euo pipefail

mkdir -p .github/workflows
cp ci/workflows/*.yml .github/workflows/
echo "Workflows CI/CD copiés avec succès dans .github/workflows/"
