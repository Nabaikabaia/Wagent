#!/usr/bin/env python3
"""Send a cached Nabees progress WebP as a reaction to an inbound WhatsApp message."""
from __future__ import annotations
import argparse, json, os, sys, urllib.error, urllib.request
from pathlib import Path

STAGES = ("on-it", "thinking", "searching", "coding", "still-on-it", "almost-done", "done", "error", "approval")
def hermes_home():
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()
def session_dir():
    return Path(os.environ.get("NABEES_WA_SESSION_DIR", hermes_home() / "whatsapp" / "session")).expanduser()
def bridge_port():
    port_file = hermes_home() / "platforms" / "whatsapp" / "bridge_port"
    try:
        value = int(port_file.read_text(encoding="utf-8").strip())
        if 1 <= value <= 65535: return value
    except (OSError, ValueError): pass
    return int(os.environ.get("WHATSAPP_BRIDGE_PORT", "3000"))
def send(args):
    if args.stage not in STAGES: raise ValueError("Unknown progress stage")
    if not args.chat_id: raise ValueError("--chat-id is required")
    if not (args.chat_id.endswith("@g.us") or args.chat_id.endswith("@s.whatsapp.net") or args.chat_id.endswith("@lid")):
        raise ValueError("Unsupported WhatsApp chat JID")
    token = (session_dir() / ".bridge-token").read_text(encoding="utf-8").strip()
    if len(token) < 32: raise RuntimeError("WhatsApp bridge token missing; start the Hermes gateway first")
    sticker_dir = hermes_home() / "whatsapp" / "progress-stickers"
    sticker_path = sticker_dir / (args.stage + ".webp")
    if not sticker_path.is_file(): raise RuntimeError("Sticker asset missing; run npm run build:stickers")
    if args.message_id:
        parent = {"remoteJid": args.chat_id, "id": args.message_id, "fromMe": False}
        if args.participant: parent["participant"] = args.participant
        payload = {"chatId": args.chat_id, "filePath": str(sticker_path.resolve()),
                   "parentMessageKey": parent, "associationType": 11}
        route = "/react-sticker"
    else:
        # The bridge resolves the latest accepted inbound message key for this
        # exact chat; the helper never invents or reuses a message ID.
        payload = {"chatId": args.chat_id, "stage": args.stage, "associationType": 11}
        route = "/react-sticker-latest"
    request = urllib.request.Request(
        "http://127.0.0.1:" + str(bridge_port()) + route,
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise RuntimeError("Sticker reaction failed (HTTP " + str(exc.code) + "): " + detail) from None
    except urllib.error.URLError as exc:
        raise RuntimeError("Could not reach WhatsApp bridge: " + str(exc.reason)) from None
    if not result.get("success"): raise RuntimeError("Bridge did not confirm the sticker reaction")
    print("Sticker reaction sent.")
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--chat-id", required=True)
    parser.add_argument("--message-id", help="Optional exact inbound message ID; otherwise use the bridge latest-key cache for this chat")
    parser.add_argument("--participant")
    args = parser.parse_args()
    try:
        send(args); return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print("Progress sticker error: " + str(exc), file=sys.stderr); return 1
if __name__ == "__main__": raise SystemExit(main())
