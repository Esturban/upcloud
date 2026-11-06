# Upcloud

Sign in, list, mirror, tidy and free disk space with a personal OneDrive from the terminal, through Microsoft Graph.
Every verb that changes something is a dry run unless you add `--apply`, and nothing is ever hard-deleted.

## Install

```sh
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/pip install -e .        # adds the `upcloud` command to venv/bin
```

`python -m upcloud` works too, with no install step.

## Azure app registration (once)

upcloud signs in through your own Azure app. Do this once, then only renew the secret.

1. Open https://portal.azure.com, then **Microsoft Entra ID > App registrations > New registration**.
2. Supported account types: **Personal Microsoft accounts only** (the `consumers` endpoints).
3. Redirect URI: platform **Web**, value `http://localhost:8080`.
4. **API permissions > Add > Microsoft Graph > Delegated**: `Files.ReadWrite`, `offline_access`.
5. Copy the **Application (client) ID** into `CLIENT_ID=` in `.env`.

### Client secret (new, or expired)

`AADSTS7000222` on `upcloud login` means the secret expired.

1. Open the app's Credentials page:
   `https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Credentials/appId/<CLIENT_ID>`
   (wrong directory? top right, **Switch directory**).
2. **Client secrets > New client secret**, expiry 24 months, **Add**.
3. Copy the **Value** column at once (it shows only once; not the Secret ID).
4. Paste it into `AZURE_VALUE=` in `.env`. Never in chat, a commit or a log.
5. Run `upcloud login && upcloud ls`. Delete the expired secret in the portal.

## Configure

Put these keys in a `.env` file at the repo root. Never commit it.

| Key | Meaning |
|-----|---------|
| `CLIENT_ID` | Azure app (client) id |
| `AZURE_VALUE` | client secret, if the app has one |
| `REDIRECT_URI` or `AZURE_REDIRECT_URI` | default `http://localhost:8080` |
| `AUTHORITY_URL`, `TOKEN_URL` | default: the `consumers` endpoints (personal accounts) |
| `SCOPES` | default `https://graph.microsoft.com/.default offline_access`; `offline_access` is always added |
| `CACHED_TOKEN_PATH` | token cache file, relative to the `.env` folder; written with mode 600 |
| `SOURCE_FOLDER`, `TARGET_FOLDER` | fallback folders for `mirror`, used only when there is no roots file |
| `RECURSIVE` | `true` (default for `mirror`) or `false` |

`UPCLOUD_ENV_FILE` points at another `.env`.

### Roots file

`~/.config/upcloud/roots.tsv` says which local folder lives where on OneDrive. One pair per line,
local folder, a TAB, OneDrive folder. `#` starts a comment. Local folders are absolute or start with `~`.

```text
# local_dir<TAB>onedrive_dir
~/Pictures	Pictures
~/Documents/work	Work
```

`UPCLOUD_ROOTS` points at another file. `UPCLOUD_MOVE_LOG` overrides the move log path.

## Usage

```sh
upcloud login                       # opens the Microsoft sign-in page once
upcloud ls                          # list the OneDrive root
upcloud ls datasets                 # list a folder
upcloud mirror                      # plan every root in roots.tsv; changes nothing
upcloud mirror ~/Pictures           # one folder; its OneDrive folder comes from roots.tsv
upcloud mirror ~/Pictures --apply   # upload new and changed files
upcloud mirror ./data datasets/data # an explicit pair, no roots file needed
upcloud mv Inbox/scan.pdf Work/2024/ --apply          # move into a folder (trailing /)
upcloud sort-by-year Pictures/Phone                   # plan; add --apply to move
upcloud review --days 180           # what is safe to remove from this Mac; writes plan.tsv
upcloud offload plan.tsv            # re-verify every row; add --apply to move to the Trash
```

### How `mirror` decides

| Line | Meaning |
|------|---------|
| `upload` | missing on OneDrive, or a different size, or a different quickXorHash |
| `skip` | same size, and same quickXorHash when OneDrive reports one (counted, not printed) |
| `extra` | only on OneDrive; listed, never deleted |

Without `--apply`, `mirror` only prints the plan. Missing OneDrive folders are created.
Uploads run 8 at a time. A failed file does not stop the run; re-run the same command to
retry, and unchanged files are skipped.

### `mv SRC DST`

Moves or renames inside OneDrive. `DST` is the new full path; end it with `/` to move into that
folder and keep the name. Missing parent folders are created on `--apply`. It refuses to overwrite
an existing item and to move a folder into itself.

### `sort-by-year PATH`

Plans moving the loose files of one OneDrive folder into its existing `YYYY/` subfolders. The year
is `photo.takenDateTime`, else the file's created date. It never creates a folder; a file with no
matching year folder, no date, or a name clash in the year folder is skipped and listed with the reason.
Not recursive.

### `review` and `offload`

`review [--days 180] [--out plan.tsv]` goes through every root and keeps the files whose OneDrive
copy has the same size and quickXorHash, and that were not opened or modified on the Mac in N days.
It prints GB per root and writes the plan. It changes nothing.

`offload plan.tsv` re-verifies every row (file still there, unchanged since the plan, OneDrive copy
still identical, hash recomputed), then with `--apply` moves the Mac file to the macOS Trash (`trash`,
else Finder). Rows that fail are refused and listed; the rest continue. Empty the Trash yourself.

Never uploaded or offloaded, whatever the plan says: `.env*`, `*.pem`, `*.key`, and any file or
folder whose name contains `token`, `tax`, `bank`, `invoice` or `statement`.

Every applied `mv`, `sort-by-year` and `offload` step is appended to
`~/.local/share/upcloud/moves.jsonl` (one JSON line each: time, verb, paths, status).

The token refreshes itself 5 minutes before it expires. If it cannot, commands stop
with exit code 3 and ask you to run `upcloud login`.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | ok |
| 1 | error (for example `mv` would overwrite, or a move failed) |
| 2 | usage (for example, no roots file and no SRC and DST, or a malformed plan.tsv) |
| 3 | sign-in needed |
| 4 | not found |
| 5 | some uploads, moves or offload rows failed or were refused |

## Legacy script

`python -m upcloud.upcloud` still uploads `SOURCE_FOLDER` to `TARGET_FOLDER`, now every
file by default (set `GLOB=*.csv` to narrow it). It skips files that already exist by name.

## Tests

```sh
venv/bin/python -m pytest -q
```

All HTTP is mocked; tests never call Microsoft and never read `.env`.
