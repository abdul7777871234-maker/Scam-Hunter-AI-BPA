"""Saved chat history, one JSON file per browser id (no accounts needed)."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "data" / "chat_history"
MAX_CHATS = 50
_UID = re.compile(r"^[a-f0-9]{32}$")


def new_id() -> str:
    return uuid.uuid4().hex


def valid_uid(uid) -> bool:
    return isinstance(uid, str) and bool(_UID.fullmatch(uid))


def valid_chat_id(chat_id) -> bool:
    return isinstance(chat_id, str) and bool(_UID.fullmatch(chat_id))


def _sanitize_messages(messages: list) -> list:
    if not isinstance(messages, list):
        return []
    safe = []
    for message in messages[:200]:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role not in {"user", "assistant"}:
            continue
        item = {"role": role, "content": str(message.get("content", ""))[:20000]}
        if "language" in message:
            item["language"] = str(message["language"])[:50]
        if "mode" in message:
            item["mode"] = str(message["mode"])[:50]
        if isinstance(message.get("verdict"), dict):
            item["verdict"] = message["verdict"]
        if isinstance(message.get("sources"), list):
            item["sources"] = message["sources"][:20]
        safe.append(item)
    return safe


def _path(uid: str) -> Path:
    return BASE / f"{uid}.json"


def load_chats(uid: str) -> list:
    if not valid_uid(uid):
        return []
    try:
        data = json.loads(_path(uid).read_text(encoding="utf-8"))
        chats = data.get("chats", []) if isinstance(data, dict) else []
        if not isinstance(chats, list):
            return []
    except (FileNotFoundError, ValueError, OSError, AttributeError):
        return []
    cleaned = []
    for chat in chats[:MAX_CHATS]:
        if not isinstance(chat, dict) or not valid_chat_id(chat.get("id")):
            continue
        cleaned.append({
            "id": chat["id"],
            "title": str(chat.get("title", "New chat"))[:100],
            "created": float(chat.get("created", 0) or 0),
            "updated": float(chat.get("updated", 0) or 0),
            "messages": _sanitize_messages(chat.get("messages", [])),
        })
    return sorted(cleaned, key=lambda c: c.get("updated", 0), reverse=True)


def _write(uid: str, chats: list) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    tmp = _path(uid).with_suffix(".tmp")
    tmp.write_text(json.dumps({"chats": chats}, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, _path(uid))


def _title(messages: list) -> str:
    for m in messages:
        if m.get("role") == "user":
            text = " ".join(str(m.get("content", "")).split())
            return (text[:45] + "…") if len(text) > 45 else (text or "New chat")
    return "New chat"


def save_chat(uid: str, chat_id: str, messages: list) -> None:
    if not valid_uid(uid) or not valid_chat_id(chat_id) or not messages:
        return
    chats = load_chats(uid)
    now = time.time()
    for chat in chats:
        if chat.get("id") == chat_id:
            chat["messages"] = _sanitize_messages(messages)
            chat["updated"] = now
            break
    else:
        chats.append(
            {
                "id": chat_id,
                "title": _title(messages),
                "created": now,
                "updated": now,
                "messages": _sanitize_messages(messages),
            }
        )
    chats.sort(key=lambda c: c.get("updated", 0), reverse=True)
    try:
        _write(uid, chats[:MAX_CHATS])
    except OSError:
        pass  # history is best-effort; never break the app


def delete_chat(uid: str, chat_id: str) -> None:
    if not valid_uid(uid) or not valid_chat_id(chat_id):
        return
    chats = load_chats(uid)
    remaining = [chat for chat in chats if chat.get("id") != chat_id]
    if len(remaining) == len(chats):
        return
    try:
        _write(uid, remaining[:MAX_CHATS])
    except OSError:
        pass


def delete_all(uid: str) -> None:
    if valid_uid(uid):
        try:
            _path(uid).unlink(missing_ok=True)
        except OSError:
            pass
