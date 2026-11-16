#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILL_DIR="$HERMES_HOME/skills/nabees-provider-manager"
mkdir -p "$SKILL_DIR"
install -m 0644 "$ROOT/skills/nabees-provider-manager/SKILL.md" "$SKILL_DIR/SKILL.md"
printf 'Installed Nabees provider manager skill to %s\n' "$SKILL_DIR"
printf 'Provider CLI remains in the Wagent repository: %s/scripts/provider_manager.py\n' "$ROOT"
