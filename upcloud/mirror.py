"""Plan and apply a one-way local -> OneDrive mirror. Never deletes anything or uploads secrets."""
# REUSE_CHECKED: none in _dev repos (mirror hits are calendar/ISPC); rclone not installed; ticket targets upcloud
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath

from .quickxor import quickxor_file
from .safety import is_sensitive

WORKERS = 8
JUNK = {".ds_store", "thumbs.db", "desktop.ini"}


@dataclass(frozen=True)
class Action:
    kind: str            # upload | skip | extra | newer
    rel: str             # posix path relative to SRC / DST
    reason: str
    size: int = 0
    local: Path = None


@dataclass
class Result:
    uploaded: list = field(default_factory=list)
    failed: list = field(default_factory=list)    # [(rel, error message)]


def _join(*parts):
    return "/".join(p.strip("/") for p in parts if p and p.strip("/") not in ("", "."))


def scan_local(src, recursive=True):
    """{relative/posix/path: Path} for every local file under src."""
    src = Path(src)
    if src.is_file():
        return {} if is_sensitive(src.name) or src.is_symlink() else {src.name: src}
    if not src.is_dir():
        raise FileNotFoundError(f"local folder not found: {src}")
    found = src.rglob("*") if recursive else src.glob("*")
    return {p.relative_to(src).as_posix(): p for p in sorted(found)
            if p.is_file() and not p.is_symlink() and p.name.lower() not in JUNK and not p.name.startswith("._")
            and not is_sensitive(p.relative_to(src).as_posix())}


def remote_files(client, dst, recursive=True):
    """{relative/posix/path: driveItem} for files under OneDrive dst ({} if dst is missing)."""
    if client.get_item(dst) is None:
        return {}
    files, pending = {}, [""]
    while pending:
        rel_dir = pending.pop()
        for item in client.list_children(_join(dst, rel_dir)):
            rel = _join(rel_dir, item["name"])
            if "folder" in item and recursive:
                pending.append(rel)
            elif "file" in item:
                files[rel] = item
    return files


def _remote_is_newer(path, item):
    # fileSystemInfo only: the top-level stamp is upload time, always "newer".
    stamp = item.get("fileSystemInfo", {}).get("lastModifiedDateTime")
    try:
        remote = datetime.fromisoformat(stamp.rstrip("Z").split(".")[0] + "+00:00").timestamp()
    except (AttributeError, ValueError):
        return False
    return remote > path.stat().st_mtime + 2  # 2 s for filesystem rounding


def _compare(path, item, size):
    """Skip on equal size; if OneDrive has a quickXorHash, it must match too.
    A differing file whose OneDrive copy is newer is never overwritten."""
    remote_hash = item.get("file", {}).get("hashes", {}).get("quickXorHash")
    if item.get("size") != size:
        kind, reason = "upload", "changed size"
    elif remote_hash and quickxor_file(path) != remote_hash:
        kind, reason = "upload", "changed content"
    else:
        return "skip", "same size and hash" if remote_hash else "same size"
    if _remote_is_newer(path, item):
        return "newer", "OneDrive copy is newer, left alone"
    return kind, reason


def plan_mirror(client, src, dst, recursive=True):
    local = scan_local(src, recursive)
    remote = remote_files(client, dst, recursive)
    actions = []
    for rel, path in local.items():
        size = path.stat().st_size
        kind, reason = ("upload", "new") if rel not in remote else _compare(path, remote[rel], size)
        actions.append(Action(kind, rel, reason, size, path))
    for rel in sorted(set(remote) - set(local)):
        actions.append(Action("extra", rel, "only on OneDrive, left alone", remote[rel].get("size", 0)))
    return actions


def _parent(path):
    parent = str(PurePosixPath(path).parent)
    return "" if parent == "." else parent


def ensure_folder(client, path, known):
    """Create path and missing parents, one segment at a time, sequentially."""
    current = ""
    for segment in [s for s in path.split("/") if s]:
        parent, current = current, _join(current, segment)
        if current not in known and client.get_item(current) is None:
            client.create_folder(segment, parent or None)
        known.add(current)


def apply_plan(client, dst, actions, workers=WORKERS, report=None):
    report = report or (lambda *a: None)
    result, known = Result(), set()
    uploads = [a for a in actions if a.kind == "upload"]
    for folder in sorted({_parent(_join(dst, a.rel)) for a in uploads}):
        ensure_folder(client, folder, known)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(client.upload_file, a.local, _parent(_join(dst, a.rel)) or None): a.rel
                   for a in uploads}
        for future in as_completed(futures):
            rel = futures[future]
            try:
                future.result()
                result.uploaded.append(rel)
                report("uploaded", rel)
            except Exception as exc:  # reported per file; the run continues
                result.failed.append((rel, str(exc)))
                report("failed", rel, str(exc))
    result.uploaded.sort()
    return result
