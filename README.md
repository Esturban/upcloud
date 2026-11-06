# Upcloud

Sign in, list and mirror a personal OneDrive from the terminal, through Microsoft Graph.

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
| `SOURCE_FOLDER`, `TARGET_FOLDER` | default local and OneDrive folders for `mirror` |
| `RECURSIVE` | `true` (default for `mirror`) or `false` |

`UPCLOUD_ENV_FILE` points at another `.env`.

## Usage

```sh
upcloud login                       # opens the Microsoft sign-in page once
upcloud ls                          # list the OneDrive root
upcloud ls datasets                 # list a folder
upcloud mirror                      # plan SOURCE_FOLDER -> TARGET_FOLDER; changes nothing
upcloud mirror ./data datasets/data # plan an explicit pair
upcloud mirror ./data datasets/data --apply   # upload new and changed files
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

The token refreshes itself 5 minutes before it expires. If it cannot, commands stop
with exit code 3 and ask you to run `upcloud login`.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | ok |
| 1 | error |
| 2 | usage (for example, mirror without SRC and DST) |
| 3 | sign-in needed |
| 4 | not found |
| 5 | some uploads failed |

## Legacy script

`python -m upcloud.upcloud` still uploads `SOURCE_FOLDER` to `TARGET_FOLDER`, now every
file by default (set `GLOB=*.csv` to narrow it). It skips files that already exist by name.

## Tests

```sh
venv/bin/python -m pytest -q
```

All HTTP is mocked; tests never call Microsoft and never read `.env`.
