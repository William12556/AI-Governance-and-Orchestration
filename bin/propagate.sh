#!/usr/bin/env bash
# propagate.sh — Push ai/ to a downstream project ai/ directory.
#
# PREREQUISITE: The LLM-Governance-and-Orchestration repository must be
# cloned locally. This script must be run from the repository root.
# Clone: https://github.com/William12556/LLM-Governance-and-Orchestration
#
# Usage:
#   bin/propagate.sh [--yes] [--allow-major] <project-root>
#
#   --yes          apply without the interactive prompt (required when stdin
#                  is not a terminal; without it a non-TTY run fails loudly)
#   --allow-major  permit a run where source and target governance differ by
#                  a major version (required with --yes in that case)
#
# Example:
#   bin/propagate.sh ~/Documents/GitHub/<project name>
#
# The script mirrors ai/ into <project-root>/ai/ (rsync --delete), so files
# renamed or retired in the source are removed from the target. Governance-
# declared project files are never touched (see Excludes below). Any other
# target file absent from the source is classified by content (see Classify):
# an unmodified framework file is deleted; anything else is project content and
# is moved to <project-root>/ai-local/ and logged there (governance P10.6).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AI_SRC="${REPO_ROOT}/ai"

# --- Argument validation ---------------------------------------------------

ASSUME_YES="false"
ALLOW_MAJOR="false"
POSITIONAL=()
for arg in "$@"; do
    case "${arg}" in
        --yes)         ASSUME_YES="true" ;;
        --allow-major) ALLOW_MAJOR="true" ;;
        -*)            echo "Error: unknown option ${arg}" >&2; exit 1 ;;
        *)             POSITIONAL+=("${arg}") ;;
    esac
done

if [[ ${#POSITIONAL[@]} -ne 1 ]]; then
    echo "Usage: $0 [--yes] [--allow-major] <project-root>" >&2
    exit 1
fi

PROJECT_ROOT="$(cd "${POSITIONAL[0]}" && pwd)"
PROJECT_AI="${PROJECT_ROOT}/ai"

if [[ ! -d "${AI_SRC}" ]]; then
    echo "Error: ai/ not found at ${AI_SRC}" >&2
    exit 1
fi

if [[ ! -d "${PROJECT_AI}" ]]; then
    echo "Error: target ai/ directory not found at ${PROJECT_AI}" >&2
    exit 1
fi

# --- Governance version check ---------------------------------------------
# A major version difference is when renames occur (e.g. 9.x -> 10.x renamed
# seven templates). Such a run is permitted, but never silently.

gov_version() {
    # Last row of the governance.md Version History table, e.g. "10.2".
    grep -E '^\| *[0-9]+\.[0-9]+ *\|' "$1" 2>/dev/null | tail -1 \
        | sed -E 's/^\| *([0-9]+\.[0-9]+).*/\1/'
}

SRC_VER="$(gov_version "${AI_SRC}/governance.md")"
DST_VER="$(gov_version "${PROJECT_AI}/governance.md")"
MAJOR_CHANGE="false"
if [[ -n "${SRC_VER}" && -n "${DST_VER}" && "${SRC_VER%%.*}" != "${DST_VER%%.*}" ]]; then
    MAJOR_CHANGE="true"
fi

# --- Excludes --------------------------------------------------------------
# Project-specific files that must never be overwritten in the target.

# Path-specific excludes are anchored with a leading '/' (relative to the
# transfer root, ai/) so each matches only its intended file. Unanchored, a
# basename pattern matches at any depth: 'workspace/' would also exclude a
# downstream ai/doc/workspace/, and 'config.yaml' any config.yaml anywhere
# under ai/. Only the genuinely depth-independent patterns below — editor and
# interpreter droppings — remain unanchored.

EXCLUDES=(
    --exclude='/ael/config.yaml'    # project-specific AEL configuration
    --exclude='/context.md'         # project-specific conventions/stack; seeded below when absent
    --exclude='/task.md'            # project-specific open-work register; seeded below when absent
    --exclude='/workspace/'         # project-local governance documents
    --exclude='/state/'             # AEL runtime state (post-2026-06-16 path; was ael/state/)
    --exclude='/dashboard-alerts.md' # govwatch write target
    --exclude='.DS_Store'
    --exclude='__pycache__/'
    --exclude='*.pyc'
    --exclude='*.pyo'
)

# --- Classify --------------------------------------------------------------
# change-c5270084 (iteration 2): a target file that --delete would remove is
# deleted only if its exact content is a blob in this repository's history,
# i.e. an unmodified framework file git can always restore. Every other such
# file, tracked or not, is project content: it is relocated to ai-local/,
# never deleted. Classification errs toward relocation.

LOCAL_DIR="ai-local"
LOCAL_ROOT="${PROJECT_ROOT}/${LOCAL_DIR}"
STAMP="$(date +%Y%m%d-%H%M%S)"

is_framework_blob() {
    local h
    [[ -f "$1" && ! -L "$1" ]] || return 1
    h="$(git hash-object --no-filters -- "$1" 2>/dev/null)" || return 1
    [[ -n "${h}" ]] && git -C "${REPO_ROOT}" cat-file -e "${h}" 2>/dev/null
}

DELETE_LIST=""
RELOCATE_LIST=""
while IFS= read -r rel; do
    [[ -z "${rel}" ]] && continue
    if is_framework_blob "${PROJECT_AI}/${rel}"; then
        DELETE_LIST+="${rel}"$'\n'
    else
        RELOCATE_LIST+="${rel}"$'\n'
    fi
done < <(
    rsync --dry-run -a --delete --itemize-changes "${EXCLUDES[@]}" \
        "${AI_SRC}/" "${PROJECT_AI}/" \
    | sed -n 's/^\*deleting  *//p' \
    | while IFS= read -r d; do
        if [[ -d "${PROJECT_AI}/${d%/}" && ! -L "${PROJECT_AI}/${d%/}" ]]; then
            (cd "${PROJECT_AI}" && find "${d%/}" \( -type f -o -type l \))
        else
            echo "${d}"
        fi
    done | sort -u
)

# --- Preview ---------------------------------------------------------------
# --itemize-changes lines beginning with '>f' indicate files that would
# actually be transferred. Directories and unchanged files are excluded.

echo "=== Preview: ai -> ${PROJECT_AI} ==="
echo ""

# context.md is excluded from the transfer, so it is invisible to CHANGES. A
# target differing from the source only by a missing context.md therefore
# reported "up to date" and exited before reaching the seeding pass below —
# making that pass unreachable in precisely the case it exists to serve, the
# new project. The seed condition is evaluated here, before the early exit,
# and admitted as work to be done.

if [[ -f "${PROJECT_AI}/context.md" ]]; then
    NEEDS_SEED_CONTEXT="false"
else
    NEEDS_SEED_CONTEXT="true"
fi

if [[ -f "${PROJECT_AI}/task.md" ]]; then
    NEEDS_SEED_TASK="false"
else
    NEEDS_SEED_TASK="true"
fi

# '*deleting' lines are files removed from the target by --delete.
CHANGES=$(rsync --dry-run -av --itemize-changes "${EXCLUDES[@]}" \
    "${AI_SRC}/" "${PROJECT_AI}/" | grep '^>f' || true)

if [[ -z "${CHANGES}" && -z "${DELETE_LIST}" && -z "${RELOCATE_LIST}" \
      && "${NEEDS_SEED_CONTEXT}" == "false" && "${NEEDS_SEED_TASK}" == "false" ]]; then
    echo "Target is up to date. No changes to apply."
    exit 0
fi

if [[ -n "${CHANGES}" ]]; then
    echo "${CHANGES}"
else
    echo "(no framework files differ)"
fi

while IFS= read -r rel; do
    [[ -n "${rel}" ]] && echo "delete       ${rel} (unmodified framework file)"
done <<< "${DELETE_LIST}"

while IFS= read -r rel; do
    [[ -n "${rel}" ]] && echo "relocate     ${rel} -> ${LOCAL_DIR}/${rel} (project content)"
done <<< "${RELOCATE_LIST}"

if [[ "${NEEDS_SEED_CONTEXT}" == "true" ]]; then
    echo "seed         context.md (absent in target)"
fi

if [[ "${NEEDS_SEED_TASK}" == "true" ]]; then
    echo "seed         task.md (absent in target)"
fi

echo ""
echo "governance: source ${SRC_VER:-unknown}, target ${DST_VER:-unknown}"
if [[ "${MAJOR_CHANGE}" == "true" ]]; then
    echo "WARNING: major governance version change (${DST_VER} -> ${SRC_VER})."
    echo "         Renamed or retired files will be deleted from the target."
fi
echo ""

# --- Confirmation ----------------------------------------------------------

if [[ "${ASSUME_YES}" == "true" ]]; then
    if [[ "${MAJOR_CHANGE}" == "true" && "${ALLOW_MAJOR}" != "true" ]]; then
        echo "Error: major version change requires --allow-major with --yes. Nothing applied." >&2
        exit 2
    fi
    echo "--yes: applying without prompt."
elif [[ ! -t 0 ]]; then
    echo "Error: stdin is not a terminal; re-run with --yes to apply. Nothing applied." >&2
    exit 2
else
    read -r -p "Apply changes? [y/N] " CONFIRM
    if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# --- Relocate --------------------------------------------------------------
# Runs before the rsync apply, so --delete below only ever removes files
# classified as unmodified framework files. Never overwrites: an existing
# destination gets a timestamp suffix. Logged in ai-local/RELOCATED.md.

if [[ -n "${RELOCATE_LIST}" ]]; then
    LOG="${LOCAL_ROOT}/RELOCATED.md"
    mkdir -p "${LOCAL_ROOT}"
    if [[ ! -f "${LOG}" ]]; then
        {
            echo "# Relocated from ai/"
            echo ""
            echo "Project files moved out of ai/ by LLM-G&O bin/propagate.sh (governance P10.6)."
            echo "Their content did not match any framework file. Review, then keep, move or delete."
            echo ""
            echo "| Date | From | To | Note |"
            echo "|---|---|---|---|"
        } > "${LOG}"
    fi
    IN_GIT="false"
    git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1 && IN_GIT="true"
    while IFS= read -r rel; do
        [[ -z "${rel}" ]] && continue
        src="${PROJECT_AI}/${rel}"
        dst_rel="${rel}"
        [[ -e "${LOCAL_ROOT}/${dst_rel}" || -L "${LOCAL_ROOT}/${dst_rel}" ]] && dst_rel="${rel}.relocated-${STAMP}"
        was_ignored="false"
        [[ "${IN_GIT}" == "true" ]] && git -C "${PROJECT_ROOT}" check-ignore -q "ai/${rel}" && was_ignored="true"
        mkdir -p "$(dirname "${LOCAL_ROOT}/${dst_rel}")"
        mv -n "${src}" "${LOCAL_ROOT}/${dst_rel}"
        if [[ -e "${src}" || -L "${src}" ]]; then
            echo "Error: could not relocate ai/${rel}. Nothing further applied." >&2
            exit 3
        fi
        note=""
        if [[ "${was_ignored}" == "true" ]] \
           && ! git -C "${PROJECT_ROOT}" check-ignore -q "${LOCAL_DIR}/${dst_rel}"; then
            note="WAS GITIGNORED, NOW NOT - check before committing"
            echo "WARNING: ${LOCAL_DIR}/${dst_rel} was gitignored in ai/ and is not ignored now."
        fi
        echo "| $(date +%Y-%m-%d) | ai/${rel} | ${LOCAL_DIR}/${dst_rel} | ${note} |" >> "${LOG}"
        echo "relocated    ai/${rel} -> ${LOCAL_DIR}/${dst_rel}"
    done <<< "${RELOCATE_LIST}"
    echo ""
fi

# --- Propagate -------------------------------------------------------------

rsync -av --delete "${EXCLUDES[@]}" \
    "${AI_SRC}/" "${PROJECT_AI}/"

# --- Seed project-specific context ----------------------------------------
# context.md is excluded from the transfer above so an existing downstream copy
# is never overwritten. New projects still need the template, so seed it here.
# NEEDS_SEED was evaluated before the preview's early exit; --ignore-existing is
# not used, as the absence of the file is already established by that test.

if [[ "${NEEDS_SEED_CONTEXT}" == "true" ]]; then
    rsync -a "${AI_SRC}/context.md" "${PROJECT_AI}/"
    echo ""
    echo "context.md: template seeded (new project). Fill it in before the first AEL run."
else
    echo ""
    echo "context.md: existing project copy preserved."
fi

if [[ "${NEEDS_SEED_TASK}" == "true" ]]; then
    rsync -a "${AI_SRC}/task.md" "${PROJECT_AI}/"
    echo ""
    echo "task.md: template seeded (new project)."
else
    echo ""
    echo "task.md: existing project copy preserved."
fi

echo ""
if [[ -n "${RELOCATE_LIST}" ]]; then
    echo ""
    echo "${LOCAL_DIR}/: project files relocated from ai/; see ${LOCAL_DIR}/RELOCATED.md."
fi
echo ""
echo "Done. Review changes and commit manually."
