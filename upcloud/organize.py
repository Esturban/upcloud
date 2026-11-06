"""Move things around inside OneDrive: `mv` and `sort-by-year`. Plans first, never overwrites."""
# REUSE_CHECKED: no OneDrive move helper in _dev repos; Graph PATCH parentReference per learn.microsoft.com
import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from requests import RequestException

from .mirror import _join, _parent, ensure_folder
from .movelog import log_move

YEAR = re.compile(r"^\d{4}$")


class MoveRefused(Exception):
    """The move would be unsafe or impossible; the message says what to do."""


@dataclass(frozen=True)
class Move:
    kind: str            # move | skip
    src: str
    dst: str
    reason: str = ""
    item_id: str = ""
    parent_id: str = ""  # known up front for sort-by-year; resolved on apply for mv
    name: str = ""


def plan_mv(client, src, dst):
    src, dst = src.strip("/"), dst.strip("/") if not dst.endswith("/") else dst.strip("/") + "/"
    if not src or any(seg in (".", "..") for seg in dst.split("/")):
        raise MoveRefused("SRC must name an item and DST may not contain . or .. segments.\n"
                          "  Fix: pass full OneDrive paths such as `Work/a.pdf`.")
    item = client.get_item(src)
    if item is None:
        raise FileNotFoundError(f"not found on OneDrive: {src}\n  Fix: check the path with `upcloud ls <parent>`.")
    if dst.endswith("/"):
        dst = _join(dst, PurePosixPath(src).name)
    if dst.casefold() == src.casefold():
        raise MoveRefused(f"{src} is already there.\n  Fix: pass a different DST.")
    if dst.casefold().startswith(src.casefold() + "/"):
        raise MoveRefused(f"cannot move {src} into itself ({dst}).\n  Fix: choose a DST outside {src}.")
    if client.get_item(dst) is not None:
        raise MoveRefused(f"{dst} already exists on OneDrive; mv never overwrites.\n"
                          "  Fix: pick a free name, or move the existing item away first.")
    return Move("move", src, dst, item_id=item["id"], name=PurePosixPath(dst).name)


def missing_parent(client, move):
    """The parent folder that does not exist yet (it would be created), else None."""
    parent = _parent(move.dst)
    return parent if parent and client.get_item(parent) is None else None


def apply_mv(client, move):
    """Create missing parents, move, log. Returns the Move on success; raises on failure."""
    parent = _parent(move.dst)
    ensure_folder(client, parent, set())
    parent_id = client.get_item(parent)["id"]
    return apply_moves(client, [Move(**{**move.__dict__, "parent_id": parent_id})], "mv")


def apply_moves(client, moves, verb, report=None):
    """Apply moves one at a time. Returns (done, failed); every step is logged."""
    report = report or (lambda *a: None)
    done, failed = [], []
    for m in moves:
        if m.kind != "move":
            continue
        try:
            client.move_item(m.item_id, m.parent_id, m.name)
        except RequestException as exc:  # reported per item; the run continues
            failed.append((m, str(exc)))
            log_move(verb, src=m.src, dst=m.dst, status="failed", detail=str(exc))
            report("failed", m, str(exc))
        else:
            done.append(m)
            log_move(verb, src=m.src, dst=m.dst, status="ok")
            report("moved", m)
    return done, failed


def _year(item):
    stamp = (item.get("photo") or {}).get("takenDateTime") \
        or (item.get("fileSystemInfo") or {}).get("createdDateTime") or ""
    return stamp[:4] if YEAR.match(stamp[:4]) else None


def plan_sort_by_year(client, path):
    """Plan moving loose files of `path` into its existing YYYY/ subfolders. Never creates folders."""
    path = path.strip("/")
    children = client.list_children(path)
    years = {c["name"]: c["id"] for c in children if "folder" in c and YEAR.match(c["name"])}
    taken, moves = {}, []
    for item in sorted((c for c in children if "file" in c), key=lambda c: c["name"]):
        name, year = item["name"], _year(item)
        src = _join(path, name)
        if year is None:
            moves.append(Move("skip", src, "", "no date on the file"))
        elif year not in years:
            moves.append(Move("skip", src, "", f"no {year}/ folder here; sort never creates one"))
        else:
            if year not in taken:
                taken[year] = {c["name"] for c in client.list_children(_join(path, year))}
            if name in taken[year]:
                moves.append(Move("skip", src, "", f"{name} is already in {year}/"))
            else:
                taken[year].add(name)
                moves.append(Move("move", src, _join(path, year, name), "", item["id"], years[year], name))
    return moves
