#!/usr/bin/env bash
# migrate-layout.sh — One-time move of a downstream project's ai/ from the
# pre-5bcd46ad layout to the engine/governance layout (change-5bcd46ad).
#
# Usage:
#   bin/migrate-layout.sh [--apply] <project-root>
#
#   Without --apply the script prints the plan and changes nothing.
#
# Behaviour:
#   - ai/ael/config.yaml moves to ai/config.yaml (project-owned); its
#     loop.state_dir value "ai/state/ralph" is changed to "ai/state", which
#     engine-mcp expects.
#   - Retired framework paths (ai/ael/, ai/governance.md, ai/workflow.md,
#     ai/primer.md, ai/templates/, ai/skills/, ai/doc/, ai/index.md,
#     ai/src/govwatch.py, ai/src/requirements-govwatch.txt) move to
#     ai-local/retired-5bcd46ad/ and are logged in ai-local/RELOCATED.md.
#   - Never deletes, never overwrites (mv -n; every destination checked first).
#   - In a git work tree, refuses uncommitted changes under ai/.
#   - ai/state/ralph/ (runtime state) is left in place and reported.
#   - Then run: bin/propagate.sh --allow-major <project-root>
#
# Exit codes: 0 done, nothing to do, or plan shown; 1 usage; 3 refused.

set -euo pipefail

APPLY="false"
POSITIONAL=()
for arg in "$@"; do
    case "${arg}" in
        --apply) APPLY="true" ;;
        -*)      echo "Error: unknown option ${arg}" >&2; exit 1 ;;
        *)       POSITIONAL+=("${arg}") ;;
    esac
done
if [[ ${#POSITIONAL[@]} -ne 1 ]]; then
    echo "Usage: $0 [--apply] <project-root>" >&2
    exit 1
fi

PROJECT_ROOT="$(cd "${POSITIONAL[0]}" && pwd)"
AI="${PROJECT_ROOT}/ai"
LOCAL="${PROJECT_ROOT}/ai-local"
RETIRED_REL="retired-5bcd46ad"
LOG="${LOCAL}/RELOCATED.md"

if [[ ! -d "${AI}" ]]; then
    echo "Error: ai/ not found at ${AI}" >&2
    exit 1
fi
if [[ ! -e "${AI}/ael" && ! -f "${AI}/governance.md" ]]; then
    echo "Nothing to migrate: ${AI} is not in the pre-5bcd46ad layout."
    exit 0
fi

RETIRED=(ael governance.md workflow.md primer.md templates skills doc index.md
         src/govwatch.py src/requirements-govwatch.txt)

# --- Plan ----------------------------------------------------------------------

ERR=""
STATE_EDIT="false"
MOVES=()   # pairs: source-relative-to-ai  destination-absolute
if [[ -e "${AI}/ael/config.yaml" ]]; then
    if [[ -e "${AI}/config.yaml" || -L "${AI}/config.yaml" ]]; then
        ERR+="  ai/config.yaml already exists; resolve ai/ael/config.yaml manually"$'\n'
    else
        MOVES+=("ael/config.yaml" "${AI}/config.yaml")
        STATE_EDIT="false"
        grep -q 'state_dir: *"ai/state/ralph"' "${AI}/ael/config.yaml" && STATE_EDIT="true"
    fi
fi
for rel in "${RETIRED[@]}"; do
    [[ -e "${AI}/${rel}" || -L "${AI}/${rel}" ]] || continue
    dst="${LOCAL}/${RETIRED_REL}/${rel}"
    if [[ -e "${dst}" || -L "${dst}" ]]; then
        ERR+="  ai-local/${RETIRED_REL}/${rel} already exists"$'\n'
    fi
    MOVES+=("${rel}" "${dst}")
done
if [[ -L "${LOCAL}" || ( -e "${LOCAL}" && ! -d "${LOCAL}" ) ]]; then
    ERR+="  ai-local is not a directory"$'\n'
fi

echo "=== Plan: ${AI} ==="
i=0
while [[ ${i} -lt ${#MOVES[@]} ]]; do
    echo "move   ai/${MOVES[i]} -> ${MOVES[i+1]#"${PROJECT_ROOT}/"}"
    i=$((i + 2))
done
[[ "${STATE_EDIT}" == "true" ]] && echo "edit   ai/config.yaml: loop.state_dir \"ai/state/ralph\" -> \"ai/state\""
[[ -d "${AI}/state/ralph" ]] && echo "note   ai/state/ralph/ is runtime state; left in place. Reset or remove it manually."

echo ""
echo "Old paths referenced outside ai/ (update manually):"
for f in CLAUDE.md AGENTS.md .gitignore .claude/settings.json; do
    [[ -f "${PROJECT_ROOT}/${f}" ]] || continue
    grep -n -E 'ai/ael|ai/(governance|workflow|primer)\.md|ai/templates|ai/state/ralph|ael-mcp|RALPH' \
        "${PROJECT_ROOT}/${f}" 2>/dev/null | sed "s|^|  ${f}:|" || true
done

if [[ -n "${ERR}" ]]; then
    echo "" >&2
    echo "Error: cannot proceed safely:" >&2
    printf '%s' "${ERR}" >&2
    echo "Nothing applied." >&2
    exit 3
fi

if [[ "${APPLY}" != "true" ]]; then
    echo ""
    echo "Dry run. Re-run with --apply to perform the moves."
    exit 0
fi

if git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if [[ -n "$(git -C "${PROJECT_ROOT}" status --porcelain -- ai 2>/dev/null)" ]]; then
        echo "Error: uncommitted changes under ai/. Commit or stash them first. Nothing applied." >&2
        exit 3
    fi
fi

# --- Apply ---------------------------------------------------------------------

mkdir -p "${LOCAL}/${RETIRED_REL}"
if [[ ! -f "${LOG}" ]]; then
    {
        echo "# Relocated from ai/"
        echo ""
        echo "| Date | From | To | Label | Note |"
        echo "|---|---|---|---|---|"
    } > "${LOG}"
fi
i=0
while [[ ${i} -lt ${#MOVES[@]} ]]; do
    src="${AI}/${MOVES[i]}"; dst="${MOVES[i+1]}"
    mkdir -p "$(dirname -- "${dst}")"
    mv -n -- "${src}" "${dst}"
    if [[ -e "${src}" || -L "${src}" ]]; then
        echo "Error: could not move ai/${MOVES[i]}; stopped. Moves so far are logged in ai-local/RELOCATED.md." >&2
        exit 3
    fi
    if [[ "${dst}" == "${LOCAL}/"* ]]; then
        echo "| $(date +%Y-%m-%d) | ai/${MOVES[i]} | ${dst#"${PROJECT_ROOT}/"} | retired framework file | layout migration change-5bcd46ad |" >> "${LOG}"
    fi
    echo "moved  ai/${MOVES[i]}"
    i=$((i + 2))
done

if [[ "${STATE_EDIT}" == "true" ]]; then
    perl -pi -e 's{state_dir:(\s*)"ai/state/ralph"}{state_dir:$1"ai/state"}' "${AI}/config.yaml"
    echo "edited ai/config.yaml: loop.state_dir -> \"ai/state\""
fi

echo ""
echo "Done. Next: bin/propagate.sh --allow-major ${PROJECT_ROOT}"
echo "Then review ai-local/${RETIRED_REL}/ and commit. This script deleted nothing."
