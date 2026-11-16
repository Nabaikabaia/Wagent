#!/usr/bin/env python3
"""Patch installed Hermes WhatsApp bridge with Nabees pairing-code and sticker-reaction support."""
from __future__ import annotations
import os, shlex, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

def hermes_python():
    executable = shutil.which("hermes")
    if not executable: return None
    try:
        first = Path(executable).read_text(encoding="utf-8").splitlines()[0]
        if first.startswith("#!"):
            parts = shlex.split(first[2:].strip())
            if parts and Path(parts[0]).name == "env" and len(parts) > 1:
                candidate = shutil.which(parts[1])
            else:
                candidate = parts[0] if parts else None
            if candidate and Path(candidate).is_file(): return candidate
    except (OSError, IndexError): pass
    return None

def maybe_reexec():
    if os.environ.get("NABEES_INSTALLER_REEXEC") == "1": return
    candidate = hermes_python()
    if candidate and Path(candidate).resolve() != Path(sys.executable).resolve():
        env = dict(os.environ, NABEES_INSTALLER_REEXEC="1")
        probe = subprocess.run([candidate, "-c", "import gateway.platforms.whatsapp_common, hermes_cli.main_platform_setup"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, check=False)
        if probe.returncode == 0: os.execve(candidate, [candidate, __file__, *sys.argv[1:]], env)

def resolve_targets():
    from gateway.platforms.whatsapp_common import resolve_whatsapp_bridge_dir
    import hermes_cli.main_platform_setup as setup_module
    return Path(resolve_whatsapp_bridge_dir()) / "bridge.js", Path(setup_module.__file__)

def replace_once(source, old, new, label):
    if new in source: return source
    count = source.count(old)
    if count != 1: raise RuntimeError("Cannot safely patch " + label + ": expected one anchor, found " + str(count))
    return source.replace(old, new, 1)

def backup_and_write(path, source):
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_name(path.name + ".nabees-backup-" + stamp)
    shutil.copy2(path, backup); path.write_text(source, encoding="utf-8")
    print("Updated " + str(path) + " (backup: " + str(backup) + ")")

def patch_bridge(path):
    source = path.read_text(encoding="utf-8")
    if "NABEES_PROGRESS_REACTION_ROUTE" in source and "NABEES_PAIRING_CODE_FLOW" in source:
        print("WhatsApp bridge already has Nabees features."); return
    source = replace_once(source, "import { attachPasskeyFlow, loadPasskeySigner } from './passkey_socket.js';",
        "import { attachPasskeyFlow, loadPasskeySigner } from './passkey_socket.js';\nimport { ReactImg } from './react_img.js';", "ReactImg import")
    source = replace_once(source, "let connectionState = 'disconnected';",
        "let connectionState = 'disconnected';\nlet nabeesPairingCodeRequested = false; // NABEES_PAIRING_CODE_FLOW", "pair-code state")
    source = replace_once(source, "    if (qr) {\n      if (PAIR_JSON) {",
        """    if (qr) {
      if (PAIR_ONLY && !PAIR_JSON && process.env.NABEES_WHATSAPP_AUTH_MODE !== 'qr' && !state.creds.registered) {
        if (!nabeesPairingCodeRequested) {
          nabeesPairingCodeRequested = true;
          (async () => {
            const terminal = createInterface({ input: process.stdin, output: process.stdout });
            let phoneNumber;
            try {
              phoneNumber = (await terminal.question('WhatsApp number to link (country code + digits only, no + or spaces): ')).trim();
            } finally { terminal.close(); }
            if (!/^\\\\d{8,15}$/.test(phoneNumber)) throw new Error('Use 8-15 digits including country calling code.');
            const code = await sock.requestPairingCode(phoneNumber);
            console.log('\\\\nWhatsApp pairing code: ' + code + '\\\\n');
            console.log('On your phone: WhatsApp → Settings → Linked Devices → Link a Device → Link with phone number instead.');
            console.log('Enter the code above. Waiting for WhatsApp to finish linking...\\\\n');
          })().catch((error) => { console.error('Pairing-code request failed: ' + error.message); process.exit(1); });
        }
      } else if (PAIR_JSON) {""", "pair-code QR event handler")
    anchor = "// Typing indicator\napp.post('/typing', async (req, res) => {"
    route = """// NABEES_PROGRESS_REACTION_ROUTE
app.post('/react-sticker', async (req, res) => {
  if (!sock || connectionState !== 'connected') return res.status(503).json({ error: 'Not connected to WhatsApp' });
  const { chatId, filePath, parentMessageKey, associationType = 11 } = req.body || {};
  if (!chatId || !filePath || !parentMessageKey?.id || parentMessageKey.remoteJid !== chatId)
    return res.status(400).json({ error: 'chatId, filePath and matching parentMessageKey are required' });
  const allowedDir = path.resolve(path.join(path.dirname(SESSION_DIR), 'progress-stickers'));
  const resolvedFile = path.resolve(filePath);
  if (!resolvedFile.startsWith(allowedDir + path.sep) || path.extname(resolvedFile).toLowerCase() !== '.webp')
    return res.status(403).json({ error: 'Sticker path is outside the Nabees progress-sticker directory' });
  if (!existsSync(resolvedFile)) return res.status(404).json({ error: 'Sticker file not found' });
  try {
    const sent = await enqueueSend(() => ReactImg.create(sock).send(chatId, {
      parentMessageKey, associationType, filePath: resolvedFile
    }));
    res.json({ success: true, messageId: sent?.key?.id || null });
  } catch (err) { res.status(500).json({ error: err?.message || 'Sticker reaction failed' }); }
});

// Typing indicator
app.post('/typing', async (req, res) => {"""
    source = replace_once(source, anchor, route, "progress reaction route")
    backup_and_write(path, source)

def patch_setup(path):
    source = path.read_text(encoding="utf-8")
    if "Nabees pairing-code flow" in source:
        print("Hermes WhatsApp setup wizard already updated."); return
    old = """    # QR code pairing
    _say("", "─" * 50)
    if wa_mode == "bot":
        _say("📱 Open WhatsApp (or WhatsApp Business) on the", "   phone with the BOT's number, then scan:")
    else:
        print("📱 Open WhatsApp on your phone, then scan:")
    _say("", "   Settings → Linked Devices → Link a Device", "─" * 50, "")"""
    new = """    # Nabees pairing-code flow (Baileys requestPairingCode; no QR is printed).
    _say("", "─" * 50)
    if wa_mode == "bot":
        _say("📱 Open WhatsApp (or WhatsApp Business) on the phone with the BOT's number.")
    else:
        print("📱 Open WhatsApp on the phone number you want to link.")
    _say("", "   Settings → Linked Devices → Link a Device → Link with phone number instead",
         "   The terminal will ask for the number and display an 8-character code.",
         "─" * 50, "")"""
    source = replace_once(source, old, new, "WhatsApp setup wizard pairing instructions")
    backup_and_write(path, source)

def set_env_mode():
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()
    env_file = home / ".env"; env_file.parent.mkdir(parents=True, exist_ok=True)
    lines = env_file.read_text(encoding="utf-8").splitlines() if env_file.exists() else []
    key = "NABEES_WHATSAPP_AUTH_MODE"; found = False
    for index, line in enumerate(lines):
        if line.startswith(key + "="): lines[index] = key + '="pairing-code"'; found = True
    if not found: lines.append(key + '="pairing-code"')
    temp = env_file.with_suffix(".env.nabees.tmp")
    temp.write_text("\\n".join(lines).rstrip() + "\\n", encoding="utf-8")
    os.chmod(temp, 0o600); temp.replace(env_file)
    print("Set " + key + "=pairing-code in " + str(env_file))

def main():
    maybe_reexec()
    try:
        bridge, setup = resolve_targets()
        react_source = Path(__file__).with_name("react_img.js")
        if not react_source.is_file(): raise RuntimeError("Missing ReactImg module: " + str(react_source))
        react_dest = bridge.parent / "react_img.js"
        if not react_dest.exists() or react_dest.read_bytes() != react_source.read_bytes():
            if react_dest.exists():
                stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                shutil.copy2(react_dest, react_dest.with_name("react_img.js.nabees-backup-" + stamp))
            shutil.copy2(react_source, react_dest)
        patch_bridge(bridge); patch_setup(setup); set_env_mode()
        print("\\nNabees WhatsApp features installed.")
        print("Next: npm run build:stickers -- ~/.hermes/whatsapp/progress-stickers")
        print("Then run: hermes whatsapp")
        return 0
    except Exception as exc:
        print("Install failed safely: " + str(exc), file=sys.stderr); return 1

if __name__ == "__main__": raise SystemExit(main())
