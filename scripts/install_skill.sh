#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ -z "$HERMES_HOME" ]; then HERMES_HOME="$HOME/.hermes"; fi

install_skill() {
  local name="$1"
  local source="$2"
  local target="$HERMES_HOME/skills/$name"
  mkdir -p "$target"
  install -m 0644 "$source" "$target/SKILL.md"
}

install_skill "nabees-provider-manager" "$ROOT/skills/nabees-provider-manager/SKILL.md"
install_skill "nabees-progress-stickers" "$ROOT/skills/nabees-progress-stickers/SKILL.md"

ENV_FILE="$HERMES_HOME/.env"
touch "$ENV_FILE"
if grep -q '^NABEES_WAGENT_HOME=' "$ENV_FILE"; then
  sed -i "s|^NABEES_WAGENT_HOME=.*|NABEES_WAGENT_HOME=\"$ROOT\"|" "$ENV_FILE"
else
  printf '\nNABEES_WAGENT_HOME="%s"\n' "$ROOT" >> "$ENV_FILE"
fi
chmod 600 "$ENV_FILE"
printf 'Installed Nabees skills and registered Wagent at %s\n' "$ROOT"
