"""Append-only JSON-lines log of every applied move, so an agent or a human can audit and undo."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def log_path():
    return Path(os.getenv("UPCLOUD_MOVE_LOG") or Path.home() / ".local/share/upcloud/moves.jsonl")


def log_move(verb, **fields):
    path = log_path()
    record = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "verb": verb, **fields}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:  # the move already happened; say so, keep going
        print(f"warning: could not write the move log {path}: {exc}", file=sys.stderr)
