#!/usr/bin/env bash
# conductor installer — one command per harness.
#
#   ./install.sh claude-code             print the two plugin-install commands (official route)
#   ./install.sh claude-code <project>   OR: symlink this checkout as a project skill of <project>
#   ./install.sh codex [AGENTS.md]       idempotently append the worker fragment
#                                        (default target: ./AGENTS.md in the current directory)
#
# The Claude Code plugin route copies this whole repo (doctrine/ + contract/
# travel with the skill). The codex route needs this checkout to stay on disk:
# the fragment + forwarder reference contract/ files by path.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

usage() { sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
[ $# -ge 1 ] || usage

case "$1" in
  claude-code)
    if [ $# -ge 2 ]; then
      proj="$2"
      [ -d "$proj" ] || { echo "ERROR: no such project dir: $proj" >&2; exit 1; }
      mkdir -p "$proj/.claude/skills"
      ln -sfn "$ROOT/adapters/claude-code" "$proj/.claude/skills/orchestration-mode"
      echo "Linked: $proj/.claude/skills/orchestration-mode -> $ROOT/adapters/claude-code"
      echo "Note: symlink mode ties the skill to this checkout; the plugin route below is self-contained."
    else
      cat <<'EOT'
Run these two commands inside Claude Code (official plugin route):

  /plugin marketplace add mileschen1217/conductor
  /plugin install conductor@conductor

The plugin copy carries doctrine/ and contract/ with it; the skill resolves
them via ${CLAUDE_PLUGIN_ROOT}.
EOT
    fi
    ;;
  codex)
    target="${2:-./AGENTS.md}"
    marker_begin="<!-- >>> conductor orchestration-mode worker contract >>> -->"
    marker_end="<!-- <<< conductor orchestration-mode worker contract <<< -->"
    if [ -f "$target" ] && grep -qF "$marker_begin" "$target"; then
      echo "Already installed in $target (marker found) — nothing to do."
      exit 0
    fi
    # fragment's single home is the adapter README; extract its fenced block
    fragment="$(awk '/^## AGENTS.md load fragment/{f=1} f && /^```markdown$/{c=1; next} c && /^```$/{exit} c' "$ROOT/adapters/codex/README.md")"
    [ -n "$fragment" ] || { echo "ERROR: could not extract fragment from $ROOT/adapters/codex/README.md" >&2; exit 1; }
    {
      [ -f "$target" ] && [ -s "$target" ] && echo ""
      echo "$marker_begin"
      echo "$fragment"
      echo "(conductor checkout: $ROOT — result schema: $ROOT/contract/task-result.schema.json; forwarder recipe: $ROOT/adapters/codex/README.md)"
      echo "$marker_end"
    } >> "$target"
    echo "Installed fragment into $target (idempotent; re-run is a no-op)."
    ;;
  *) usage ;;
esac
