#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILL_DIR="$HERMES_HOME/skills/nabees-provider-manager"
mkdir -p "$SKILL_DIR"
install -m 0644 "$ROOT/skills/nabees-provider-manager/SKILL.md" "$SKILL_DIR/SKILL.md"
ENV_FILE="$HERMES_HOME/.env"
touch "$ENV_FILE"
if ! grep -q '^NABEES_WAGENT_HOME=' "$ENV_FILE"; then
  printf '\nNABEES_WAGENT_HOME="%s"\n' "$ROOT" >> "$ENV_FILE"
fi
chmod 600 "$ENV_FILE"
printf 'Installed Nabees provider skill to %s\n' "$SKILL_DIR"
printf 'Provider CLI: %s/scripts/provider_manager.py\n' "$ROOT"
printf 'Restart the Hermes gateway so it loads the new skill and environment variable.\n'
