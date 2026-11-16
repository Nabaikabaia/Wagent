# Nabees Agent

**Nabees Agent by Nabees Tech** is a self-hosted WhatsApp-operated assistant built on [Hermes Agent](https://hermes-agent.nousresearch.com/).

The design goal is provider independence: add API base URLs, API keys and model identifiers, test compatibility, switch models and roll back without tying the agent permanently to one AI vendor.

## Architecture

- Runtime: upstream Hermes Agent, patched locally by the Nabees installer (not a fork)
- Messaging: Hermes WhatsApp bridge (Baileys)
- Authentication: phone-number pairing code; QR display is disabled for the Nabees pairing flow
- Progress: cached WebP stickers sent as association reactions to the original WhatsApp task message
- Hosting target: Linux container / Upstash Box
- AI: named custom OpenAI-compatible provider profiles
- Tools: Hermes terminal, files, browser, skills, MCP and delegation
- Safety: sender allowlist, hidden secret entry, config backups and approval gates

## Requirements

- Linux environment with persistent storage
- Python 3.10+
- Node.js 20+ and npm
- At least one model endpoint compatible with Hermes; tool calling is required for agentic workflows

## Install Hermes

~~~bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes --version
hermes setup
~~~

Choose a working model provider and verify normal chat before configuring WhatsApp.

## Install Wagent

Clone the private repository (authenticate with GitHub if prompted):

~~~bash
cd /workspace/home
git clone https://github.com/Nabaikabaia/Wagent.git
cd Wagent

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
~~~

Install the provider manager and progress sticker skills:

~~~bash
bash scripts/install_skill.sh
~~~

Generate the progress sticker pack:

~~~bash
npm run build:stickers
~~~

The generator writes nine 512×512 WebP sticker assets to ~/.hermes/whatsapp/progress-stickers (or $HERMES_HOME/whatsapp/progress-stickers).

## Install the WhatsApp features

After Hermes is installed, run the patch installer from the activated Hermes Python environment. It locates the installed Hermes bridge and setup wizard, backs up both files, adds the pairing-code flow and authenticated sticker-reaction endpoint, and writes NABEES_WHATSAPP_AUTH_MODE=pairing-code to the private Hermes .env.

~~~bash
python scripts/install_whatsapp_features.py
~~~

If the installer cannot import Hermes modules, run it with the Python interpreter used by the Hermes CLI. It fails closed rather than patching an unknown bridge version. Original files are saved beside the patched files with a .nabees-backup-* suffix.

Then pair WhatsApp:

~~~bash
hermes whatsapp
~~~

Choose bot mode or self-chat. At the bridge prompt, enter the WhatsApp number privately in the Upstash terminal using country code + digits only (no plus sign, spaces or punctuation). The terminal displays an 8-character pairing code.

On the phone:
**WhatsApp → Settings → Linked Devices → Link a Device → Link with phone number instead**, then enter the displayed code.

The linked session is persisted. Ordinary restarts should not require pairing again. If you deliberately unlink the companion device or remove its session credentials, pair again.

Set the owner allowlist when the wizard asks. Keep it restricted to your own number; do not use * for a private assistant.

## Start Nabees Agent

~~~bash
hermes gateway
~~~

Send the linked bot/self-chat a task. For tasks expected to take more than about 15 seconds, Nabees Agent should react to the original message with cached progress stickers:

- ON IT — accepted
- THINKING / SEARCHING — investigation
- COOKING / STILL ON IT — implementation or extended work
- ALMOST DONE — final checks
- DONE — verified completion
- OOPS — failure
- YOUR MOVE — owner approval needed

The sticker is associated with the inbound message using Baileys messageAssociation type 11. Progress updates are sent only at meaningful milestones (normally 2–4 per task), not on every tool call. The actual result still arrives as a normal WhatsApp response.

### Progress helper

The installed skill instructs the agent to call this helper with the current inbound event identifiers:

~~~bash
python3 "$NABEES_WAGENT_HOME/scripts/progress.py" on-it \
  --chat-id 'CHAT_JID' \
  --message-id 'INBOUND_MESSAGE_ID' \
  --participant 'SENDER_JID'
~~~

For direct chats, omit --participant. Never invent or reuse message identifiers. If the current turn does not expose the source chat/message IDs, continue without a sticker.

## Provider management

Add a provider. The API key is collected with hidden terminal input and stored in Hermes' private environment file:

~~~bash
python scripts/provider_manager.py add
python scripts/provider_manager.py list
python scripts/provider_manager.py test PROVIDER_NAME
python scripts/provider_manager.py activate PROVIDER_NAME
~~~

The manager tests a normal chat completion and attempts a function/tool-call check. It backs up Hermes configuration before switching. To roll back:

~~~bash
python scripts/provider_manager.py rollback
~~~

A successful text-chat test does not prove full agentic compatibility. Verify tool calls in a real Hermes session before relying on a provider.

## Security and operational notes

- Keep API keys in Hermes' private ~/.hermes/.env, not this repository.
- WhatsApp credentials and .bridge-token are account secrets; never commit or share them.
- The sticker reaction endpoint is loopback-only and uses the bridge's per-session bearer token. It accepts only WebP files from the dedicated progress-sticker directory.
- Ask for owner approval before destructive actions, purchases, external publication, third-party messaging and security/access changes.
- Baileys is an unofficial WhatsApp Web client. Use a dedicated number where possible and avoid bulk or unsolicited messaging; account restrictions are possible.
- The Nabees patcher is version-sensitive. It checks exact upstream source anchors and stops if the installed Hermes version differs. Backups are created before each modified source file is written.
- The anonymous android.chat.openai.com web-chat endpoint is not an official stable API and is not the same as an OpenAI-compatible tool-calling provider. Do not use it as the sole agentic model backend.

## Upstream documentation

- [Hermes Quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart)
- [Hermes Providers](https://hermes-agent.nousresearch.com/docs/integrations/providers/)
- [Hermes WhatsApp](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp)
- [Baileys](https://github.com/WhiskeySockets/Baileys)
