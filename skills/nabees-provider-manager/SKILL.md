---
name: nabees-provider-manager
description: Add, test, activate, list and roll back custom OpenAI-compatible model providers for Nabees Agent.
---

# Nabees provider manager

Use this skill when the owner asks to add an API provider, change a base URL, rotate a key, switch models, test tool-calling compatibility or roll back a provider.

## Secret handling

Do not ask the owner to paste API keys into ordinary WhatsApp messages. Until a secure one-time credential channel exists, ask them to enter keys through the hidden terminal prompt. Never echo, log or repeat keys. Never save secrets in this repository.

## Commands

The installer sets `NABEES_WAGENT_HOME` in Hermes' private environment. Run:

- `python "$NABEES_WAGENT_HOME/scripts/provider_manager.py" list`
- `python "$NABEES_WAGENT_HOME/scripts/provider_manager.py" add` (hidden API-key prompt)
- `python "$NABEES_WAGENT_HOME/scripts/provider_manager.py" test NAME`
- `python "$NABEES_WAGENT_HOME/scripts/provider_manager.py" activate NAME`
- `python "$NABEES_WAGENT_HOME/scripts/provider_manager.py" rollback`

Do not activate a provider until tests pass. A basic chat response does not prove tool calling works. After activation, verify with a fresh Hermes request. If it fails, roll back and explain what failed without exposing credentials.
