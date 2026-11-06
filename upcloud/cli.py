"""upcloud: sign in, list, mirror, tidy and offload a personal OneDrive from the terminal."""
# REUSE_CHECKED: wraps upcloud/config.py and onedrive_client.py; no other OneDrive CLI in _dev repos
import argparse
import os
import sys
from pathlib import PurePosixPath

EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_AUTH, EXIT_NOT_FOUND, EXIT_PARTIAL = 0, 1, 2, 3, 4, 5
EXIT_INTERRUPTED = 130

EPILOG = """examples:
  upcloud login        sign in once; the token refreshes itself
  upcloud ls datasets  list a OneDrive folder (no PATH: the root)
  upcloud mirror       plan every root in ~/.config/upcloud/roots.tsv (changes nothing)
  upcloud mirror ~/Pictures --apply   upload new and changed files of one root
  upcloud mv a/f.pdf b/ --apply       move inside OneDrive (never overwrites)
  upcloud sort-by-year Pictures       file loose files into existing YYYY/ folders
  upcloud review                      what is safe to remove from this Mac (writes plan.tsv)
  upcloud offload plan.tsv --apply    re-verify, then move those files to the Trash

changing commands are a dry run unless --apply; nothing is ever hard-deleted.
exit codes: 0 ok, 1 error, 2 usage, 3 sign-in needed, 4 not found, 5 some items failed or were refused"""


def err(msg):
    print(msg, file=sys.stderr)


def cmd_login(args):
    from .config import Config, get_new_token
    get_new_token()
    print(f"Signed in. Token cached at {Config.CACHED_TOKEN_PATH} (mode 600); it refreshes itself.")
    return EXIT_OK


def human(n):
    n = float(n or 0)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def make_client():
    from .config import get_access_token
    from .onedrive_client import OneDriveClient
    return OneDriveClient(get_access_token(interactive=False))


def cmd_ls(args):
    for item in make_client().list_children(args.path):
        name = item["name"] + ("/" if "folder" in item else "")
        modified = item.get("lastModifiedDateTime", "")[:10]
        print(f"{human(item.get('size')):>10}  {modified:<10}  {name}")
    return EXIT_OK


def _mirror_pairs(args):
    """[(local, onedrive)] to mirror: explicit pair, PATH via the roots file, every root, or .env."""
    from .roots import load_roots, resolve
    if args.src and args.dst is not None:
        return [(args.src, args.dst)]
    roots = load_roots()
    if args.src:
        from pathlib import Path
        base = Path(args.src).expanduser()
        dst = resolve(base.parent if base.is_file() else base)
        if dst is None and not roots:
            dst = os.getenv("TARGET_FOLDER")
        return [(args.src, dst)] if dst is not None else []
    if roots:
        return [(str(r.local), r.onedrive) for r in roots]
    src, dst = os.getenv("SOURCE_FOLDER"), os.getenv("TARGET_FOLDER")
    return [(src, dst)] if src and dst is not None else []


def _mirror_one(client, src, dst, apply, recursive):
    from .mirror import apply_plan, plan_mirror
    actions = plan_mirror(client, src, dst, recursive)
    counts = {k: sum(a.kind == k for a in actions) for k in ("upload", "skip", "extra", "newer")}
    for a in actions:
        if a.kind != "skip":
            print(f"{a.kind:<8} {a.rel}  ({a.reason}, {human(a.size)})")
    print(f"{src} -> OneDrive:{dst or '/'}: {counts['upload']} to upload, "
          f"{counts['skip']} unchanged, {counts['extra']} only on OneDrive, "
          f"{counts['newer']} newer on OneDrive (left alone).")
    if not apply:
        return EXIT_OK

    def report(event, rel, detail=""):
        if event == "failed":
            err(f"failed   {rel}: {detail}")

    result = apply_plan(client, dst, actions, report=report)
    print(f"Done: {len(result.uploaded)} uploaded, {len(result.failed)} failed.")
    return EXIT_PARTIAL if result.failed else EXIT_OK


def cmd_mirror(args):
    pairs = _mirror_pairs(args)
    if not pairs:
        err("Error: mirror has no folder pair.\n"
            "  Fix: pass SRC and DST, add the folder to ~/.config/upcloud/roots.tsv "
            "(local_dir TAB onedrive_dir), or set SOURCE_FOLDER and TARGET_FOLDER in .env.")
        return EXIT_USAGE
    recursive = os.getenv("RECURSIVE", "true").strip().lower() in ("1", "true", "t", "yes")
    client = make_client()
    code = EXIT_OK
    for src, dst in pairs:
        try:
            code = max(code, _mirror_one(client, src, dst, args.apply, recursive))
        except FileNotFoundError as e:
            err(f"Error: {e}\n  Fix: check the local folder in roots.tsv, or mount the drive.")
            code = max(code, EXIT_NOT_FOUND)
    if not args.apply:
        print("Dry run: nothing changed. Add --apply to upload.")
    elif code == EXIT_PARTIAL:
        err("Re-run the same command to retry; unchanged files are skipped.")
    return code


def cmd_mv(args):
    from .organize import apply_mv, missing_parent, plan_mv
    client = make_client()
    move = plan_mv(client, args.src, args.dst)
    parent = missing_parent(client, move)
    print(f"{move.src} -> {move.dst}")
    if parent:
        print(f"  would create folder {parent}")
    if not args.apply:
        print("Dry run: nothing changed. Add --apply to move.")
        return EXIT_OK
    done, failed = apply_mv(client, move)
    for m, why in failed:
        err(f"failed   {m.src}: {why}")
    return EXIT_ERROR if failed else EXIT_OK


def cmd_sort_by_year(args):
    from .organize import apply_moves, plan_sort_by_year
    client = make_client()
    moves = plan_sort_by_year(client, args.path)
    for m in moves:
        if m.kind == "move":
            print(f"move     {PurePosixPath(m.src).name} -> {PurePosixPath(m.dst).parent.name}/")
        else:
            print(f"skip     {PurePosixPath(m.src).name}  ({m.reason})")
    todo = sum(m.kind == "move" for m in moves)
    print(f"{args.path}: {todo} to move, {len(moves) - todo} skipped.")
    if not args.apply:
        print("Dry run: nothing changed. Add --apply to move.")
        return EXIT_OK
    done, failed = apply_moves(client, moves, "sort-by-year",
                               report=lambda ev, m, why="": err(f"failed   {m.src}: {why}") if ev == "failed" else None)
    print(f"Done: {len(done)} moved, {len(failed)} failed.")
    return EXIT_PARTIAL if failed else EXIT_OK


def _gb(n):
    return f"{n / 1024 ** 3:.1f} GB"


def cmd_review(args):
    from .offload import review_root, write_plan
    from .roots import load_roots
    roots = load_roots()
    if not roots:
        err("Error: review needs roots.\n"
            "  Fix: add `local_dir<TAB>onedrive_dir` lines to ~/.config/upcloud/roots.tsv.")
        return EXIT_USAGE
    client, code, plan = make_client(), EXIT_OK, []
    for root in roots:
        try:
            rows = review_root(client, root, args.days)
        except FileNotFoundError as e:
            err(f"Error: {e}\n  Fix: check the local folder in roots.tsv, or mount the drive.")
            code = EXIT_NOT_FOUND
            continue
        plan.extend(rows)
        print(f"{root.local} -> OneDrive:{root.onedrive}: {len(rows)} files, {_gb(sum(r.size for r in rows))} "
              f"identical on OneDrive and untouched for {args.days} days")
    write_plan(plan, args.out)
    print(f"Total {len(plan)} files, {_gb(sum(r.size for r in plan))}. Plan written to {args.out}.\n"
          f"Next: `upcloud offload {args.out}` (dry run), then add --apply to move them to the Trash.")
    return code


def cmd_offload(args):
    from .offload import PlanError, offload, read_plan
    try:
        rows = read_plan(args.plan)
    except PlanError as e:
        err(f"Error: {e}")
        return EXIT_USAGE

    def report(event, row, detail):
        if event == "refused":
            err(f"refused  {row.local}: {detail}")
        else:
            print(f"{event:<8} {row.local}  ({human(row.size)})")

    ok, refused = offload(make_client(), rows, args.apply, report)
    verb = "moved to the Trash" if args.apply else "would move to the Trash"
    print(f"{len(ok)} {verb} ({_gb(sum(r.size for r in ok))}), {len(refused)} refused.")
    if not args.apply:
        print("Dry run: nothing changed. Add --apply to move the files to the Trash.")
    return EXIT_PARTIAL if refused else EXIT_OK


def build_parser():
    p = argparse.ArgumentParser(prog="upcloud", description=__doc__, epilog=EPILOG,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", metavar="<command>")
    login = sub.add_parser("login", help="sign in with your Microsoft account (opens a browser)")
    login.set_defaults(func=cmd_login)
    ls = sub.add_parser("ls", help="list a OneDrive folder")
    ls.add_argument("path", nargs="?", default="", help="OneDrive folder (default: root)")
    ls.set_defaults(func=cmd_ls)
    mirror = sub.add_parser("mirror", help="upload new and changed files from SRC to DST (dry run unless --apply)")
    mirror.add_argument("src", nargs="?", help="local folder (default: every root in roots.tsv)")
    mirror.add_argument("dst", nargs="?", help="OneDrive folder (default: looked up in roots.tsv)")
    mirror.add_argument("--apply", action="store_true", help="upload; without it nothing changes")
    mirror.set_defaults(func=cmd_mirror)
    mv = sub.add_parser("mv", help="move or rename inside OneDrive; never overwrites (dry run unless --apply)")
    mv.add_argument("src", help="OneDrive path to move")
    mv.add_argument("dst", help="new OneDrive path; end it with / to move into that folder")
    mv.add_argument("--apply", action="store_true", help="move; without it nothing changes")
    mv.set_defaults(func=cmd_mv)
    sort = sub.add_parser("sort-by-year", help="file loose files into the folder's existing YYYY/ subfolders")
    sort.add_argument("path", help="OneDrive folder with YYYY/ subfolders")
    sort.add_argument("--apply", action="store_true", help="move; without it nothing changes")
    sort.set_defaults(func=cmd_sort_by_year)
    review = sub.add_parser("review", help="find local files already safe on OneDrive and untouched (writes plan.tsv)")
    review.add_argument("--days", type=int, default=180, help="untouched for this many days (default 180)")
    review.add_argument("--out", default="plan.tsv", help="plan file to write (default ./plan.tsv)")
    review.set_defaults(func=cmd_review)
    off = sub.add_parser("offload", help="re-verify plan.tsv rows, then move the Mac files to the Trash (dry run unless --apply)")
    off.add_argument("plan", help="plan.tsv from `upcloud review`")
    off.add_argument("--apply", action="store_true", help="move to the Trash; without it nothing changes")
    off.set_defaults(func=cmd_offload)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return EXIT_OK
    from requests import HTTPError
    from .config import AuthRequired, load_env
    from .organize import MoveRefused
    from .roots import RootsError
    load_env()
    try:
        return args.func(args)
    except AuthRequired as e:
        err(f"Error: {e}\n  Fix: check CLIENT_ID in .env, then run `upcloud login`.")
        return EXIT_AUTH
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status == 404:
            err(f"Error: not found on OneDrive: {getattr(args, 'path', '') or e.request.url}\n"
                "  Fix: check the path with `upcloud ls <parent>`.")
            return EXIT_NOT_FOUND
        if status in (401, 403):
            err(f"Error: OneDrive refused the request ({status}).\n  Fix: run `upcloud login`.")
            return EXIT_AUTH
        err(f"Error: OneDrive request failed: {e}")
        return EXIT_ERROR
    except RootsError as e:
        err(f"Error: {e}")
        return EXIT_USAGE
    except MoveRefused as e:
        err(f"Error: {e}")
        return EXIT_ERROR
    except FileNotFoundError as e:
        err(f"Error: {e}")
        return EXIT_NOT_FOUND
    except KeyboardInterrupt:
        err("Interrupted. Re-run the same command; finished files are skipped.")
        return EXIT_INTERRUPTED


def run():
    sys.exit(main())
