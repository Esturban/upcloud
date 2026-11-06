"""Names upcloud never uploads or offloads: secrets and financial records."""
from fnmatch import fnmatchcase
from pathlib import PurePosixPath

PATTERNS = (".env*", "*.pem", "*.key", "*token*", "*tax*", "*bank*", "*invoice*", "*statement*")


def is_sensitive(path):
    """True if the file name or any folder above it (posix style, relative) matches PATTERNS."""
    parts = PurePosixPath(str(path).replace("\\", "/")).parts
    return any(fnmatchcase(part.lower(), pat) for part in parts for pat in PATTERNS)
