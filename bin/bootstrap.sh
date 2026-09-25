#!/usr/bin/env bash
# bootstrap.sh — Install the AI-G&O ai/ framework into a project directory.
# Downloads the latest release from GitHub. Does not require cloning the repository.
#
# Usage:
#   bash bootstrap.sh <project-root>
#   curl -fsSL https://raw.githubusercontent.com/William12556/AI-Governance-and-Orchestration/main/bin/bootstrap.sh | bash -s -- <project-root>
#
# The script creates <project-root>/ai/ from the latest framework release.
# Review ai/ael/config.yaml before first use.

set -euo pipefail

REPO="William12556/AI-Governance-and-Orchestration"
GITHUB_API="https://api.github.com/repos/${REPO}"

# --- Argument validation ---------------------------------------------------

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <project-root>" >&2
    exit 1
fi

if [[ ! -d "$1" ]]; then
    echo "Error: project directory not found: $1" >&2
    exit 1
fi

PROJECT_ROOT="$(cd "$1" && pwd)"
PROJECT_AI="${PROJECT_ROOT}/ai"

if [[ -d "${PROJECT_AI}" ]]; then
    echo "Error: ai/ already exists at ${PROJECT_AI}" >&2
    echo "To update an existing installation use bin/propagate.sh from the AI-G&O repository." >&2
    exit 1
fi

# --- Dependency check ------------------------------------------------------

if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required" >&2
    exit 1
fi

# --- Resolve latest release ------------------------------------------------

echo "==> Resolving latest release..."

TAG=$(curl -fsSL "${GITHUB_API}/releases/latest" \
    | grep '"tag_name"' \
    | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/')

if [[ -z "${TAG}" ]]; then
    echo "Error: could not resolve latest release tag" >&2
    exit 1
fi

echo "    Latest release: ${TAG}"

# --- Download tarball -------------------------------------------------------

ASSET="ai-framework-${TAG}.tar.gz"
URL="https://github.com/${REPO}/releases/download/${TAG}/${ASSET}"
TMPWORK="$(mktemp -d)"
TARBALL="${TMPWORK}/${ASSET}"

echo "==> Downloading ${ASSET}..."
curl -fsSL --output "${TARBALL}" "${URL}"

# --- Extract ----------------------------------------------------------------

echo "==> Extracting to ${PROJECT_ROOT}/ai/..."
tar -xz -C "${PROJECT_ROOT}" -f "${TARBALL}"

# --- Cleanup ----------------------------------------------------------------

rm -rf "${TMPWORK}"

echo ""
echo "Done."
echo "Review ai/ael/config.yaml before first use: ${PROJECT_AI}/ael/config.yaml"
