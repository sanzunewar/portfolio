# Technical Documentation — sanjeevshrestha.info.np

Complete reference for the personal portfolio website: its architecture, how every
part works, how to run and deploy it, and how to maintain it day to day.

- **Live site:** https://sanjeevshrestha.info.np
- **Repository:** https://github.com/sanzunewar/portfolio
- **Owner:** Sanjeev Shrestha

---

## 1. Overview

This is a server-rendered personal portfolio built with Django. It serves the public
pages (home, projects, about) and includes an AI chatbot that answers visitors'
questions. The whole thing runs as a single application on Render, with Cloudflare
providing DNS, HTTPS, and a CDN in front, and a GitHub-based CI/CD pipeline that tests
and deploys automatically on every push.

The design is a dark, infrastructure-themed aesthetic ("Signal") with a network-node
animation in the hero, chosen to reflect a background in network engineering, IT, ISP,
banking, and software.

---

## 2. Technology stack

| Layer | Technology | Notes |
|---|---|---|
| Language | Python 3.12 | |
| Web framework | Django 6.0 | Pages, routing, chatbot endpoint |
| App server | Gunicorn | Runs Django in production |
| Static files | WhiteNoise | Serves CSS/JS with cache-busting hashes |
| Database | SQLite (default) | Ephemeral on Render free tier; no dynamic data is stored yet |
| AI / chatbot | Google Gemini (`gemini-2.5-flash`) | Free tier; called server-side via `google-genai` |
| Hosting | Render (free web service) | Auto-deploys from GitHub |
| DNS / CDN / SSL | Cloudflare (free) | In front of Render |
| CI | GitHub Actions | Lint + tests on every push |
| Domain registrar | Mercantile (register.com.np) | `.info.np` domain |

Python dependencies (see `requirements.txt`): `Django`, `gunicorn`, `whitenoise`,
`dj-database-url`, `python-dotenv`, `google-genai`.

---

## 3. Architecture

The site is a **Django monolith**: one application serves both the HTML pages and the
chatbot API. The request flow is:

```
Browser  →  Cloudflare (DNS, CDN, SSL)  →  Render (Gunicorn + Django)
                                                      │
                                          chatbot call → Google Gemini API
```

For normal page views, Django renders templates and returns HTML. For the chatbot, the
browser sends the visitor's message to a Django endpoint, which calls Gemini
**server-side** and returns the reply as JSON. The AI key never reaches the browser —
this is the core security property of the design.

A key consequence of the free SQLite setup: the database is **ephemeral** on Render's
free tier (it resets on redeploy). This is fine because the public pages and the chatbot
do not write to or read from the database. If dynamic, persistent data is added later,
it should move to a managed Postgres (e.g., Render Postgres, Neon, or Supabase).

---

## 4. Project structure

```
portfolio/
├── manage.py                 # Django command-line entry point
├── requirements.txt          # Python dependencies
├── render.yaml               # Render deployment blueprint (infra as code)
├── pyproject.toml            # Ruff (linter) configuration
├── README.md                 # Quick-start readme
├── .gitignore                # Keeps secrets/artifacts out of git
├── .env.example              # Template for local environment variables
│
├── .github/workflows/
│   └── ci.yml                # GitHub Actions CI pipeline
│
├── config/                   # Project configuration package
│   ├── settings.py           # All settings (env-driven)
│   ├── urls.py               # Top-level URL routing
│   ├── storages.py           # Lenient WhiteNoise static storage class
│   ├── wsgi.py               # Production server entry point
│   └── asgi.py
│
├── portfolio_app/            # The public pages
│   ├── views.py              # home, projects, about views + project data
│   ├── urls.py               # Page routes
│   └── tests.py              # Page tests
│
├── chatbot/                  # The AI assistant
│   ├── views.py              # /api/chat/ endpoint + call_ai_model()
│   ├── urls.py               # Chatbot route
│   └── tests.py              # Endpoint tests
│
├── templates/
│   ├── base.html             # Shared layout, nav, footer, chat widget
│   └── portfolio_app/
│       ├── home.html         # Hero (with network canvas) + featured projects
│       ├── projects.html
│       └── about.html
│
└── static/
    ├── css/style.css         # The "Signal" dark theme
    └── js/
        ├── chat.js           # Chat widget logic (CSRF-protected fetch)
        └── effects.js        # Network-node hero animation + scroll reveals
```

---

## 5. Configuration & environment variables

All configuration is driven by environment variables so the same code runs locally and
in production. Locally these come from a `.env` file; on Render they are set in the
dashboard. Secrets are never committed to git.

| Variable | Purpose | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Cryptographic signing key | (random 50-char string) |
| `DJANGO_DEBUG` | Debug mode — `True` locally, `False` in production | `False` |
| `DJANGO_ALLOWED_HOSTS` | Hostnames allowed to serve the site | `sanjeevshrestha.info.np,www.sanjeevshrestha.info.np` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origins allowed to submit forms/POST | `https://sanjeevshrestha.info.np,https://www.sanjeevshrestha.info.np` |
| `AI_API_KEY` | Google Gemini API key (server-side only) | (secret) |
| `AI_MODEL` | Gemini model name | `gemini-2.5-flash` |

The Render hostname (`*.onrender.com`) is added to `ALLOWED_HOSTS` automatically at
runtime, so the default Render URL also works without extra configuration.

Generate a new secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 6. Local development

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a local .env from the template, then fill in values
cp .env.example .env
#    - set DJANGO_SECRET_KEY (generate one with the command above)
#    - set AI_API_KEY to your Gemini key for local chatbot testing

# 4. Set up the database and run
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000.

---

## 7. The chatbot

The chat widget lives in the bottom-right corner on every page. When a visitor sends a
message, `static/js/chat.js` POSTs it (with the CSRF token) to `/api/chat/`. The view in
`chatbot/views.py` validates the input, calls the AI model server-side, and returns the
reply as JSON.

**Security design:**

- The API key is read from the `AI_API_KEY` environment variable and used only on the
  server — it is never sent to the browser.
- The endpoint accepts POST only and is CSRF-protected.
- Input is validated: empty messages are rejected, and messages are capped at 2000
  characters.
- Provider errors are caught and returned as a generic, friendly message so internal
  details are never leaked.

**Switching or configuring the AI:** the entire provider integration is isolated in one
function, `call_ai_model()`. The current implementation uses Google Gemini:

```python
def call_ai_model(message: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.AI_API_KEY)
    response = client.models.generate_content(
        model=settings.AI_MODEL,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=400,
        ),
    )
    return (response.text or "").strip()
```

To change the chatbot's personality or what it knows, edit `SYSTEM_PROMPT` in the same
file. To switch providers entirely, rewrite only this function; the validation, CSRF,
and error handling around it stay the same.

Gemini's free tier (`gemini-2.5-flash`) allows roughly 250 requests/day, far beyond a
portfolio's needs. `gemini-2.5-flash-lite` allows around 1,000/day if more headroom is
ever wanted.

---

## 8. Frontend & theme ("Signal")

**Design tokens** (defined as CSS variables at the top of `static/css/style.css`):

| Token | Value | Role |
|---|---|---|
| `--bg` / `--bg-2` | `#0A0E1A` / `#0D1322` | Deep slate-navy background gradient |
| `--surface` / `--surface-2` | `#121A2E` / `#16203A` | Cards and panels |
| `--text` / `--muted` | `#E8ECF5` / `#8B96AD` | Text and secondary text |
| `--accent` | `#5B8DEF` | Signal blue (primary accent) |
| `--accent-2` | `#3FC7D4` | Cyan (links, connection hints) |

**Typography:** Space Grotesk (display/headings), Inter (body), JetBrains Mono (labels
and technical captions) — loaded from Google Fonts in `base.html`.

**Signature element:** a subtle, animated network constellation behind the hero — moving
nodes connected by lines when close, evoking network topology. Implemented in
`static/js/effects.js` on a `<canvas>` in the hero.

**Motion:** `effects.js` also reveals each section with a fade-and-rise as it scrolls
into view (via `IntersectionObserver`). Any element with the `reveal` class animates in.
All motion respects `prefers-reduced-motion` — if a visitor's system requests reduced
motion, the constellation does not run and content appears without animation.

**Accessibility floor:** keyboard focus is visible (`:focus-visible` outlines), the
layout is responsive down to mobile, and reduced motion is honored.

---

## 9. CI/CD pipeline

Two layers work together so that pushing code is the only action needed to ship.

**Layer 1 — GitHub Actions** (`.github/workflows/ci.yml`): on every push and pull
request it checks out the code, installs dependencies, lints with Ruff, runs
`collectstatic`, and runs the test suite (`python manage.py test`). This is the quality
gate.

**Layer 2 — Render auto-deploy:** Render watches the connected GitHub branch and
rebuilds + redeploys automatically on every push to `main`, using the build and start
commands defined in `render.yaml`.

The day-to-day result: `git push` → GitHub Actions runs tests → Render rebuilds and goes
live, typically within a couple of minutes.

---

## 10. Deployment (Render)

Deployment is defined declaratively in `render.yaml`:

- **Build:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start:** `gunicorn config.wsgi:application`
- **Plan:** free (upgrade to Starter, ~$7/mo, to remove cold starts)
- **Env vars:** `DJANGO_SECRET_KEY` is generated by Render; `DJANGO_DEBUG`,
  `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, and `AI_MODEL` are set in the
  blueprint; `AI_API_KEY` is marked `sync: false` and must be set manually in the Render
  dashboard (never in git).

To deploy from scratch: push the repo to GitHub, then in Render choose **New → Blueprint**
and select the repo. Render reads `render.yaml` and creates the service. Finally, set
`AI_API_KEY` in the service's **Environment** tab.

---

## 11. Domain, DNS & SSL (Cloudflare)

The domain `sanjeevshrestha.info.np` uses Cloudflare for DNS, with the registrar's
nameservers pointed at Cloudflare.

DNS records (in Cloudflare → DNS → Records):

- `@` → **CNAME** → `portfolio-uz3a.onrender.com` (Cloudflare flattens the apex)
- `www` → **CNAME** → `portfolio-uz3a.onrender.com`

**Setup sequence that matters:** when first connecting the domain, the records are set to
**DNS only (grey cloud)** so Render can verify the domain and issue its SSL certificate.
Once Render shows the domain as verified with a certificate, the records are switched to
**Proxied (orange cloud)** for the CDN and security, and Cloudflare's SSL/TLS mode is set
to **Full** (not Flexible, which would cause a redirect loop).

Django is configured to accept this domain via `DJANGO_ALLOWED_HOSTS` and
`DJANGO_CSRF_TRUSTED_ORIGINS`, so no code change is needed when the domain points at the
app.

---

## 12. Day-to-day workflow

Every change follows the same loop:

```bash
# edit files in VS Code, then:
git add .
git commit -m "describe the change"
git push
```

Render auto-deploys within a minute or two. If a style change doesn't appear, hard-refresh
(Cmd/Ctrl + Shift + R) — WhiteNoise serves hashed filenames so new assets bust the cache
automatically.

**Where to edit common things:**

- **Projects shown on the site:** the `PROJECTS` list in `portfolio_app/views.py`
- **About text / contact:** `templates/portfolio_app/about.html`
- **Hero headline and tagline:** `templates/portfolio_app/home.html`
- **Chatbot personality / facts:** `SYSTEM_PROMPT` in `chatbot/views.py`
- **Colors, fonts, spacing:** the CSS variables at the top of `static/css/style.css`

---

## 13. Testing

```bash
python manage.py test
```

The suite covers the public pages (each returns HTTP 200) and the chatbot endpoint
(method restriction, input validation, missing-key handling, and a successful reply with
the AI call mocked). The same command runs automatically in CI.

---

## 14. Security notes

- Secrets (`DJANGO_SECRET_KEY`, `AI_API_KEY`) live only in environment variables, never in
  code or git. `.gitignore` excludes `.env`.
- When `DJANGO_DEBUG` is `False` (production), Django enables HTTPS redirect, HSTS,
  secure cookies, content-type nosniff, and clickjacking protection. It also trusts
  Render's `X-Forwarded-Proto` header so HTTPS detection works behind the proxy.
- The chatbot key is used server-side only; the browser never sees it.
- The chat endpoint is CSRF-protected and validates/limits input.

---

## 15. Costs

Everything currently runs at no cost:

- **Render** — free web service (sleeps after ~15 min idle; a free uptime monitor such as
  UptimeRobot keeps it warm, or upgrade to ~$7/mo to remove sleeping).
- **Cloudflare** — free plan (DNS, CDN, SSL, DDoS protection).
- **Google Gemini** — free API tier for the chatbot.
- **Domain** — `.info.np` (free/low-cost via the registrar).

---

## 16. Roadmap / planned additions

These are designed but not yet built:

- **Articles / technical writing** — a Markdown-file-based blog (drop a `.md` file in a
  content folder and push; no database needed), with a list page and individual post
  pages.
- **Experience timeline** — a typed career history (network engineering, ISP, banking,
  software roles) rendered from data in `portfolio_app/views.py`.
- **Skills section** — highlighted technologies and areas of expertise.
- **Content polish** — hero, about, projects, and chatbot prompt written around the real
  professional background.

---

## 17. Troubleshooting

- **Git push rejected — "workflow scope":** the GitHub token needs the `workflow` scope to
  push the `.github/workflows/ci.yml` file. Add it to the token (Settings → Developer
  settings → Tokens classic) and push again.
- **Git push 403 — "denied to <other-user>":** an old GitHub login is cached. Clear it
  with `printf "protocol=https\nhost=github.com\n\n" | git credential-osxkeychain erase`,
  then push and authenticate as the correct account.
- **Domain shows the old page:** browser/Cloudflare cache. Try an incognito window or wait
  a few minutes; static assets are hashed so they update automatically.
- **First page load is slow (~30–60s):** Render free-tier cold start after the service
  slept. Use an uptime monitor to keep it warm, or upgrade the plan.
- **Chatbot says "not configured":** `AI_API_KEY` isn't set in Render → Environment.
- **Redirect loop after enabling Cloudflare proxy:** set Cloudflare SSL/TLS mode to
  **Full**, not Flexible.
