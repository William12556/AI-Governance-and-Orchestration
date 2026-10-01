#!/usr/bin/env bash
# bootstrap.sh — Install the AI-G&O ai/ framework into a project directory.
# Downloads the latest release from GitHub. Does not require cloning the repository.
#
# Usage:
#   bash bootstrap.sh <project-root>
#   curl -fsSL https://raw.githubusercontent.com/William12556/AI-Governance-and-Orchestration/main/bin/bootstrap.sh | bash -s -- <project-root>
#
# The script creates <project-root>/ai/ from the latest framework release.
# Review ai/config.yaml before first use.

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

# --- Seed project files ----------------------------------------------------
# One governance model per project (proposal-5bcd46ad D-05).

MODEL="software-engineering"
[[ -e "${PROJECT_AI}/config.yaml" ]] || cp "${PROJECT_AI}/engine/config.template.yaml" "${PROJECT_AI}/config.yaml"
[[ -e "${PROJECT_AI}/context.md" ]]  || cp "${PROJECT_AI}/governance/${MODEL}/seed/context.md" "${PROJECT_AI}/context.md"
[[ -e "${PROJECT_AI}/task.md" ]]     || cp "${PROJECT_AI}/governance/${MODEL}/seed/task.md" "${PROJECT_AI}/task.md"

# --- Workspace folders (change-e58fd295, FR-01-04) ---------------------------
# Creates each ai/workspace/<folder> listed under workspace_folders: in the
# governance model manifest when absent. Existing paths are never changed; a
# non-directory in the way is reported and left alone.
create_workspace_folders() {
    local manifest="$1" workspace="$2" d
    [[ -f "${manifest}" ]] || { echo "workspace: no manifest at ${manifest}; folders not created"; return 0; }
    while IFS= read -r d; do
        [[ -z "${d}" || "${d}" == /* || "/${d}/" == */../* ]] && continue
        if [[ -e "${workspace}/${d}" || -L "${workspace}/${d}" ]]; then
            [[ -d "${workspace}/${d}" ]] || echo "workspace: ${d} exists and is not a directory; left unchanged"
            continue
        fi
        mkdir -p "${workspace}/${d}" && echo "workspace: created ${d}/"
    done < <(awk '/^workspace_folders:/{f=1;next} f&&/^[^[:space:]#]/{f=0} f&&/^[[:space:]]*-[[:space:]]/{sub(/^[[:space:]]*-[[:space:]]*/,"");sub(/[[:space:]]*#.*$/,"");gsub(/["\047]/,"");print}' "${manifest}")
}
create_workspace_folders "${PROJECT_AI}/governance/${MODEL}/manifest.yaml" "${PROJECT_AI}/workspace"

# --- Cleanup ----------------------------------------------------------------

rm -rf "${TMPWORK}"

echo ""
echo "Done."
echo "Review ai/config.yaml and ai/context.md before first use: ${PROJECT_AI}/config.yaml"
