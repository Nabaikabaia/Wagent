#!/usr/bin/env python3
"""Provider registry for Nabees Agent; secrets stay in Hermes' private .env."""
from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("Install dependencies first: pip install -r requirements.txt")

HERMES = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()
ENV = HERMES / ".env"
CONFIG = HERMES / "config.yaml"
REGISTRY = HERMES / "nabees-providers.json"
BACKUPS = HERMES / "backups" / "nabees-provider-manager"
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,39}$")


def registry():
    if not REGISTRY.exists():
        return {"providers": {}, "active": None, "last_backup": None}
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    data.setdefault("providers", {})
    return data


def env_lines():
    return ENV.read_text(encoding="utf-8").splitlines() if ENV.exists() else []


def get_env(key):
    for line in reversed(env_lines()):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def set_env(values):
    lines = env_lines()
    for key, value in values.items():
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        replacement = f'{key}="{escaped}"'
        hits = [i for i, line in enumerate(lines) if line.startswith(key + "=")]
        if hits:
            lines[hits[-1]] = replacement
            for i in reversed(hits[:-1]):
                del lines[i]
        else:
            lines.append(replacement)
    ENV.parent.mkdir(parents=True, exist_ok=True)
    tmp = ENV.with_suffix(".env.tmp")
    tmp.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(ENV)


def save_registry(data):
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(REGISTRY)


def base_url(value):
    value = value.strip().rstrip("/")
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise ValueError("Enter an absolute http(s) base URL")
    if parsed.username or parsed.password:
        raise ValueError("Do not embed credentials in the URL")
    if parsed.scheme != "https" and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("HTTPS is required except for localhost")
    return value


def http_json(url, key, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "Nabees-Agent/0.1"},
        method="GET" if payload is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            return res.status, json.loads(res.read(2_000_000).decode())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Provider returned HTTP {exc.code}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Provider connection failed: {exc.reason}") from None
    except (TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
        raise RuntimeError("Provider timed out or returned invalid JSON") from None


def test_provider(p):
    key = get_env(p["key_env"])
    if not key:
        raise RuntimeError("Provider key is missing from Hermes' private .env")
    base, model = p["base_url"], p["model"]
    models_found = None
    try:
        _, data = http_json(base + "/models", key)
        ids = [x.get("id") for x in data.get("data", []) if isinstance(x, dict)]
        models_found = model in ids if ids else None
    except RuntimeError:
        pass  # Some compatible endpoints do not expose /models.

    status, data = http_json(base + "/chat/completions", key, {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly NABEES_PROVIDER_OK"}],
        "max_tokens": 32
    })
    choices = data.get("choices") or []
    chat_ok = bool(choices and choices[0].get("message", {}).get("content"))
    tool_ok = False
    tool_note = None
    try:
        _, result = http_json(base + "/chat/completions", key, {
            "model": model,
            "messages": [{"role": "user", "content": "Use the ping function with value nabees."}],
            "tools": [{"type": "function", "function": {
                "name": "ping", "description": "Provider compatibility test",
                "parameters": {"type": "object", "properties": {
                    "value": {"type": "string"}}, "required": ["value"]}
            }}],
            "tool_choice": "auto", "max_tokens": 64
        })
        msg = (result.get("choices") or [{}])[0].get("message", {})
        tool_ok = bool(msg.get("tool_calls"))
    except RuntimeError as exc:
        tool_note = str(exc)
    return {"models_listed_model": models_found, "chat_http_status": status,
            "chat_completion_ok": chat_ok, "tool_calling_ok": tool_ok,
            "tool_calling_note": tool_note}


def backup():
    BACKUPS.mkdir(parents=True, exist_ok=True)
    target = BACKUPS / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target.mkdir(mode=0o700)
    for path in (CONFIG, ENV, REGISTRY):
        if path.exists():
            shutil.copy2(path, target / path.name)
    return target


def add(_):
    name = input("Provider name: ").strip()
    if not NAME.fullmatch(name):
        raise ValueError("Name must be 2-40 letters, numbers, _ or -")
    data = registry()
    if name in data["providers"]:
        raise ValueError("That provider name already exists")
    url = base_url(input("OpenAI-compatible API base URL: "))
    model = input("Model identifier: ").strip()
    if not model:
        raise ValueError("Model identifier is required")
    secret = getpass.getpass("API key (hidden): ").strip()
    if not secret:
        raise ValueError("API key cannot be empty")
    key_env = "NABEES_PROVIDER_" + re.sub(r"[^A-Z0-9]", "_", name.upper()) + "_API_KEY"
    set_env({key_env: secret})
    data["providers"][name] = {"base_url": url, "model": model, "key_env": key_env}
    save_registry(data)
    print(f"Saved '{name}'. Test it with: python scripts/provider_manager.py test {name}")


def listing(_):
    data = registry()
    if not data["providers"]:
        print("No custom providers saved.")
    for name, p in data["providers"].items():
        active = " [active]" if data.get("active") == name else ""
        print(f"{name}{active}: {p['model']} — {p['base_url']}")


def test(args):
    p = registry()["providers"].get(args.name)
    if not p:
        raise ValueError("Unknown provider: " + args.name)
    result = test_provider(p)
    print(json.dumps(result, indent=2))
    if not result["chat_completion_ok"]:
        raise SystemExit(1)


def activate(args):
    data = registry()
    p = data["providers"].get(args.name)
    if not p:
        raise ValueError("Unknown provider: " + args.name)
    result = test_provider(p)
    print(json.dumps(result, indent=2))
    if not result["chat_completion_ok"]:
        raise RuntimeError("Basic chat test failed; provider was not activated")
    old_backup = backup()
    cfg = {}
    if CONFIG.exists():
        cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    model_cfg = cfg.setdefault("model", {})
    if not isinstance(model_cfg, dict):
        raise ValueError("Unexpected Hermes model configuration format")
    model_cfg["provider"] = "openai-api"
    model_cfg["default"] = p["model"]
    set_env({"OPENAI_BASE_URL": p["base_url"], "OPENAI_API_KEY": get_env(p["key_env"])})
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG.with_suffix(".yaml.tmp")
    tmp.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(CONFIG)
    data["active"] = args.name
    data["last_backup"] = str(old_backup)
    save_registry(data)
    print(f"Activated {args.name} / {p['model']}. Backup: {old_backup}")
    if not result["tool_calling_ok"]:
        print("WARNING: text chat passed, but tool calling was not confirmed. Verify Hermes tool use before relying on agentic tasks.")


def rollback(_):
    data = registry()
    path = Path(data.get("last_backup") or "")
    if not path.is_dir():
        raise RuntimeError("No provider-manager backup is available")
    for filename in ("config.yaml", ".env", "nabees-providers.json"):
        src = path / filename
        if src.exists():
            dst = HERMES / filename
            shutil.copy2(src, dst)
            os.chmod(dst, 0o600)
    print("Restored configuration from " + str(path))


def main():
    parser = argparse.ArgumentParser(description="Nabees Agent provider manager")
    subs = parser.add_subparsers(required=True)
    for name, fn, help_text in [
        ("add", add, "Add a provider with hidden key entry"),
        ("list", listing, "List saved providers"),
        ("test", test, "Test a provider"),
        ("activate", activate, "Test, back up and activate a provider"),
        ("rollback", rollback, "Restore the latest backup")
    ]:
        p = subs.add_parser(name, help=help_text)
        if name in ("test", "activate"):
            p.add_argument("name")
        p.set_defaults(func=fn)
    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
