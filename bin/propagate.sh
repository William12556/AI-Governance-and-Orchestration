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
#                  a major version, or the target version is unknown
#                  (required with --yes in that case)
#
# Behaviour (change-c5270084 iteration 3; governance P10.6):
#   - Copies ai/ into <project-root>/ai/ with rsync, WITHOUT --delete.
#     This script never deletes a file.
#   - Declared project paths (see Excludes) are never touched.
#   - Every other target file absent from the source, or whose type differs
#     from the source, is moved to <project-root>/ai-local/ before the copy and
#     logged in ai-local/RELOCATED.md, labelled either 'retired framework file'
#     (content matches framework history at that path; safe to delete) or
#     'project content'. Review ai-local/ and delete what is not needed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AI_SRC="${REPO_ROOT}/ai"

# --- Arguments ---------------------------------------------------------------

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
LOCAL_DIR="ai-local"
LOCAL_ROOT="${PROJECT_ROOT}/${LOCAL_DIR}"

if [[ ! -d "${AI_SRC}" ]]; then
    echo "Error: ai/ not found at ${AI_SRC}" >&2
    exit 1
fi

if [[ ! -d "${PROJECT_AI}" ]]; then
    echo "Error: target ai/ directory not found at ${PROJECT_AI}" >&2
    exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

# --- Governance version ------------------------------------------------------
# Last row of the governance.md Version History table. An absent file or an
# unparseable table yields "unknown", which is treated like a major change:
# never a silent exit (audit F-03).

gov_version() {
    local v=""
    if [[ -f "$1" ]]; then
        v="$(grep -E '^\| *[0-9]+\.[0-9]+(\.[0-9]+)? *\|' "$1" 2>/dev/null | tail -1 \
            | sed -E 's/^\| *([0-9]+\.[0-9]+(\.[0-9]+)?).*/\1/' || true)"
    fi
    echo "${v:-unknown}"
}

SRC_VER="$(gov_version "${AI_SRC}/governance.md")"
DST_VER="$(gov_version "${PROJECT_AI}/governance.md")"
MAJOR_CHANGE="false"
if [[ "${SRC_VER}" == "unknown" || "${DST_VER}" == "unknown" \
      || "${SRC_VER%%.*}" != "${DST_VER%%.*}" ]]; then
    MAJOR_CHANGE="true"
fi

# --- Excludes ----------------------------------------------------------------
# Declared project paths (governance P10.6), anchored at ai/. No trailing
# slash, so a symlink at a declared path is protected too (audit F-06).

EXCLUDES=(
    --exclude='/ael/config.yaml'     # project-specific AEL configuration
    --exclude='/context.md'          # project conventions/stack; seeded when absent
    --exclude='/task.md'             # open-work register; seeded when absent
    --exclude='/workspace'           # project governance documents
    --exclude='/state'               # AEL runtime state
    --exclude='/logs'                # AEL run-log archive (log_archive_dir)
    --exclude='/dashboard-alerts.md' # govwatch write target
    --exclude='.DS_Store'
    --exclude='__pycache__'
    --exclude='*.pyc'
    --exclude='*.pyo'
)

is_declared() {
    case "$1" in
        ael/config.yaml|context.md|task.md|dashboard-alerts.md) return 0 ;;
        workspace|workspace/*|state|state/*|logs|logs/*) return 0 ;;
        .DS_Store|*/.DS_Store|__pycache__|__pycache__/*|*/__pycache__|*/__pycache__/*) return 0 ;;
        *.pyc|*.pyo) return 0 ;;
    esac
    return 1
}

# --- Enumerate ---------------------------------------------------------------
# Target entries (files and symlinks) are compared with the source directly,
# NUL-delimited, independent of rsync output (audit F-01, F-07). An entry is a
# candidate when the source has nothing of the same type at that path.

same_type() {
    local s="${AI_SRC}/$1" t="${PROJECT_AI}/$1"
    if [[ -L "${t}" ]]; then [[ -L "${s}" ]]; return; fi
    [[ -L "${s}" ]] && return 1
    [[ -f "${t}" && -f "${s}" ]]
}

CAND="${WORK}/candidates"
: > "${CAND}"
while IFS= read -r -d '' p; do
    rel="${p#./}"
    is_declared "${rel}" && continue
    same_type "${rel}" && continue
    printf '%s\0' "${rel}" >> "${CAND}"
done < <(cd "${PROJECT_AI}" && find . -mindepth 1 \( -type f -o -type l \) -print0)
CAND_COUNT="$(tr -cd '\0' < "${CAND}" | wc -c | tr -d ' ')"

# --- Label -------------------------------------------------------------------
# Label only; nothing is deleted on its strength. 'retired framework file'
# means the content is a non-empty blob committed at the same path under ai/
# (or the historic framework/ai/, skel/ai/) in history reachable from the
# framework's refs (audit F-02).

BLOBS="${WORK}/blobs"
git -C "${REPO_ROOT}" log --all --format= --raw --no-abbrev --no-renames \
    -- ai framework/ai skel/ai 2>/dev/null \
  | awk -F'\t' '{ split($1, m, " "); p = $2; sub(/^(framework|skel)\//, "", p); sub(/^ai\//, "", p);
                   if (m[4] !~ /^0+$/) print m[4] " " p }' \
  | sort -u > "${BLOBS}" || true
EMPTY_BLOB="e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
SHALLOW="$(git -C "${REPO_ROOT}" rev-parse --is-shallow-repository 2>/dev/null || echo false)"

label_of() {
    local f="${PROJECT_AI}/$1" h
    [[ -f "${f}" && ! -L "${f}" ]] || { echo "project content"; return; }
    h="$(git hash-object --no-filters -- "${f}" 2>/dev/null || true)"
    if [[ -n "${h}" && "${h}" != "${EMPTY_BLOB}" ]] && grep -Fxq -- "${h} $1" "${BLOBS}"; then
        echo "retired framework file"
    else
        echo "project content"
    fi
}

# --- Plan relocations --------------------------------------------------------
# Destinations are fixed and checked before the first move (audit F-01, F-10):
# ai-local/ and every existing component of a destination's directory must be a
# real directory, never a symlink or a file. Existing files are never
# overwritten; a timestamp suffix is used instead.

STAMP="$(date +%Y%m%d-%H%M%S)"
PLAN="${WORK}/plan"
: > "${PLAN}"
PLAN_ERR=""

check_dir_chain() {
    local d="$1" cur="${LOCAL_ROOT}" part rest
    if [[ -L "${cur}" || ( -e "${cur}" && ! -d "${cur}" ) ]]; then return 1; fi
    rest="${d}"
    while [[ -n "${rest}" && "${rest}" != "." ]]; do
        part="${rest%%/*}"
        if [[ "${rest}" == */* ]]; then rest="${rest#*/}"; else rest=""; fi
        cur="${cur}/${part}"
        if [[ -L "${cur}" || ( -e "${cur}" && ! -d "${cur}" ) ]]; then return 1; fi
    done
    return 0
}

if [[ "${CAND_COUNT}" -gt 0 ]]; then
    while IFS= read -r -d '' rel; do
        dst="${rel}"
        if [[ -e "${LOCAL_ROOT}/${dst}" || -L "${LOCAL_ROOT}/${dst}" ]]; then
            dst="${rel}.relocated-${STAMP}"
        fi
        ddir="$(dirname "${dst}")"
        if ! check_dir_chain "${ddir}"; then
            PLAN_ERR+="  ${LOCAL_DIR}/${dst}: a path component is a file or symlink"$'\n'
        fi
        ign="false"
        if git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
           && git -C "${PROJECT_ROOT}" check-ignore -q -- "ai/${rel}" 2>/dev/null; then
            ign="true"
        fi
        printf '%s\0%s\0%s\0%s\0' "${rel}" "${dst}" "$(label_of "${rel}")" "${ign}" >> "${PLAN}"
    done < "${CAND}"
fi

# --- Preview -----------------------------------------------------------------

NEEDS_SEED_CONTEXT="false"; [[ -f "${PROJECT_AI}/context.md" ]] || NEEDS_SEED_CONTEXT="true"
NEEDS_SEED_TASK="false";    [[ -f "${PROJECT_AI}/task.md" ]]    || NEEDS_SEED_TASK="true"

echo "=== Preview: ai -> ${PROJECT_AI} ==="
echo ""

CHANGES=$(rsync --dry-run -a --itemize-changes "${EXCLUDES[@]}" \
    "${AI_SRC}/" "${PROJECT_AI}/" | grep -E '^[<>c]f' || true)

if [[ -z "${CHANGES}" && "${CAND_COUNT}" -eq 0 \
      && "${NEEDS_SEED_CONTEXT}" == "false" && "${NEEDS_SEED_TASK}" == "false" ]]; then
    echo "Target is up to date. No changes to apply."
    exit 0
fi

if [[ -n "${CHANGES}" ]]; then echo "${CHANGES}"; else echo "(no framework files differ)"; fi

RELOC_GITIGNORE="false"
if [[ "${CAND_COUNT}" -gt 0 ]]; then
    while IFS= read -r -d '' rel && IFS= read -r -d '' dst && IFS= read -r -d '' lab && IFS= read -r -d '' ign; do
        echo "relocate     ${rel} -> ${LOCAL_DIR}/${dst} (${lab})"
        [[ "$(basename "${rel}")" == ".gitignore" ]] && RELOC_GITIGNORE="true"
    done < "${PLAN}"
fi
[[ "${NEEDS_SEED_CONTEXT}" == "true" ]] && echo "seed         context.md (absent in target)"
[[ "${NEEDS_SEED_TASK}" == "true" ]] && echo "seed         task.md (absent in target)"

echo ""
echo "governance: source ${SRC_VER}, target ${DST_VER}"
if [[ "${MAJOR_CHANGE}" == "true" ]]; then
    echo "WARNING: major or unknown governance version change (${DST_VER} -> ${SRC_VER})."
    echo "         Renamed or retired files will be relocated to ${LOCAL_DIR}/."
fi
if [[ "${RELOC_GITIGNORE}" == "true" ]]; then
    echo "WARNING: a .gitignore under ai/ will be relocated; files it ignored may become committable."
fi
[[ "${SHALLOW}" == "true" ]] && echo "NOTE: framework clone is shallow; 'retired framework file' labels may be missing."

if [[ -n "${PLAN_ERR}" ]]; then
    echo "" >&2
    echo "Error: cannot relocate safely into ${LOCAL_DIR}/:" >&2
    printf '%s' "${PLAN_ERR}" >&2
    echo "Resolve these paths in ${LOCAL_DIR}/ and re-run. Nothing applied." >&2
    exit 3
fi
echo ""

# --- Confirmation ------------------------------------------------------------

if [[ "${ASSUME_YES}" == "true" ]]; then
    if [[ "${MAJOR_CHANGE}" == "true" && "${ALLOW_MAJOR}" != "true" ]]; then
        echo "Error: major or unknown version change requires --allow-major with --yes. Nothing applied." >&2
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

# --- Relocate ----------------------------------------------------------------
# Runs before the copy. Each move is logged immediately after it succeeds. Any
# failure stops the run before the copy (exit 3); completed moves stay logged.

if [[ "${CAND_COUNT}" -gt 0 ]]; then
    LOG="${LOCAL_ROOT}/RELOCATED.md"
    mkdir -p "${LOCAL_ROOT}" || { echo "Error: cannot create ${LOCAL_ROOT}. Nothing applied." >&2; exit 3; }
    if [[ ! -f "${LOG}" ]]; then
        {
            echo "# Relocated from ai/"
            echo ""
            echo "Files moved out of ai/ by LLM-G&O bin/propagate.sh (governance P10.6)."
            echo "'retired framework file': content matches framework history at that path; safe to delete."
            echo "'project content': review, then keep elsewhere or delete."
            echo ""
            echo "| Date | From | To | Label | Note |"
            echo "|---|---|---|---|---|"
        } > "${LOG}"
    fi
    while IFS= read -r -d '' rel && IFS= read -r -d '' dst && IFS= read -r -d '' lab && IFS= read -r -d '' ign; do
        if ! mkdir -p "$(dirname "${LOCAL_ROOT}/${dst}")" \
           || ! mv -n -- "${PROJECT_AI}/${rel}" "${LOCAL_ROOT}/${dst}" \
           || [[ -e "${PROJECT_AI}/${rel}" || -L "${PROJECT_AI}/${rel}" ]]; then
            echo "Error: could not relocate ai/${rel}. Copy not applied; see ${LOCAL_DIR}/RELOCATED.md." >&2
            exit 3
        fi
        row_rel="${rel//|/\\|}"; row_dst="${dst//|/\\|}"
        echo "| $(date +%Y-%m-%d) | ai/${row_rel} | ${LOCAL_DIR}/${row_dst} | ${lab} | ${ign} |" >> "${LOG}"
        echo "relocated    ai/${rel} -> ${LOCAL_DIR}/${dst}"
    done < "${PLAN}"
    # Gitignore coverage, evaluated after all moves against the pre-move record
    # (audit F-04).
    while IFS= read -r -d '' rel && IFS= read -r -d '' dst && IFS= read -r -d '' lab && IFS= read -r -d '' ign; do
        if [[ "${ign}" == "true" ]] && ! git -C "${PROJECT_ROOT}" check-ignore -q -- "${LOCAL_DIR}/${dst}" 2>/dev/null; then
            echo "WARNING: ${LOCAL_DIR}/${dst} was gitignored in ai/ and is not ignored now. Check before committing."
        fi
    done < "${PLAN}"
    # Directories left empty where the source has a file block the copy; rmdir
    # removes only empty directories.
    while IFS= read -r -d '' d; do
        rel="${d#./}"
        if [[ -e "${AI_SRC}/${rel}" && ! -d "${AI_SRC}/${rel}" ]]; then
            rmdir "${PROJECT_AI}/${rel}" 2>/dev/null || true
        fi
    done < <(cd "${PROJECT_AI}" && find . -mindepth 1 -depth -type d -empty -print0)
    echo ""
fi

# --- Propagate ---------------------------------------------------------------
# No --delete: rsync only adds and updates framework files.

rsync -a -v "${EXCLUDES[@]}" "${AI_SRC}/" "${PROJECT_AI}/"

# --- Seed project-specific files ---------------------------------------------

if [[ "${NEEDS_SEED_CONTEXT}" == "true" ]]; then
    cp "${AI_SRC}/context.md" "${PROJECT_AI}/context.md"
    echo ""
    echo "context.md: template seeded (new project). Fill it in before the first AEL run."
else
    echo ""
    echo "context.md: existing project copy preserved."
fi

if [[ "${NEEDS_SEED_TASK}" == "true" ]]; then
    cp "${AI_SRC}/task.md" "${PROJECT_AI}/task.md"
    echo ""
    echo "task.md: template seeded (new project)."
else
    echo ""
    echo "task.md: existing project copy preserved."
fi

if [[ "${CAND_COUNT}" -gt 0 ]]; then
    echo ""
    echo "${LOCAL_DIR}/: ${CAND_COUNT} file(s) relocated; see ${LOCAL_DIR}/RELOCATED.md."
fi
echo ""
echo "Done. Review changes and commit manually. This script deleted nothing."
