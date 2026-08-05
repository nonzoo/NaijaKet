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

> **PowerShell gotcha:** never build files with `>` or `Out-File` without `-Encoding utf8`
> — the default writes UTF-16, which pip and Django can't parse. Prefer the tool's own
> flag, e.g. `python manage.py dumpdata ... -o file.json`.
>
> This already happened once: `pip freeze > requirements.txt` produced a UTF-16 file.
> Regenerate with:
> ```bash
> .\.venv313\Scripts\python.exe -m pip freeze | Out-File -Encoding utf8 requirements.txt
> ```

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
2. **New → Database → PostgreSQL**
3. **Variables** on the *web* service:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   SECRET_KEY=<generated>
   DEBUG=False
   ALLOWED_HOSTS=naijaket.up.railway.app
   CLOUDINARY_URL=cloudinary://<key>:<secret>@<cloud_name>
   EMAIL_HOST_PASSWORD=<outlook password>
   ```
4. **Settings → Networking → Generate Domain**

### `DATABASE_URL` is not automatic — this is the big one

Adding a Postgres service does **not** give the web service `DATABASE_URL`. Variables are
per-service. You must add the reference `${{Postgres.DATABASE_URL}}` yourself (the name
before the dot must match the database service exactly).

Miss it and `settings.py` falls back to SQLite **silently**, inside a container whose disk
is wiped every deploy — so **all data disappears on every push**. Use the `${{...}}`
reference rather than pasting the connection string, so credential rotation doesn't break it.

Verify:

```bash
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])"
```

Want `django.db.backends.postgresql`. Second check: the next deploy log should say
**`No migrations to apply`**. If it replays old migrations, the DB is still ephemeral.

### `ALLOWED_HOSTS`

Set it explicitly. Relying on Railway's auto-injected `RAILWAY_PUBLIC_DOMAIN` fails when the
container booted before the domain existed. Comma-separated, no scheme, no trailing slash.

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

Two traps, both of which surface as misleading errors:

- **Wrong service.** If you see `docker-entrypoint-initdb.d` and no `/app`, you're in the
  Postgres container. Symptoms: `python: command not found`, missing files.
- **Venv not active.** Right container (`/app`, `manage.py` present) but bare `python` is the
  system interpreter → `ModuleNotFoundError: No module named 'django'`.
  Use `/opt/venv/bin/python` or `source /opt/venv/bin/activate`.

Use an **interactive** `railway ssh` for `createsuperuser` — it needs a real TTY for the
password prompts. `railway ssh <command>` won't do.

First connection prompts for host key trust; answer `yes`, or pre-seed it:

```bash
ssh-keyscan -t ed25519 ssh.railway.com >> ~/.ssh/known_hosts
```

## 4. Moving reference data to production

Dump locally (SQLite), commit, redeploy, then load in the container.

```bash
python manage.py dumpdata store.Category store.Subcategory --indent 2 -o categories.json
python manage.py dumpdata userprofile.State --indent 2 -o states.json
```

Current fixtures: `categories.json` (9 categories + 106 subcategories),
`states.json` (37 — 36 states + FCT).

```bash
railway ssh
source /opt/venv/bin/activate && python manage.py loaddata categories.json states.json
python manage.py createsuperuser
```

The fixture must be **committed and deployed** — `railway ssh` runs inside the image, so an
uncommitted file isn't there. FK ordering is handled (one transaction, deferred constraints),
and `loaddata` resets Postgres ID sequences afterward, so admin-created rows won't collide.

**Do this only after `DATABASE_URL` is confirmed working**, or it all lands in throwaway SQLite.

## 5. Static vs media — keep them separate

| | Served by | Use for |
|---|---|---|
| `/static/` | whitenoise, from `collectstatic` | CSS, JS, logo, icons — anything shipped with the code |
| `/media/` | Cloudinary | user uploads: product images, profile pics, video |

With `DEBUG=False` Django serves **neither** by itself. A site asset referenced as
`/media/uploads/logo.png` 404s in production — that's why the logo vanished. It belongs in
`static/`, referenced with the template tag:

```django
{% load static %}
<img src="{% static 'images/logo.png' %}" alt="logo" />
```

Always `{% static %}`, never a hardcoded `/static/...` path: the staticfiles backend is a
**manifest** storage, so files get content-hashed names (`logo.4f2a9c.png`) in production. A
hardcoded path works locally and 404s live. The tag also gives cache-busting for free.

> With manifest storage, if `collectstatic` fails during build, `{% static %}` raises
> `ValueError` at render time and **every page 500s**. Confirm `N static files copied` in the
> build log.

### Cloudinary (media)

Code is already wired — no changes needed:

- `INSTALLED_APPS` has `cloudinary_storage` + `cloudinary`, listed **after**
  `django.contrib.staticfiles` (before it would override `collectstatic`)
- `settings.py` swaps `STORAGES["default"]` to `MediaCloudinaryStorage` when `CLOUDINARY_URL`
  is present
- `store/models.py` `video_storage()` returns `VideoMediaCloudinaryStorage` — video needs a
  separate backend; the image one rejects it

Setup: sign up at cloudinary.com → Dashboard → **API Environment variable** → copy the
`cloudinary://key:secret@cloud_name` string → set as `CLOUDINARY_URL` in Railway.

Verify:

```bash
python manage.py shell -c "from django.core.files.storage import storages; print(storages['default'].__class__.__name__)"
```

Want `MediaCloudinaryStorage`. Then upload a product image in the admin and confirm the URL
is `res.cloudinary.com/...`.

**Existing images won't appear.** Rows already in the DB point at paths never uploaded to
Cloudinary, and local `media/uploads/*` is gitignored. Re-upload through the admin, or write a
one-off command that uploads with `public_id` matching the stored path.

Leave `CLOUDINARY_URL` out of local `.env` and uploads stay on disk — no quota burned in dev.

## 6. SSL and custom domain (Namecheap)

SSL is free and automatic — Let's Encrypt, auto-renewing, on both `*.up.railway.app` and
custom domains. Already handled in `settings.py`:

```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Railway terminates TLS at the edge
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in ALLOWED_HOSTS ...]
```

Steps:

1. Railway → **Settings → Networking → Custom Domain** → enter `www.naijaket.com`, copy the
   CNAME target (`xyz123.up.railway.app`)
2. Namecheap → **Domain List → Manage → Advanced DNS**
3. **Delete the default parking records first** — `CNAME www → parkingpage.namecheap.com` and
   the `URL Redirect @`. A duplicate `www` CNAME silently conflicts and the cert never issues.
4. **Add New Record → CNAME Record** — Host `www`, Value = the target, TTL Automatic.
   If rejected, retry with a trailing dot.
5. **Apex** (`naijaket.com`): Namecheap BasicDNS has no ALIAS/ANAME, so add a
   **URL Redirect Record** — Host `@`, Value `https://www.naijaket.com`, **Permanent (301)**,
   *Unmasked*. Masked serves the site in a hidden frame and breaks CSRF, cookies, and SEO.
6. **Domain tab → Nameservers** must read **Namecheap BasicDNS**, or Advanced DNS is ignored.
7. Add the domain to `ALLOWED_HOSTS` in Railway:
   ```
   ALLOWED_HOSTS=naijaket.up.railway.app,www.naijaket.com
   ```

Verify:

```bash
nslookup www.naijaket.com
curl -I https://www.naijaket.com
```

Want `HTTP/2 200` or a 302, no cert warning. Propagation is ~5–30 min. A `400` here means DNS
and SSL are fine and only step 7 is missing.

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| **Data wiped on every push** | `DATABASE_URL` missing → silent SQLite fallback on ephemeral disk | Add `DATABASE_URL=${{Postgres.DATABASE_URL}}` |
| Old migrations replay every deploy | Same as above | Same as above |
| `Bad Request (400)`, plain white page | `DisallowedHost` — domain not in `ALLOWED_HOSTS` | Set the variable, redeploy |
| 404 right after generating the domain | Edge not wired up yet | Wait / redeploy |
| CSRF failure on login only | `CSRF_TRUSTED_ORIGINS` missing the scheme | Derives from `ALLOWED_HOSTS`; fix that |
| `'super' object has no attribute 'dicts'` | Python 3.14 + Django 4.2 | Confirm `.python-version` deployed; log should say `Using Python 3.13` |
| CSS missing, HTML fine | `collectstatic` didn't run / whitenoise | Check build log for `N static files copied` |
| Every page 500s after a static change | manifest storage + failed `collectstatic` | Fix the build step |
| Logo/icon 404s but CSS works | Asset referenced under `/media/` | Move to `static/`, use `{% static %}` |
| Uploaded images vanish after deploy | `CLOUDINARY_URL` not set | Set it; verify storage class |
| `python: command not found` over SSH | Wrong service (Postgres) | `railway service` → pick web |
| `No module named 'django'` over SSH | Venv not active | `source /opt/venv/bin/activate` |

Healthy deploy log:

```
Using Python 3.13
N static files copied
No migrations to apply
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8080
```

Add `--access-logfile -` to the gunicorn command for request logs — it turns guesswork like
the 400 above into one visible line.

## 8. Outstanding

- **`requirements.txt` is UTF-16 locally** and pins `Django==4.2.1` on `origin/main`.
  Regenerate as UTF-8 and bump to `4.2.25` — 4.2.1 has known CVEs.
- **Fail loudly on missing `DATABASE_URL`.** Raise `ImproperlyConfigured` when `DEBUG=False`
  and it's absent, instead of silently serving a disposable SQLite database.
- **`SECURE_SSL_REDIRECT = True`** behind the `if not DEBUG` guard, once the domain is stable.
- **Backfill existing media to Cloudinary** — see §5.
- **Django 4.2 reached end of life in April 2026.** Plan an upgrade separately from deploys.
