# Nabees Agent

**Nabees Agent by Nabees Tech** is a self-hosted WhatsApp-operated assistant built on [Hermes Agent](https://hermes-agent.nousresearch.com/).

The design goal is provider independence: the owner can add API base URLs, API keys and model identifiers, test compatibility, switch models and roll back without tying the agent permanently to one AI vendor.

## Architecture

- Runtime: upstream Hermes Agent (not a fork)
- Messaging: Hermes built-in WhatsApp bridge (Baileys)
- Hosting target: Linux container / Upstash Box
- Identity: Nabees Agent, by Nabees Tech
- AI: named custom OpenAI-compatible provider profiles
- Tools: Hermes terminal, files, browser, skills, MCP and delegation, enabled deliberately
- Safety: sender allowlist, hidden secret entry, config backups and approval gates

## Requirements

- Linux environment with persistent storage
- Python 3.10+
- Node.js 20+ and npm (WhatsApp bridge)
- At least one model endpoint compatible with Hermes; Hermes currently requires at least 64K context for agentic workflows

## Install Hermes

Use the official installer and setup wizard:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes --version
hermes setup
```

Choose a working model and verify a normal chat before setting up messaging.

## Install the Nabees provider manager

From this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/provider_manager.py --help
```

Add a provider. Its API key is collected with hidden terminal input and stored in Hermes' private environment file:

```bash
python scripts/provider_manager.py add
python scripts/provider_manager.py list
python scripts/provider_manager.py test PROVIDER_NAME
python scripts/provider_manager.py activate PROVIDER_NAME
```

The manager tests a normal chat completion and attempts a function/tool-call check. It backs up Hermes configuration before switching. If a change breaks the setup, use:

```bash
python scripts/provider_manager.py rollback
```

**Important:** this first version accepts secrets through a hidden terminal prompt. Do not send API keys in ordinary WhatsApp messages; chat history and model context are not a suitable secret vault. A secure one-time credential flow can be added separately.

## WhatsApp setup

Hermes has a built-in Baileys WhatsApp bridge:

```bash
hermes whatsapp
hermes gateway setup
```

Pair by scanning the terminal QR code using WhatsApp → Settings → Linked Devices → Link a Device.

Set a private sender allowlist in `~/.hermes/.env` (country code, no plus sign):

```env
WHATSAPP_ENABLED=true
WHATSAPP_MODE=self-chat
WHATSAPP_ALLOWED_USERS=234XXXXXXXXXX
```

Then run:

```bash
hermes gateway
hermes gateway status
```

Use a dedicated number if possible. The Baileys bridge emulates WhatsApp Web and is unofficial, so there is some account-restriction risk. Avoid bulk or unsolicited messaging.

## Identity and operating policy

See [config/identity.md](config/identity.md). Nabees Agent should identify as Nabees Agent by Nabees Tech; Hermes is the underlying runtime, not its identity.

## Security

- Never enable wildcard sender access for a private assistant.
- Keep API keys in Hermes' private `~/.hermes/.env`, not this repository.
- Do not commit `~/.hermes/.env`, WhatsApp credentials, provider registry files, tokens or logs.
- Require owner approval for destructive operations, purchases, external publication, third-party messaging and security/access changes.
- Back up important state before modifying it.
- Verify actions before reporting success.

## Current scope and limitations

The provider manager currently targets OpenAI-compatible Chat Completions endpoints using Hermes' `openai-api` provider. Not every endpoint that supports text chat supports tool calls or Hermes' full tool schema. Passing the basic chat test is not proof of full agentic compatibility; the tool-call test and a real Hermes tool-use test are also needed.

Hermes remains an upstream dependency. Consult the official documentation for current setup and compatibility:

- [Quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart)
- [Providers](https://hermes-agent.nousresearch.com/docs/integrations/providers/)
- [WhatsApp](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp)
