# NaijaKet — Deploy Runbook (Railway)

## 0. Local environment

Django 4.2 **breaks on Python 3.14** (`'super' object has no attribute 'dicts'` on any
template using an inclusion tag). Use 3.13.

```bash
py -3.13 -m venv .venv313
.\.venv313\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Point the editor's interpreter at `.venv313\Scripts\python.exe` — not system Python,
which has no deps installed.

> **PowerShell gotcha:** never build files with `>` or `Out-File` (writes UTF-16, which
> pip and Django can't parse). Use the tool's own `-o` flag, e.g.
> `python manage.py dumpdata ... -o file.json`.

## 1. Files that make the deploy work

| File | Purpose |
|---|---|
| `.python-version` | `3.13` — pins the builder's Python. **Without this the 3.14 bug returns in production.** |
| `railway.json` | Builder, `collectstatic` build step, `migrate` + gunicorn start command |
| `Procfile` | Fallback start command |
| `nixpacks.toml` | Build config |
| `.env.example` | Reference for required env vars (no real values) |

Start command (in `railway.json`):

```
python manage.py migrate --noinput && gunicorn project.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

New deploy files are **untracked** — `git commit -a` silently skips them. Always
`git add` them explicitly and verify:

```bash
git ls-tree -r origin/main --name-only | grep -E "python-version|railway.json|Procfile"
```

## 2. Railway setup

1. **New Project → Deploy from GitHub repo →** `nonzoo/NaijaKet`
2. **New → Database → PostgreSQL** — injects `DATABASE_URL` itself; never paste it
3. **Variables** on the *web* service:
   ```
   SECRET_KEY=<generated>
   DEBUG=False
   ALLOWED_HOSTS=naijaket.up.railway.app
   EMAIL_HOST_PASSWORD=<outlook password>
   ```
4. **Settings → Networking → Generate Domain**

Set `ALLOWED_HOSTS` explicitly. Relying on Railway's auto-injected
`RAILWAY_PUBLIC_DOMAIN` fails if the container booted before the domain existed.

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 3. Shelling into the container

```bash
railway service          # pick the WEB service, not Postgres
railway ssh
source /opt/venv/bin/activate
```

Two traps, both of which look like unrelated errors:

- **Wrong service.** If you see `docker-entrypoint-initdb.d` and no `/app`, you're in
  the Postgres container. Symptoms: `python: command not found`, missing files.
- **Venv not active.** Right container (`/app`, `manage.py` present) but bare `python`
  is the system interpreter → `ModuleNotFoundError: No module named 'django'`.
  Use `/opt/venv/bin/python` or `source /opt/venv/bin/activate`.

Then:

```bash
python manage.py createsuperuser
```

Use an **interactive** `railway ssh` for `createsuperuser` — it needs a real TTY for the
password prompts. `railway ssh <command>` won't do.

First connection prompts for host key trust; answer `yes`, or pre-seed it:

```bash
ssh-keyscan -t ed25519 ssh.railway.com >> ~/.ssh/known_hosts
```

## 4. Moving reference data to production

Dump locally (SQLite), commit, redeploy, then load in the container:

```bash
python manage.py dumpdata store.Category store.Subcategory --indent 2 -o categories.json
```

```bash
railway ssh
source /opt/venv/bin/activate && python manage.py loaddata categories.json
```

The fixture must be **committed and deployed** — `railway ssh` runs inside the image,
so an uncommitted file isn't there. FK ordering is handled (one transaction, deferred
constraints), and `loaddata` resets Postgres ID sequences afterward, so admin-created
rows won't collide.

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Bad Request (400)`, plain white page | `DisallowedHost` — domain not in `ALLOWED_HOSTS` | Set the `ALLOWED_HOSTS` variable, redeploy |
| 404 right after generating the domain | Edge not wired up yet | Wait / redeploy |
| CSRF failure on login only | `CSRF_TRUSTED_ORIGINS` missing the scheme | Derives from `ALLOWED_HOSTS`; fix that |
| `'super' object has no attribute 'dicts'` | Python 3.14 + Django 4.2 | Confirm `.python-version` deployed; log should say `Using Python 3.13` |
| CSS missing, HTML fine | `collectstatic` didn't run / whitenoise | Check build log for `N static files copied` |
| Uploaded images vanish after deploy | Ephemeral container filesystem | Needs Cloudinary (below) |

Healthy deploy log:

```
Using Python 3.13
N static files copied
Applying store.0042_... OK
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8080
```

Add `--access-logfile -` to the gunicorn command to get request logs — it turns
guesswork like the 400 above into one visible line.

## 6. Still outstanding

- **Cloudinary for media.** Admin uploads currently die on every redeploy. Local
  `media/uploads/*` is gitignored, so migrated `Product` rows point at files that don't
  exist in production until images are re-uploaded through Cloudinary.
- **Django 4.2 reached end of life in April 2026.** Unsupported for security patches;
  plan an upgrade separately from deploys.
