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
# Behaviour (governance P10.6; change-c5270084, change-b170cf6a iteration 2):
#   - Never deletes a file. rsync copies ai/ into <project-root>/ai/ without
#     --delete. Declared project paths (see Excludes) are never touched.
#   - Every other target entry absent from the source, or of a different type,
#     is moved to <project-root>/ai-local/ before the copy.
#   - A target file at a framework path whose content was edited locally is
#     copied to ai-local/ before the copy overwrites it.
#   - ai-local/RELOCATED.md logs every move and copy, labelled 'retired
#     framework file' (safe to delete), 'project content' or 'local
#     modification'. Review ai-local/ and delete what is not needed.
#
# Exit codes: 0 done or up to date; 1 usage; 2 confirmation required;
#   3 refused before the copy (unsafe ai-local/ or declared path, target or
#   ai-local/ changed during the prompt or could not be snapshotted,
#   enumeration or relocation failed);
#   4 the copy failed after relocation.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname -- "$0")/.." && pwd)"
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
LOG_NAME="RELOCATED.md"

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

# Display a path with control characters replaced (N-08).
disp() { printf '%s' "${1//[[:cntrl:]]/?}"; }

# --- Governance version ------------------------------------------------------
# Absent file or unparseable table -> "unknown", treated like a major change.

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
# slash, so a symlink at a declared path is protected too. A symlink at
# context.md or task.md with no regular file behind it is refused, because
# seeding would follow it.

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
    esac
    return 1
}

is_dropping() {
    case "$1" in
        .DS_Store|*/.DS_Store|__pycache__|__pycache__/*|*/__pycache__|*/__pycache__/*) return 0 ;;
        *.pyc|*.pyo) return 0 ;;
    esac
    return 1
}

# Declared files that live below a non-declared directory (N-07).
DECLARED_NESTED=("ael/config.yaml")

# --- Exact names -------------------------------------------------------------
# A path exists in a tree only if every component matches a directory entry
# byte for byte, so case-insensitive file systems cannot equate Primer.md with
# primer.md (N-02).

exact_exists() {
    local dir="$1" rest="$2" part e found
    while :; do
        part="${rest%%/*}"
        found="false"
        for e in "${dir}"/* "${dir}"/.[!.]* "${dir}"/..?*; do
            [[ -e "${e}" || -L "${e}" ]] || continue
            if [[ "${e##*/}" == "${part}" ]]; then found="true"; break; fi
        done
        [[ "${found}" == "true" ]] || return 1
        dir="${dir}/${part}"
        [[ "${rest}" == */* ]] || return 0
        rest="${rest#*/}"
    done
}

same_type() {
    local s="${AI_SRC}/$1" t="${PROJECT_AI}/$1"
    exact_exists "${AI_SRC}" "$1" || return 1
    if [[ -L "${t}" ]]; then [[ -L "${s}" ]]; return; fi
    [[ -L "${s}" ]] && return 1
    [[ -f "${t}" && -f "${s}" ]]
}

# True if an ancestor of $1 is a non-directory in the source (type conflict).
ancestor_conflict() {
    local rel="$1" pre=""
    while [[ "${rel}" == */* ]]; do
        pre="${pre:+${pre}/}${rel%%/*}"
        rel="${rel#*/}"
        if exact_exists "${AI_SRC}" "${pre}" && [[ ! -d "${AI_SRC}/${pre}" || -L "${AI_SRC}/${pre}" ]]; then
            return 0
        fi
    done
    return 1
}

# --- Labels ------------------------------------------------------------------
# 'retired framework file': non-empty blob committed at the same path under
# ai/ (or historic framework/ai/, skel/ai/) in the history of the framework's
# checked-out HEAD only — not other branches, tags or stashes (N-06; A5).

BLOBS="${WORK}/blobs"
git -C "${REPO_ROOT}" log HEAD --format= --raw --no-abbrev --no-renames \
    -- ai framework/ai skel/ai 2>/dev/null \
  | awk -F'\t' '{ split($1, m, " "); p = $2; sub(/^(framework|skel)\//, "", p); sub(/^ai\//, "", p);
                   if (m[4] !~ /^0+$/) print m[4] " " p }' \
  | sort -u > "${BLOBS}" || true
EMPTY_BLOB="e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
SHALLOW="$(git -C "${REPO_ROOT}" rev-parse --is-shallow-repository 2>/dev/null || echo false)"

is_framework_version() {
    local f="${PROJECT_AI}/$1" h
    [[ -f "${f}" && ! -L "${f}" ]] || return 1
    h="$(git hash-object --no-filters -- "${f}" 2>/dev/null || true)"
    [[ -n "${h}" && "${h}" != "${EMPTY_BLOB}" ]] && grep -Fxq -- "${h} $1" "${BLOBS}"
}

# --- Enumeration -------------------------------------------------------------
# find runs to a file and its exit status is checked; any enumeration error
# stops the run before any change (audit-b170cf6a A2). Declared directories
# are pruned, so their contents are never read.

list0() {
    # $1 directory, $2 output file, $3 find type test ("! -type d" or "-type d")
    local err="${WORK}/find.err"
    if ! (cd "$1" && find . -mindepth 1 \( -path ./workspace -o -path ./state -o -path ./logs \) -prune \
            -o $3 -print0) > "$2" 2> "${err}"; then
        echo "Error: cannot list $(disp "$1"):" >&2
        sed 's/^/  /' "${err}" >&2
        echo "Fix permissions and re-run. Nothing applied." >&2
        exit 3
    fi
}

# --- Plan --------------------------------------------------------------------
# Writes NUL-delimited lists into directory $1:
#   cands    target entries to relocate (absent from source or other type)
#   backups  target files at framework paths edited locally (N-01)
#   updates  "add|update" <NUL> path, for the preview (N-03: computed here,
#            not parsed from rsync output)

plan() {
    local out="$1" p rel s t
    : > "${out}/cands"; : > "${out}/backups"; : > "${out}/updates"
    list0 "${PROJECT_AI}" "${out}/tgt.list" "! -type d"
    list0 "${AI_SRC}" "${out}/src.list" "! -type d"
    while IFS= read -r -d '' p; do
        rel="${p#./}"
        is_declared "${rel}" && continue
        if is_dropping "${rel}"; then
            ancestor_conflict "${rel}" || continue
            printf '%s\0' "${rel}" >> "${out}/cands"; continue
        fi
        if ! same_type "${rel}"; then
            printf '%s\0' "${rel}" >> "${out}/cands"; continue
        fi
        if [[ -f "${PROJECT_AI}/${rel}" && ! -L "${PROJECT_AI}/${rel}" ]] \
           && ! cmp -s -- "${AI_SRC}/${rel}" "${PROJECT_AI}/${rel}" \
           && ! is_framework_version "${rel}"; then
            printf '%s\0' "${rel}" >> "${out}/backups"
        fi
    done < "${out}/tgt.list"
    while IFS= read -r -d '' p; do
        rel="${p#./}"
        is_declared "${rel}" && continue
        is_dropping "${rel}" && continue
        s="${AI_SRC}/${rel}"; t="${PROJECT_AI}/${rel}"
        if ! exact_exists "${PROJECT_AI}" "${rel}" 2>/dev/null; then
            printf 'add\0%s\0' "${rel}" >> "${out}/updates"
        elif [[ -L "${s}" ]]; then
            [[ -L "${t}" && "$(readlink -- "${s}")" == "$(readlink -- "${t}")" ]] \
                || printf 'update\0%s\0' "${rel}" >> "${out}/updates"
        elif [[ ! -f "${t}" || -L "${t}" ]] || ! cmp -s -- "${s}" "${t}"; then
            printf 'update\0%s\0' "${rel}" >> "${out}/updates"
        fi
    done < "${out}/src.list"
}

# Snapshot of ai/ (declared paths included) and ai-local/: every name, symlink
# target and regular-file checksum. Taken before plan and compared after the
# prompt, so any change there refuses the run (audit-b170cf6a A1, A3, A4, B2).
# A symlinked ai/ is recorded and followed, as every other step follows it
# (B1); a symlinked ai-local/ is recorded only (refused by check_dir_chain).
# Any failure returns non-zero; the caller exits 3 (B3).
SNAP_FILE="${WORK}/snapshot"
snapshot() {
    local d l
    : > "${SNAP_FILE}" || return 1
    for d in "${PROJECT_AI}" "${LOCAL_ROOT}"; do
        printf '== %s\n' "${d}" >> "${SNAP_FILE}" || return 1
        if [[ -L "${d}" ]]; then
            l="$(readlink -- "${d}")" || return 1
            printf 'link %s\n' "${l}" >> "${SNAP_FILE}" || return 1
            [[ "${d}" == "${PROJECT_AI}" ]] || continue
        fi
        if [[ ! -d "${d}" ]]; then
            if [[ -e "${d}" ]]; then
                { printf 'file '; cksum < "${d}"; } >> "${SNAP_FILE}" || return 1
            else
                printf 'absent\n' >> "${SNAP_FILE}" || return 1
            fi
            continue
        fi
        ( cd "${d}" \
          && find . -print0 | LC_ALL=C sort -z \
          && printf 'L\0' \
          && find . -type l -print0 -exec readlink {} \; \
          && printf 'F\0' \
          && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 cksum ) >> "${SNAP_FILE}" || return 1
    done
    cksum < "${SNAP_FILE}"
}
snapshot_failed() {
    echo "Error: cannot snapshot ai/ or ${LOCAL_DIR}/ for the prompt guard. Nothing applied; fix and re-run." >&2
    exit 3
}
count0() { tr -cd '\0' < "$1" | wc -c | tr -d ' '; }

# Interactive baseline before plan, so no edit can enter it after planning (B2).
INTERACTIVE="false"
if [[ "${ASSUME_YES}" != "true" && -t 0 ]]; then
    INTERACTIVE="true"
    SNAP_BEFORE="$(snapshot)" && [[ -n "${SNAP_BEFORE}" ]] || snapshot_failed
fi

mkdir -p "${WORK}/p1"
plan "${WORK}/p1"
CAND_COUNT="$(count0 "${WORK}/p1/cands")"
BACKUP_COUNT="$(count0 "${WORK}/p1/backups")"
UPDATE_COUNT="$(( $(count0 "${WORK}/p1/updates") / 2 ))"

# --- Destinations ------------------------------------------------------------
# Fixed before the first change. Never overwrite; reserve the log file name;
# suffix with timestamp and index until free (N-05). ai-local/ and every
# existing component of a destination directory must be a real directory.

STAMP="$(date +%Y%m%d-%H%M%S)"
PLAN_ERR=""
IDX=0

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

dest_for() {
    local rel="$1" dst="$1" n=0
    IDX=$((IDX + 1))
    while [[ "${dst}" == "${LOG_NAME}" || -e "${LOCAL_ROOT}/${dst}" || -L "${LOCAL_ROOT}/${dst}" ]]; do
        n=$((n + 1))
        dst="${rel}.relocated-${STAMP}-${IDX}-${n}"
    done
    printf '%s' "${dst}"
}

IN_GIT="false"
git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1 && IN_GIT="true"

# Record format: kind, rel, dst, label, ignored, note (all NUL-terminated).
RECS="${WORK}/recs"
: > "${RECS}"
add_rec() {
    local kind="$1" rel="$2" lab="$3" dst ign="false" note="" d lc
    dst="$(dest_for "${rel}")"
    if ! check_dir_chain "$(dirname -- "${dst}")"; then
        PLAN_ERR+="  $(disp "${LOCAL_DIR}/${dst}"): a path component is a file or symlink"$'\n'
    fi
    for d in "${DECLARED_NESTED[@]}"; do
        if [[ "${d}" == "${rel}/"* ]]; then
            PLAN_ERR+="  ai/$(disp "${rel}"): holds declared ${d}; resolve manually"$'\n'
        fi
    done
    lc="$(printf '%s' "${rel}" | tr '[:upper:]' '[:lower:]')"
    if is_declared "${lc}" || [[ "${lc}" == "ael" ]]; then
        PLAN_ERR+="  ai/$(disp "${rel}"): differs from a declared path only by letter case; rename manually"$'\n'
    fi
    if [[ "${IN_GIT}" == "true" ]] && git -C "${PROJECT_ROOT}" check-ignore -q -- "ai/${rel}" 2>/dev/null; then
        ign="true"
    fi
    if [[ -L "${PROJECT_AI}/${rel}" && "$(readlink -- "${PROJECT_AI}/${rel}")" != /* ]]; then
        note="relative symlink; target may resolve differently"
    fi
    printf '%s\0%s\0%s\0%s\0%s\0%s\0' "${kind}" "${rel}" "${dst}" "${lab}" "${ign}" "${note}" >> "${RECS}"
}

while IFS= read -r -d '' rel; do
    if is_framework_version "${rel}"; then add_rec move "${rel}" "retired framework file"
    else add_rec move "${rel}" "project content"; fi
done < "${WORK}/p1/cands"
while IFS= read -r -d '' rel; do
    add_rec copy "${rel}" "local modification"
done < "${WORK}/p1/backups"

LOG="${LOCAL_ROOT}/${LOG_NAME}"
for f in context.md task.md; do
    # A symlink to an existing regular file is preserved; any other symlink
    # would be followed by seeding (audit-b170cf6a A6, B4).
    if [[ -L "${PROJECT_AI}/${f}" && ! -f "${PROJECT_AI}/${f}" ]]; then
        PLAN_ERR+="  ai/${f}: is a symlink with no regular file behind it; seeding would follow it; resolve manually"$'\n'
    fi
done
if [[ -e "${LOG}" || -L "${LOG}" ]] && [[ ! -f "${LOG}" || -L "${LOG}" ]]; then
    PLAN_ERR+="  ${LOCAL_DIR}/${LOG_NAME}: exists but is not a regular file"$'\n'
fi

# --- Preview -----------------------------------------------------------------

NEEDS_SEED_CONTEXT="false"; [[ -f "${PROJECT_AI}/context.md" ]] || NEEDS_SEED_CONTEXT="true"
NEEDS_SEED_TASK="false";    [[ -f "${PROJECT_AI}/task.md" ]]    || NEEDS_SEED_TASK="true"

echo "=== Preview: ai -> ${PROJECT_AI} ==="
echo ""

if [[ "${UPDATE_COUNT}" -eq 0 && "${CAND_COUNT}" -eq 0 && "${BACKUP_COUNT}" -eq 0 \
      && "${NEEDS_SEED_CONTEXT}" == "false" && "${NEEDS_SEED_TASK}" == "false" ]]; then
    echo "Target is up to date. No changes to apply."
    exit 0
fi

while IFS= read -r -d '' kind && IFS= read -r -d '' rel; do
    printf '%-12s %s\n' "${kind}" "$(disp "${rel}")"
done < "${WORK}/p1/updates"
[[ "${UPDATE_COUNT}" -eq 0 ]] && echo "(no framework files differ)"

RELOC_GITIGNORE="false"
while IFS= read -r -d '' kind && IFS= read -r -d '' rel && IFS= read -r -d '' dst \
      && IFS= read -r -d '' lab && IFS= read -r -d '' ign && IFS= read -r -d '' note; do
    if [[ "${kind}" == "move" ]]; then
        echo "relocate     $(disp "${rel}") -> ${LOCAL_DIR}/$(disp "${dst}") (${lab})"
        [[ "${rel##*/}" == ".gitignore" ]] && RELOC_GITIGNORE="true"
    else
        echo "backup       $(disp "${rel}") -> ${LOCAL_DIR}/$(disp "${dst}") (${lab}; then overwritten)"
    fi
done < "${RECS}"
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
    echo "Error: cannot proceed safely:" >&2
    printf '%s' "${PLAN_ERR}" >&2
    echo "Resolve these paths and re-run. Nothing applied." >&2
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
elif [[ "${INTERACTIVE}" != "true" ]]; then
    echo "Error: stdin is not a terminal; re-run with --yes to apply. Nothing applied." >&2
    exit 2
else
    read -r -p "Apply changes? [y/N] " CONFIRM
    if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
        echo "Aborted."
        exit 0
    fi
    # Nothing under ai/ or ai-local/ may change between the baseline and here.
    SNAP_AFTER="$(snapshot)" && [[ -n "${SNAP_AFTER}" ]] || snapshot_failed
    if [[ "${SNAP_AFTER}" != "${SNAP_BEFORE}" ]]; then
        echo "Error: ai/ or ${LOCAL_DIR}/ changed while the prompt was open. Nothing applied; re-run." >&2
        exit 3
    fi
fi

# --- Relocate and back up ----------------------------------------------------
# Before the copy. Each row is logged before its action; a failed action is
# logged as such and stops the run before the copy (exit 3).

if [[ "${CAND_COUNT}" -gt 0 || "${BACKUP_COUNT}" -gt 0 ]]; then
    mkdir -p "${LOCAL_ROOT}" || { echo "Error: cannot create ${LOCAL_ROOT}. Nothing applied." >&2; exit 3; }
    if [[ ! -f "${LOG}" ]]; then
        {
            echo "# Relocated from ai/"
            echo ""
            echo "Files moved or copied out of ai/ by LLM-G&O bin/propagate.sh (governance P10.6)."
            echo "'retired framework file': content matches framework history at that path; safe to delete."
            echo "'project content': review, then keep elsewhere or delete."
            echo "'local modification': an edited framework file, saved before propagation overwrote it."
            echo ""
            echo "| Date | From | To | Label | Note |"
            echo "|---|---|---|---|---|"
        } > "${LOG}"
    fi
    row() { local r="${1//|/\\|}"; r="${r//[[:cntrl:]]/?}"; printf '%s' "${r}"; }
    while IFS= read -r -d '' kind && IFS= read -r -d '' rel && IFS= read -r -d '' dst \
          && IFS= read -r -d '' lab && IFS= read -r -d '' ign && IFS= read -r -d '' note; do
        [[ "${ign}" == "true" ]] && note="${note:+${note}; }was gitignored in ai/"
        echo "| $(date +%Y-%m-%d) | ai/$(row "${rel}") | ${LOCAL_DIR}/$(row "${dst}") | ${lab} | ${note} |" >> "${LOG}"
        ok="true"
        mkdir -p -- "$(dirname -- "${LOCAL_ROOT}/${dst}")" || ok="false"
        if [[ "${ok}" == "true" ]]; then
            if [[ "${kind}" == "move" ]]; then
                mv -n -- "${PROJECT_AI}/${rel}" "${LOCAL_ROOT}/${dst}" || ok="false"
                [[ -e "${PROJECT_AI}/${rel}" || -L "${PROJECT_AI}/${rel}" ]] && ok="false"
            else
                # No-clobber: copy to a fresh temporary name, then mv -n
                # (audit-b170cf6a A3). A file or symlink at the destination
                # makes mv -n decline, which is detected below.
                tmp="$(mktemp "$(dirname -- "${LOCAL_ROOT}/${dst}")/.propagate-tmp.XXXXXX")" || ok="false"
                if [[ "${ok}" == "true" ]]; then
                    cp -p -- "${PROJECT_AI}/${rel}" "${tmp}" || ok="false"
                    [[ "${ok}" == "true" ]] && { mv -n -- "${tmp}" "${LOCAL_ROOT}/${dst}" || ok="false"; }
                    [[ -e "${tmp}" ]] && ok="false"
                    [[ -L "${LOCAL_ROOT}/${dst}" ]] && ok="false"
                    [[ "${ok}" == "true" ]] && { cmp -s -- "${PROJECT_AI}/${rel}" "${LOCAL_ROOT}/${dst}" || ok="false"; }
                fi
            fi
        fi
        if [[ "${ok}" != "true" ]]; then
            echo "| $(date +%Y-%m-%d) | ai/$(row "${rel}") | — | FAILED | action above did not complete |" >> "${LOG}"
            echo "Error: could not ${kind} ai/$(disp "${rel}"). Copy not applied; see ${LOCAL_DIR}/${LOG_NAME}." >&2
            exit 3
        fi
        if [[ "${kind}" == "move" ]]; then
            echo "relocated    ai/$(disp "${rel}") -> ${LOCAL_DIR}/$(disp "${dst}")"
        else
            echo "backed up    ai/$(disp "${rel}") -> ${LOCAL_DIR}/$(disp "${dst}")"
        fi
    done < "${RECS}"
    # Gitignore coverage, checked after all moves against the pre-move record.
    while IFS= read -r -d '' kind && IFS= read -r -d '' rel && IFS= read -r -d '' dst \
          && IFS= read -r -d '' lab && IFS= read -r -d '' ign && IFS= read -r -d '' note; do
        if [[ "${ign}" == "true" ]] && ! git -C "${PROJECT_ROOT}" check-ignore -q -- "${LOCAL_DIR}/${dst}" 2>/dev/null; then
            echo "WARNING: ${LOCAL_DIR}/$(disp "${dst}") was gitignored in ai/ and is not ignored now. Check before committing."
        fi
    done < "${RECS}"
    # Remove only empty directories at or below a path where the source has a file.
    while IFS= read -r -d '' d; do
        rel="${d#./}"
        if ancestor_conflict "${rel}" \
           || { exact_exists "${AI_SRC}" "${rel}" && [[ ! -d "${AI_SRC}/${rel}" ]]; }; then
            rmdir -- "${PROJECT_AI}/${rel}" 2>/dev/null || true
        fi
    done < <(cd "${PROJECT_AI}" && find . -mindepth 1 \( -path ./workspace -o -path ./state -o -path ./logs \) -prune \
                 -o -type d -empty -print0 | LC_ALL=C sort -rz)
    echo ""
fi

# --- Propagate ---------------------------------------------------------------
# No --delete: rsync only adds and updates framework files.

if ! rsync -a -v "${EXCLUDES[@]}" "${AI_SRC}/" "${PROJECT_AI}/"; then
    echo "Error: rsync copy failed. Relocations are complete and logged in ${LOCAL_DIR}/${LOG_NAME}; re-run after resolving." >&2
    exit 4
fi

# --- Seed project-specific files ---------------------------------------------

if [[ "${NEEDS_SEED_CONTEXT}" == "true" ]] && [[ -e "${PROJECT_AI}/context.md" || -L "${PROJECT_AI}/context.md" ]]; then
    echo ""
    echo "context.md: appeared during the run; not seeded, existing file preserved."
elif [[ "${NEEDS_SEED_CONTEXT}" == "true" ]]; then
    cp "${AI_SRC}/context.md" "${PROJECT_AI}/context.md"
    echo ""
    echo "context.md: template seeded (new project). Fill it in before the first AEL run."
else
    echo ""
    echo "context.md: existing project copy preserved."
fi

if [[ "${NEEDS_SEED_TASK}" == "true" ]] && [[ -e "${PROJECT_AI}/task.md" || -L "${PROJECT_AI}/task.md" ]]; then
    echo ""
    echo "task.md: appeared during the run; not seeded, existing file preserved."
elif [[ "${NEEDS_SEED_TASK}" == "true" ]]; then
    cp "${AI_SRC}/task.md" "${PROJECT_AI}/task.md"
    echo ""
    echo "task.md: template seeded (new project)."
else
    echo ""
    echo "task.md: existing project copy preserved."
fi

if [[ "${CAND_COUNT}" -gt 0 || "${BACKUP_COUNT}" -gt 0 ]]; then
    echo ""
    echo "${LOCAL_DIR}/: ${CAND_COUNT} relocated, ${BACKUP_COUNT} backed up; see ${LOCAL_DIR}/${LOG_NAME}."
fi
echo ""
echo "Done. Review changes and commit manually. This script deleted nothing."
