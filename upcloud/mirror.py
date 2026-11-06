"""Plan and apply a one-way local -> OneDrive mirror. Never deletes anything."""
# REUSE_CHECKED: none in _dev repos (mirror hits are calendar/ISPC); rclone not installed; ticket targets upcloud
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .quickxor import quickxor_file

WORKERS = 8


@dataclass(frozen=True)
class Action:
    kind: str            # upload | skip | extra
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
        return {src.name: src}
    if not src.is_dir():
        raise FileNotFoundError(f"local folder not found: {src}")
    found = src.rglob("*") if recursive else src.glob("*")
    return {p.relative_to(src).as_posix(): p for p in sorted(found) if p.is_file()}


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


def _compare(path, item, size):
    """Skip on equal size; if OneDrive has a quickXorHash, it must match too."""
    if item.get("size") != size:
        return "upload", "changed size"
    remote_hash = item.get("file", {}).get("hashes", {}).get("quickXorHash")
    if remote_hash and quickxor_file(path) != remote_hash:
        return "upload", "changed content"
    return "skip", "same size and hash" if remote_hash else "same size"


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
