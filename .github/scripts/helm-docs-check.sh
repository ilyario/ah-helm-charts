#!/usr/bin/env bash
# Fails when chart READMEs are stale relative to values.yaml (helm-docs).
# Regenerates charts/*/README.md from README.md.gotmpl templates, then requires
# the tree to be clean, i.e. committed READMEs must match generated output.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if command -v helm-docs >/dev/null 2>&1; then
  helm-docs
else
  # Fallback for CI runners without the binary
  docker run --rm --workdir /data -v "$ROOT":/data jnorwood/helm-docs:1.14.2
fi

if ! git diff --exit-code -- charts/citadel-monolith/README.md charts/static-proxy/README.md >/dev/null 2>&1; then
  echo "Chart READMEs are out of date - run helm-docs and commit the updated README.md files" >&2
  git diff --stat -- charts/*/README.md >&2 || true
  exit 1
fi

echo "helm-docs: chart READMEs are up to date"
