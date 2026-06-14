# Sanjeev Shrestha — Portfolio

A personal portfolio website built with Django, featuring an AI chatbot that
answers visitors' questions about you. The AI key is kept server-side and never
exposed to the browser. Includes a full CI/CD pipeline (GitHub → Render).

## Stack

- **Django 6** — pages, routing, and the chatbot endpoint
- **Gunicorn + WhiteNoise** — production server and static-file serving
- **Render** — hosting (free tier to start, $7/mo to remove cold starts)
- **GitHub Actions** — runs lint + tests on every push
- **SQLite** by default; swap to Postgres later via `DATABASE_URL`

## Project structure

```
portfolio/
├── config/              # project settings, URLs, WSGI, storage
├── portfolio_app/       # home, projects, about pages
├── chatbot/             # /api/chat/ endpoint (calls the AI server-side)
├── templates/           # HTML templates
├── static/              # CSS + JS (the chat widget lives here)
├── render.yaml          # Render Blueprint (deploy config)
├── .github/workflows/   # CI pipeline
├── requirements.txt
└── .env.example         # copy to .env for local dev
```

## Run it locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your local .env from the template
cp .env.example .env

# 4. Generate a secret key and paste it into .env (DJANGO_SECRET_KEY)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 5. Set up the database and run
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000.

## The chatbot

The widget in the bottom-right corner posts messages to `/api/chat/`. The view
in `chatbot/views.py` calls the AI provider using `AI_API_KEY` from the
environment — the key is never sent to the browser.

- **To enable it:** put a real key in `.env` as `AI_API_KEY=...`. Without a key
  the endpoint returns a friendly "not configured" message.
- **To change the AI's personality:** edit `SYSTEM_PROMPT` in `chatbot/views.py`.
- **To use a different provider:** rewrite only the `call_ai_model` function;
  the validation, CSRF, and error handling around it stay the same.

## Deploy to Render

1. Push this repo to GitHub.
2. On [Render](https://render.com), choose **New → Blueprint** and select your
   repo. Render reads `render.yaml` and creates the service automatically.
3. In the service's **Environment** tab, set `AI_API_KEY` to your real key
   (it is marked `sync: false`, so it must be set in the dashboard, not git).
4. Deploy. Every future `git push` to `main` redeploys automatically.

### Connect your domain (sanjeevshrestha.info.np)

1. In Render, open your service → **Settings → Custom Domains** → add
   `sanjeevshrestha.info.np` (and `www.`).
2. Render gives you a DNS target. At your domain registrar, add the CNAME/A
   records Render shows. HTTPS is provisioned automatically.

## CI/CD pipeline

Two layers work together:

- **GitHub Actions** (`.github/workflows/ci.yml`) runs on every push and pull
  request: it lints with ruff, collects static files, and runs the test suite.
- **Render auto-deploy** rebuilds and ships the site on every push to `main`.

To make deploys happen *only* after tests pass, turn off auto-deploy in Render
and add a final step to the workflow that calls Render's deploy hook.

## A note on the free tier

Render's free web services sleep after ~15 minutes of inactivity, so the first
visitor after a quiet period waits ~30–50 seconds. Two fixes:

- Free: point a free uptime monitor (e.g. UptimeRobot) at your URL to ping it
  every few minutes and keep it warm.
- Paid: upgrade to Render's Starter plan ($7/mo) to remove sleeping entirely.

## Tests

```bash
python manage.py test
```
