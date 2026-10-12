# Deploying AgroSmart

| Part | Where | Cost |
|---|---|---|
| Website (`Web/`) | [Vercel](https://vercel.com) | Free (Hobby) |
| Backend API (`crop_recommendation/`) | [Hugging Face Spaces](https://huggingface.co/spaces), Docker | Free (CPU basic) |
| Database and uploaded photos | [Supabase](https://supabase.com) | Free tier |

Do the steps in this order. Each part needs an address from the one before it.

---

## 1. Supabase: database and photo storage

1. **Create a project** at [supabase.com](https://supabase.com/dashboard).
   - Pick a region in the US East. Hugging Face runs Spaces mainly in the US, and the API talks to the database many times per page, so keeping them close keeps the site fast.
   - Save the database password somewhere safe.
2. **Database connection string.**
   - Click **Connect** at the top of the project and choose **Session pooler** (not "Direct connection": that one only works over IPv6, which Hugging Face does not have).
   - Copy the URI and replace `[YOUR-PASSWORD]` with your database password. It looks like this:
     ```
     postgresql://postgres.abcdefghijkl:PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres
     ```
   - This is your `DATABASE_URL`.
3. **Storage bucket for photos.**
   - Open **Storage → New bucket**, name it `media`, and switch **Public bucket** on. Listing photos and post thumbnails must be viewable by everyone.
4. **Storage access keys.**
   - Open **Storage → Settings → S3 Connection** and make sure the connection is enabled.
   - Note the **Region**, e.g. `us-east-1`.
   - Under **S3 Access Keys**, click **New access key** and copy the **Access key ID** and the **Secret access key**. The secret is shown only once.
5. **Project ref.** This is the id in your project URL, `https://<project-ref>.supabase.co`, and also appears under **Project Settings → General**.

---

## 2. Hugging Face Space: backend API

1. **Create the Space** at [huggingface.co/new-space](https://huggingface.co/new-space):
   - **Name:** e.g. `agrosmart-api`. The API address becomes `https://<your-username>-agrosmart-api.hf.space`.
   - **SDK:** Docker, Blank template.
   - **Hardware:** CPU basic (free).
   - **Visibility:** Public. The website calls the API from visitors' browsers, which cannot log in to a private Space.
2. **Add two files** to the Space: **Files → Add file → Upload files**. Upload both files from `deploy/huggingface/` in this repo:
   - `Dockerfile`
   - `README.md` (replace the default one; its header tells Hugging Face to use Docker on port 7860)

   The Space doesn't hold the code. When it builds, it downloads the code and models from GitHub.
3. **Settings → Variables and secrets.**

   Add these as **Secrets** (hidden):

   | Name | Value |
   |---|---|
   | `SECRET_KEY` | A new random key for production (see below) |
   | `DATABASE_URL` | The Supabase session pooler URI from step 1.2 |
   | `GROQ_API_KEY`, `GOOGLE_API_KEY`, `OPENWEATHER_API_KEY`, `ISDA_API_KEY` | Same values as your local `crop_recommendation/.env` |
   | `SUPABASE_S3_ACCESS_KEY_ID`, `SUPABASE_S3_SECRET_ACCESS_KEY` | From step 1.4 |
   | `DJANGO_SUPERUSER_PASSWORD` | Password for the admin account |
   | `GOOGLE_OAUTH_CLIENT_SECRET`, `FACEBOOK_APP_SECRET` | Only if you use social login |

   Make a new secret key on your computer:
   ```bash
   crop_recommendation/venv/bin/python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
   ```

   Add these as **Variables** (visible):

   | Name | Value |
   |---|---|
   | `DEBUG` | `False` |
   | `BACKEND_URL` | `https://<your-username>-agrosmart-api.hf.space` |
   | `FRONTEND_URLS` | Your Vercel address, e.g. `https://agrosmart.vercel.app` (fill in after step 3; use `http://localhost:5173` until then) |
   | `SUPABASE_PROJECT_REF` | From step 1.5 |
   | `SUPABASE_STORAGE_BUCKET` | `media` |
   | `SUPABASE_S3_REGION` | From step 1.4, e.g. `us-east-1` |
   | `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` | Admin account name and email |
   | `GOOGLE_OAUTH_CLIENT_ID`, `FACEBOOK_APP_ID` | Only if you use social login |
4. **Wait for the build.** The first build takes about 10–15 minutes, mostly installing TensorFlow; watch the **Logs** tab.
   - When the status turns **Running**, open `https://<your-username>-agrosmart-api.hf.space/api/prices/`. You should see a list of crop prices.
   - The prices are downloaded in the background on first start, so give it a minute.
   - The admin is at `/admin/`.

**What happens on each start:** database migrations run, the admin account is created if it's missing, and market prices refresh in the background if they're more than 30 days old. Hugging Face has no scheduled jobs, so this replaces the monthly `refresh_prices` cron.

**Deploying a new version:** push your changes to GitHub `main`, then click **Settings → Factory rebuild** in the Space.

**Sleeping:** free Spaces go to sleep after 48 hours without visits. The next visit wakes the Space up, which takes 1–3 minutes, so open the API before a demo.

---

## 3. Vercel: website

1. **Import the project.** At [vercel.com/new](https://vercel.com/new), import the GitHub repo `Agrosmart`.
   - **Root Directory:** `Web`
   - **Framework preset:** Vite (detected automatically; `Web/vercel.json` also sets it)
2. **Environment variable:** add `VITE_API_URL` = `https://<your-username>-agrosmart-api.hf.space` (no slash at the end).
3. **Deploy.**
4. **Turn on Git LFS.** Open **Settings → Git**, switch **Git LFS** on, then go to **Deployments → ⋯ → Redeploy**. The landing-page video is stored with Git LFS; without this, it is a broken placeholder.
5. **Connect the API to the site.** Copy your site's address (e.g. `https://agrosmart.vercel.app`) into the Space variable `FRONTEND_URLS`, then restart the Space (**Settings → Restart this Space**).
   - Until you do this, the browser blocks the website's calls to the API (a CORS error in the console).
   - To also allow Vercel preview deployments, add a `FRONTEND_URL_REGEX` variable such as `^https://agrosmart-.*\.vercel\.app$`.

---

## 4. After deploying

- **Demo data:** the Space has no terminal on the free tier, so run management commands from your computer against Supabase:
  ```bash
  cd crop_recommendation
  DATABASE_URL='postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres' \
    venv/bin/python manage.py seed_demo
  ```
  The same works for `refresh_prices` or `createsuperuser`.
- **Google / Facebook login:** add the Vercel address to the authorised JavaScript origins (Google Cloud Console) and to the app domains (Facebook).
- **Check the site:**
  - pages load after a refresh (e.g. `/marketplace`)
  - you can register and log in
  - an uploaded listing photo appears (its address should start with `https://<project-ref>.supabase.co/storage/…`)
  - the chatbot types its answers
  - crop recommendations and disease detection work

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Bad Request (400)` from the API | The address isn't in `ALLOWED_HOSTS`. Check `BACKEND_URL`, or add the host to an `ALLOWED_HOSTS` variable |
| CORS error in the browser console | The site's address isn't in `FRONTEND_URLS` (exact match, `https://`, no trailing slash). Restart the Space after changing it |
| Space log: `could not translate host name` or `Network is unreachable` for the database | You used Supabase's direct connection. Use the **Session pooler** string |
| Photos upload but don't show | The `media` bucket isn't **Public** |
| Space crashes with "Memory limit exceeded" | Set `WEB_WORKERS=1` |
| Landing video missing | Git LFS isn't enabled in the Vercel project; enable it and redeploy |

## Running the backend image yourself

The same image runs anywhere Docker does, for example Render, Railway or Google Cloud Run (give it at least 2 GB of memory):

```bash
cd crop_recommendation
git lfs pull
docker build -t agrosmart-api .
docker run -p 7860:7860 --env-file .env agrosmart-api
```
