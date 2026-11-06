"""Free local disk safely: `review` finds files whose OneDrive copy is proven identical and
untouched locally; `offload` re-verifies each one, then moves the Mac file to the macOS Trash.
Nothing is ever hard-deleted and no OneDrive item is ever touched.
"""
# REUSE_CHECKED: no verified-offload tool in _dev repos; rclone not installed; macOS ships /usr/bin/trash
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .mirror import _join, remote_files, scan_local
from .movelog import log_move
from .quickxor import quickxor_file
from .safety import is_sensitive

DAY_SECONDS = 86400
TRASH_TIMEOUT_SECONDS = 120
PLAN_HEADER = "# local\tonedrive\tsize\tquickxor\tmtime"


class TrashError(Exception):
    """The file could not be moved to the macOS Trash."""


class PlanError(Exception):
    """plan.tsv is malformed."""


@dataclass(frozen=True)
class Row:
    local: str
    onedrive: str
    size: int
    quickxor: str
    mtime: int


def review_root(client, root, days, now=None):
    """Rows for files under root.local that OneDrive holds byte-identical and that were not
    opened or modified locally in `days` days. Raises FileNotFoundError for a missing folder."""
    cutoff = (now or time.time()) - days * DAY_SECONDS
    if is_sensitive(root.onedrive):
        return []
    local = scan_local(root.local)
    remote = remote_files(client, root.onedrive)
    rows = []
    for rel, path in local.items():
        item = remote.get(rel)
        if item is None or path.is_symlink() or "\t" in str(path) or "\n" in str(path):
            continue
        stat = path.stat()
        remote_hash = item.get("file", {}).get("hashes", {}).get("quickXorHash")
        if max(stat.st_atime, stat.st_mtime) >= cutoff or item.get("size") != stat.st_size or not remote_hash:
            continue
        if quickxor_file(path) == remote_hash:
            rows.append(Row(str(path), _join(root.onedrive, rel), stat.st_size, remote_hash, int(stat.st_mtime)))
    return rows


def write_plan(rows, path):
    lines = [PLAN_HEADER] + ["\t".join([r.local, r.onedrive, str(r.size), r.quickxor, str(r.mtime)])
                             for r in rows]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_plan(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        try:
            if len(cols) != 5:
                raise ValueError
            rows.append(Row(cols[0], cols[1], int(cols[2]), cols[3], int(cols[4])))
        except ValueError:
            raise PlanError(f"{path} line {number}: expected local, onedrive, size, quickxor, mtime "
                            "separated by TABs.\n  Fix: regenerate the plan with `upcloud review`.") from None
    return rows


def refusal(client, row):
    """Why this row must not be offloaded, or None when everything re-verifies."""
    local = Path(row.local)
    if not local.is_absolute():
        return "path is not absolute; regenerate the plan with `upcloud review`"
    if any(part.startswith("OneDrive") for part in local.parts):
        return "inside a synced OneDrive folder; trashing it would delete the cloud copy"
    if is_sensitive(local.name) or is_sensitive(row.onedrive):
        return "secret or financial name; never offloaded"
    if local.is_symlink():
        return "is a symlink"
    if not local.is_file():
        return "no longer on this Mac"
    stat = local.stat()
    if stat.st_size != row.size or int(stat.st_mtime) != row.mtime:
        return "changed since the plan; run `upcloud review` again"
    item = client.get_item(row.onedrive)
    if item is None or "file" not in item:
        return "not on OneDrive"
    remote_hash = item["file"].get("hashes", {}).get("quickXorHash")
    if item.get("size") != row.size or remote_hash != row.quickxor:
        return "OneDrive copy differs from the plan"
    if quickxor_file(local) != row.quickxor:
        return "local content differs from the plan"
    after = local.stat()
    if (after.st_size, after.st_mtime_ns, after.st_ino) != (stat.st_size, stat.st_mtime_ns, stat.st_ino):
        return "changed while verifying; run `upcloud review` again"
    return None


def trash_path(path):
    """Move path to the macOS Trash (the `trash` command, else Finder). Never deletes."""
    exe, osascript = shutil.which("trash", path="/usr/bin"), shutil.which("osascript", path="/usr/bin")
    if exe:
        cmd = [exe, str(path)]
    elif osascript:
        cmd = [osascript, "-e", "on run argv", "-e",
               "tell application \"Finder\" to delete (POSIX file (item 1 of argv) as alias)",
               "-e", "end run", str(path)]
    else:
        raise TrashError("neither `trash` nor `osascript` found; offload needs macOS.\n"
                         "  Fix: run it on the Mac that holds the files.")
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=TRASH_TIMEOUT_SECONDS)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        raise TrashError(f"could not move {path} to the Trash: {exc}") from exc
    if Path(path).exists() or Path(path).is_symlink():
        raise TrashError(f"{path} is still in place after the Trash call")


def offload(client, rows, apply, report):
    """Verify every row; with apply, Trash the verified ones. Returns (trashed, refused).
    refused is [(row, reason)]; each applied step is appended to the move log."""
    trashed, refused = [], []
    for row in rows:
        reason = refusal(client, row)
        if reason is None and apply:
            try:
                trash_path(row.local)
            except TrashError as exc:
                reason, status = str(exc), "failed"
            else:
                trashed.append(row)
                log_move("offload", src=row.local, onedrive=row.onedrive, size=row.size, status="trashed")
                report("trashed", row, "")
                continue
        elif reason is None:
            trashed.append(row)   # dry run: would be trashed
            report("would trash", row, "")
            continue
        else:
            status = "refused"
        refused.append((row, reason))
        if apply:
            log_move("offload", src=row.local, onedrive=row.onedrive, status=status, detail=reason)
        report("refused", row, reason)
    return trashed, refused
