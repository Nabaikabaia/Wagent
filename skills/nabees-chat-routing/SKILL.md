---
name: nabees-chat-routing
description: Keep WhatsApp replies in the originating conversation and prevent cross-chat or stale-recipient sends.
---

# Nabees WhatsApp chat routing

## Normal replies

- A normal answer to the current inbound WhatsApp message must be returned through the active conversation response. Do not call a separate outbound messaging tool to answer the same message.
- Use the current event's source chat JID as the only default destination.
- Never infer a recipient from the owner's phone number, a previous chat, memory, a quoted contact, or a message body.
- Never reuse a target_ref, chat_id, or JID from another task or conversation.
- If the agent's current session has no source chat JID, do not send a WhatsApp message through a guessed destination.

## Explicit third-party messages

- Use an outbound messaging tool only when the owner explicitly asks to contact another person or group.
- Confirm the destination if the requested person or group cannot be mapped unambiguously to a recipient.
- In a group, send to the group JID; use the participant JID only to identify or mention the individual sender.
- Before sending, verify the tool's destination matches the owner's explicit request.

## Generated files and media

- For artifacts created for the current conversation, use the active WhatsApp adapter's native media/document method with the current source chat JID.
- Never use a remembered recipient as a fallback.
- Do not send a file to another chat just because its path or previous delivery metadata is available.

## Failure handling

- If the send tool proposes a different chat from the current inbound source, stop and report the mismatch.
- Never claim delivery unless the messaging tool confirms success.
