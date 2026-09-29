#!/usr/bin/env bash
# release.sh — Create a versioned GitHub release with the ai/ framework tarball.
#
# Usage:
#   bin/release.sh <version>
#
# Example:
#   bin/release.sh v1.0.0
#
# Prerequisites:
#   - gh (GitHub CLI) installed and authenticated
#   - Run from the repository root
#   - No uncommitted changes in the repository

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AI_SRC="${REPO_ROOT}/ai"

# --- Argument validation ---------------------------------------------------

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <version>" >&2
    echo "Example: $0 v1.0.0" >&2
    exit 1
fi

VERSION="$1"

if [[ ! "${VERSION}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: version must be in format vX.Y.Z (e.g. v1.0.0)" >&2
    exit 1
fi

# --- Dependency checks -----------------------------------------------------

if ! command -v gh >/dev/null 2>&1; then
    echo "Error: gh (GitHub CLI) is required" >&2
    echo "Install: brew install gh" >&2
    exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "Error: gh is not authenticated" >&2
    echo "Run: gh auth login" >&2
    exit 1
fi

# --- Repository state checks -----------------------------------------------

if [[ -n "$(git -C "${REPO_ROOT}" status --porcelain)" ]]; then
    echo "Error: uncommitted changes in repository" >&2
    echo "Commit or stash before releasing." >&2
    exit 1
fi

if git -C "${REPO_ROOT}" tag | grep -q "^${VERSION}$"; then
    echo "Error: tag ${VERSION} already exists" >&2
    exit 1
fi

# --- Archive ai/ -----------------------------------------------------------

ASSET="ai-framework-${VERSION}.tar.gz"
TMPWORK="$(mktemp -d)"
TARBALL="${TMPWORK}/${ASSET}"

echo "==> Archiving ai/ as ${ASSET}..."

tar -cz \
    --exclude='ai/state' \
    --exclude='ai/logs' \
    --exclude='ai/config.yaml' \
    --exclude='ai/workspace' \
    --exclude='ai/dashboard-alerts.md' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='.DS_Store' \
    -C "${REPO_ROOT}" \
    -f "${TARBALL}" \
    ai/

echo "    Archive: $(du -sh "${TARBALL}" | cut -f1)"

# --- Tag and push ----------------------------------------------------------

echo "==> Creating tag ${VERSION}..."
git -C "${REPO_ROOT}" tag "${VERSION}"
git -C "${REPO_ROOT}" push origin "${VERSION}"

# --- Create GitHub release -------------------------------------------------

echo "==> Creating GitHub release ${VERSION}..."
gh release create "${VERSION}" \
    --title "${VERSION}" \
    --notes "ai/ framework release ${VERSION}" \
    "${TARBALL}"

# --- Cleanup ---------------------------------------------------------------

rm -rf "${TMPWORK}"

echo ""
echo "Done. Release ${VERSION} published."
echo "    https://github.com/William12556/AI-Governance-and-Orchestration/releases/tag/${VERSION}"
