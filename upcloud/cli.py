"""upcloud: sign in, list and mirror a personal OneDrive from the terminal."""
# REUSE_CHECKED: wraps upcloud/config.py and onedrive_client.py; no other OneDrive CLI in _dev repos
import argparse
import sys

EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_AUTH, EXIT_NOT_FOUND = 0, 1, 2, 3, 4
EXIT_INTERRUPTED = 130

EPILOG = """examples:
  upcloud login        sign in once; the token refreshes itself

exit codes: 0 ok, 1 error, 2 usage, 3 sign-in needed, 4 not found"""


def err(msg):
    print(msg, file=sys.stderr)


def cmd_login(args):
    from .config import Config, get_new_token
    get_new_token()
    print(f"Signed in. Token cached at {Config.CACHED_TOKEN_PATH} (mode 600); it refreshes itself.")
    return EXIT_OK


def build_parser():
    p = argparse.ArgumentParser(prog="upcloud", description=__doc__, epilog=EPILOG,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", metavar="<command>")
    login = sub.add_parser("login", help="sign in with your Microsoft account (opens a browser)")
    login.set_defaults(func=cmd_login)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return EXIT_OK
    from .config import AuthRequired, load_env
    load_env()
    try:
        return args.func(args)
    except AuthRequired as e:
        err(f"Error: {e}\n  Fix: check CLIENT_ID in .env, then run `upcloud login`.")
        return EXIT_AUTH
    except KeyboardInterrupt:
        err("Interrupted.")
        return EXIT_INTERRUPTED


def run():
    sys.exit(main())
