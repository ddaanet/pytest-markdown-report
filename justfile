# Justfile Rules:
# - Errors should not pass silently without good reason
# - Only use `2>/dev/null` for probing (checking exit status when command has no quiet option)
# - Only use `|| true` to continue after expected failures (required with `set -e`)

# List available recipes
help:
    @just --list --unsorted

# Full development workflow
[no-exit-message]
dev: format check test

# Run test suite
[no-exit-message]
test *ARGS:
    uv run pytest tests/test_output_expectations.py {{ ARGS }}

# Format, check with complexity disabled, test
[no-exit-message]
lint: format
    uv run ruff check -q --ignore=C901
    docformatter -c src tests
    uv run mypy
    uv run pytest tests/test_output_expectations.py

# Check code style
[no-exit-message]
check:
    uv run ruff check -q
    docformatter -c src tests
    uv run mypy

# Format code
format:
    #!/usr/bin/env bash -euo pipefail
    tmpfile=$(mktemp tmp-fmt-XXXXXX)
    trap "rm $tmpfile" EXIT
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    uv run ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    uv run ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff src tests | patch-and-print -RCp1 >> "$tmpfile" || true

    git ls-files | grep '\.md$' | uv run claudeutils markdown >> "$tmpfile"
    dprint -c .dprint.json check --list-different \
    | sed "s|^$(pwd)/||g" >> "$tmpfile" || true
    dprint -c .dprint.json fmt -L warn
    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files:**"
        echo "$modified" | sed "s|^|${bold}${red}  - ${nobold}${resetfg}|"
    fi

# Create release: tag, build tarball, upload to PyPI and GitHub
# Use --dry-run to perform local changes and verify external permissions without publishing
# Use --rollback to revert local changes from a crashed dry-run
release bump='patch' *FLAGS: _fail_if_claudecode test
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    DRY_RUN=false
    ROLLBACK=false
    for flag in {{ FLAGS }}; do
        if [[ "$flag" == "--dry-run" ]]; then
            DRY_RUN=true
        elif [[ "$flag" == "--rollback" ]]; then
            ROLLBACK=true
        fi
    done

    # Cleanup function: revert commit and remove build artifacts
    cleanup_release() {
        local initial_head=$1
        local version=$2
        local silent=${3:-false}

        [[ "$silent" == "false" ]] && echo "Reverting changes..."
        git reset --hard "$initial_head"
        git checkout "$initial_head"

        # Remove only this version's build artifacts
        if [[ -n "$version" ]] && [[ -d dist ]]; then
            find dist -name "*${version}*" -delete
            [[ -d dist ]] && [[ -z "$(ls -A dist)" ]] && rmdir dist
        fi
        [[ "$silent" == "false" ]] && echo "${GREEN}✓${NORMAL} Reverted to $(git rev-parse --short "$initial_head")"
    }

    # Rollback mode
    if [[ "$ROLLBACK" == "true" ]]; then
        # Verify no permanent changes
        if git log @{u}.. --oneline | grep -q "🔖 Release"; then
            fail "Error: release commit pushed to remote"
        fi

        if git log -1 --format=%s | grep -q "🔖 Release"; then
            version=$(git log -1 --format=%s | grep -oP '(?<=Release ).*')
            cleanup_release "HEAD~1" "$version"
            echo "${GREEN}✓${NORMAL} Rollback complete"
        else
            echo "${GREEN}✓${NORMAL} No release commit found"
        fi
        exit 0
    fi

    # Check preconditions
    git diff --quiet HEAD || fail "Error: uncommitted changes"
    release=$(uv version --bump {{ bump }} --dry-run)
    tag="v${release}"
    git rev-parse "$tag" >/dev/null 2>&1 && fail "Error: tag $tag already exists"

    # Interactive confirmation (skip in dry-run)
    if [[ "$DRY_RUN" == "false" ]]; then
        while read -re -p "Release $release? [y/n] " answer; do
            case "$answer" in
                y|Y) break;;
                n|N) exit 1;;
                *) continue;;
            esac
        done
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        INITIAL_HEAD=$(git rev-parse HEAD)
        trap 'cleanup_release "$INITIAL_HEAD" "${version:-}"; exit 1' ERR EXIT
    fi

    # Perform local changes: version bump, commit, build
    visible uv version --bump {{ bump }}
    version=$(uv version)
    git add pyproject.toml uv.lock
    visible git commit -m "🔖 Release $version"
    tag="v$(uv version --short)"
    visible uv build

    if [[ "$DRY_RUN" == "true" ]]; then
        # Verify external permissions
        git push --dry-run || fail "Error: cannot push to git remote"
        uv publish --dry-run dist/* || fail "Error: cannot publish to PyPI"
        gh auth status >/dev/null 2>&1 || fail "Error: not authenticated with GitHub"

        echo ""
        echo "${GREEN}✓${NORMAL} Dry-run complete: $version"
        echo "  ${GREEN}✓${NORMAL} Git push permitted"
        echo "  ${GREEN}✓${NORMAL} PyPI publish permitted"
        echo "  ${GREEN}✓${NORMAL} GitHub release permitted"

        # Normal cleanup
        trap - ERR EXIT
        fail "Error: dry-run aborted"
        cleanup_release "$INITIAL_HEAD" "$version"
        echo ""
        echo "Run: ${COMMAND}just release {{ bump }}${NORMAL}"
        exit 0
    fi

    # Perform external actions
    visible git push
    visible git tag -a "$tag" -m "Release $version"
    visible git push origin "$tag"
    visible uv publish
    visible gh release create "$tag" --title "$version" --generate-notes
    echo "${GREEN}✓${NORMAL} Release $tag complete"

# Bash definitions
[private]
_bash-defs := '''
COMMAND="''' + style('command') + '''"
ERROR="{{ style('error') }}"
GREEN=$'\033[32m'
NORMAL="''' + NORMAL + '''"
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${ERROR}$*${NORMAL}"; exit 1; }
'''

# Fail if CLAUDECODE is set
[no-exit-message]
[private]
_fail_if_claudecode:
    #!/usr/bin/env bash -euo pipefail
    if [ "${CLAUDECODE:-}" != "" ]; then
        echo -e '{{ style("error") }}⛔️ Denied: use agent recipes{{ NORMAL }}'
        exit 1
    fi

