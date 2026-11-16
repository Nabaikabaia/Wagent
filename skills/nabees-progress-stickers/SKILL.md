---
name: nabees-progress-stickers
description: Send cached Nabees progress WebP stickers as WhatsApp reactions to the message that started a long task.
---

# Nabees progress sticker reactions

Use this capability for WhatsApp tasks that require sustained work. These are message-associated sticker reactions, not standalone chat messages.

## When to use

- For a task expected to take more than about 15 seconds, react with ON IT shortly after accepting it.
- During longer work, send a new reaction only at meaningful milestones: THINKING, SEARCHING, COOKING, STILL ON IT, or ALMOST DONE.
- Finish with DONE only after the result is verified. Use OOPS if the task fails. Use YOUR MOVE when waiting for owner approval.
- Do not send a sticker for every tool call. Usually 2-4 updates per task are enough.
- For quick answers, do not send progress stickers.

## Required message context

Use the current inbound WhatsApp event's exact chat_id. Never guess a recipient or reuse a chat ID from another turn. The bridge keeps a bounded, one-hour cache of accepted inbound message keys separately for each chat, so the helper does not need a fabricated message ID or participant. If the current turn does not expose its current chat_id, do not send a reaction.

## Command

Run the helper from the Wagent checkout:

    python3 "$NABEES_WAGENT_HOME/scripts/progress.py" on-it --chat-id 'CURRENT_CHAT_JID'

Use the same current chat JID for later stages. Available stages: on-it, thinking, searching, coding, still-on-it, almost-done, done, error, approval.

The bridge resolves the latest accepted inbound message key for that exact chat and sends the associated WebP reaction through the authenticated local endpoint. The helper reads the private bridge token and never prints it. The explicit --message-id option remains available when an exact message key is already supplied by the runtime.

## Requirements

- The Hermes gateway must be running and connected.
- Assets must exist in ~/.hermes/whatsapp/progress-stickers (build with npm run build:stickers).
- Only react to the owner's current inbound task message.
- A sticker failure must never cancel the actual task; fall back to text progress if needed.
