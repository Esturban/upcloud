"""Roots file: which local folder mirrors to which OneDrive folder.

~/.config/upcloud/roots.tsv, one pair per line: local_dir TAB onedrive_dir. '#' starts a comment.
"""
import os
from dataclasses import dataclass
from pathlib import Path


class RootsError(Exception):
    """The roots file is malformed."""


@dataclass(frozen=True)
class Root:
    local: Path
    onedrive: str


def roots_path():
    return Path(os.getenv("UPCLOUD_ROOTS") or Path.home() / ".config/upcloud/roots.tsv")


def load_roots():
    path = roots_path()
    if not path.is_file():
        return []
    roots = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 2 or not cols[0].strip() or not cols[1].strip("/ "):
            raise RootsError(f"{path} line {number}: expected `local_dir<TAB>onedrive_dir`.\n"
                             "  Fix: separate the two folders with a single TAB character.")
        local = Path(cols[0].strip()).expanduser()
        if not local.is_absolute():
            raise RootsError(f"{path} line {number}: local_dir must be absolute or start with ~.\n"
                             f"  Fix: write the full path for `{cols[0].strip()}`.")
        roots.append(Root(local, cols[1].strip().strip("/")))
    return roots


def _fold(path):
    return str(path).casefold()  # macOS volumes are case-insensitive


def resolve(path):
    """OneDrive folder for a local path inside a root (longest matching root wins), else None."""
    path = Path(path).expanduser().resolve()
    best = None
    for root in load_roots():
        base = root.local.resolve()
        if _fold(path) == _fold(base) or _fold(base) in [_fold(p) for p in path.parents]:
            if best is None or len(base.parts) > len(best[0].parts):
                best = (base, root.onedrive)
    if best is None:
        return None
    rel = "/".join(path.parts[len(best[0].parts):])
    return f"{best[1]}/{rel}" if rel else best[1]
