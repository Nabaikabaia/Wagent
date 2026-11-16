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

Use the current inbound WhatsApp event's exact chat_id, message_id and, for group messages, sender_id / participant JID. Never guess or reuse identifiers from another turn. If the current turn does not expose these identifiers, do not fabricate them; continue without a sticker.

## Command

Run the helper from the Wagent checkout:

    python3 "$NABEES_WAGENT_HOME/scripts/progress.py" on-it --chat-id 'CHAT_JID' --message-id 'INBOUND_MESSAGE_ID' --participant 'SENDER_JID'

Available stages: on-it, thinking, searching, coding, still-on-it, almost-done, done, error, approval.

For direct chats, omit --participant. The helper reads the private bridge token and sends a cached WebP through the authenticated local bridge. It never prints the token.

## Requirements

- The Hermes gateway must be running and connected.
- Assets must exist in ~/.hermes/whatsapp/progress-stickers (build with npm run build:stickers).
- Only react to the owner's current inbound task message.
- A sticker failure must never cancel the actual task; fall back to text progress if needed.
