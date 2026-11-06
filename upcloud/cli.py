"""upcloud: sign in, list and mirror a personal OneDrive from the terminal."""
# REUSE_CHECKED: wraps upcloud/config.py and onedrive_client.py; no other OneDrive CLI in _dev repos
import argparse
import os
import sys

EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_AUTH, EXIT_NOT_FOUND, EXIT_PARTIAL = 0, 1, 2, 3, 4, 5
EXIT_INTERRUPTED = 130

EPILOG = """examples:
  upcloud login        sign in once; the token refreshes itself
  upcloud ls datasets  list a OneDrive folder (no PATH: the root)
  upcloud mirror       plan SOURCE_FOLDER -> TARGET_FOLDER from .env (changes nothing)
  upcloud mirror ./data datasets/data --apply   upload new and changed files

exit codes: 0 ok, 1 error, 2 usage, 3 sign-in needed, 4 not found, 5 some uploads failed"""


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


def cmd_mirror(args):
    from .mirror import apply_plan, plan_mirror
    src = args.src or os.getenv("SOURCE_FOLDER")
    dst = args.dst if args.dst is not None else os.getenv("TARGET_FOLDER")
    if not src or dst is None:
        err("Error: mirror needs SRC and DST.\n"
            "  Fix: pass them, or set SOURCE_FOLDER and TARGET_FOLDER in .env.")
        return EXIT_USAGE
    recursive = os.getenv("RECURSIVE", "true").strip().lower() in ("1", "true", "t", "yes")
    client = make_client()
    actions = plan_mirror(client, src, dst, recursive)
    counts = {k: sum(a.kind == k for a in actions) for k in ("upload", "skip", "extra")}
    for a in actions:
        if a.kind != "skip":
            print(f"{a.kind:<8} {a.rel}  ({a.reason}, {human(a.size)})")
    summary = f"{src} -> OneDrive:{dst or '/'}: {counts['upload']} to upload, " \
              f"{counts['skip']} unchanged, {counts['extra']} only on OneDrive."
    if not args.apply:
        print(f"{summary}\nDry run: nothing changed. Add --apply to upload.")
        return EXIT_OK
    print(summary)

    def report(event, rel, detail=""):
        if event == "failed":
            err(f"failed   {rel}: {detail}")

    result = apply_plan(client, dst, actions, report=report)
    print(f"Done: {len(result.uploaded)} uploaded, {len(result.failed)} failed.")
    if result.failed:
        err("Re-run the same command to retry; unchanged files are skipped.")
        return EXIT_PARTIAL
    return EXIT_OK


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
    mirror.add_argument("src", nargs="?", help="local folder (default: SOURCE_FOLDER)")
    mirror.add_argument("dst", nargs="?", help="OneDrive folder (default: TARGET_FOLDER)")
    mirror.add_argument("--apply", action="store_true", help="upload; without it nothing changes")
    mirror.set_defaults(func=cmd_mirror)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return EXIT_OK
    from requests import HTTPError
    from .config import AuthRequired, load_env
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
    except FileNotFoundError as e:
        err(f"Error: {e}")
        return EXIT_NOT_FOUND
    except KeyboardInterrupt:
        err("Interrupted. Re-run the same command; finished files are skipped.")
        return EXIT_INTERRUPTED


def run():
    sys.exit(main())
