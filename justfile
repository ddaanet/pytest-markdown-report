# List available recipes
help:
    @just --list --unsorted

# Run test suite
test:
    uv run pytest test_output_expectations.py -v

# Create release: tag, build tarball, upload to PyPI and GitHub
release bump='patch': _fail_if_claudecode test
    #!/usr/bin/env bash -euo pipefail
    {{ _bash-defs }}
    git diff --quiet HEAD || fail "Error: uncommitted changes"
    release=$(version --bump {{ bump }} --dry-run)
    while read -re -p "Release $release? [y/n] " answer; do
        case "$answer" in
            y|Y) break;;
            n|N) exit 1;;
            *) continue;;
        esac
    done
    visible uv version --bump {{ bump }}
    version=$(uv version)
    git add pyproject.toml uv.lock
    visible git commit -m "🔖 Release $version"
    visible git push
    tag="v$(uv version --short)"
    git rev-parse "$tag" >/dev/null 2>&1 && fail "Error: tag $tag already exists"
    visible git tag -a "$tag" -m "Release $version"
    visible git push origin "$tag"
    visible uv build
    visible uv publish
    visible gh release create "$tag" --title "$version" \
        --generate-notes
    echo "${GREEN}Release $tag complete${NORMAL}"

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

