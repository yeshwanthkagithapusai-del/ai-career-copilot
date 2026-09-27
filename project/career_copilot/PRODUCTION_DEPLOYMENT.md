# Deploying AI Career Copilot to Production

This guide covers deploying AI Career Copilot to a Platform-as-a-Service (PaaS) like **Render**, **Railway**, or **Heroku**.

## 1. Prerequisites

You will need accounts for the following services:
- **PaaS Provider** (e.g., [Render.com](https://render.com))
- **PostgreSQL Database** (Can be provisioned via Render or [Supabase](https://supabase.com))
- **OpenAI API Key** ([Platform.openai.com](https://platform.openai.com))

---

## 2. Environment Variables

Before deploying, prepare the following environment variables. Do **NOT** commit these to your repository.

### Security
- `SECRET_KEY`: A 50+ character random string. (You can generate one via `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG`: Must be `False` in production.
- `ALLOWED_HOSTS`: Your production domain names separated by commas (e.g., `yourdomain.com,www.yourdomain.com,your-app.onrender.com`).
- `CSRF_TRUSTED_ORIGINS`: Your production URLs separated by commas (e.g., `https://yourdomain.com,https://your-app.onrender.com`). **CRITICAL**: Include `https://` in these.

### Database
- `DATABASE_URL`: Your PostgreSQL connection string (e.g., `postgresql://user:password@host:port/dbname`).

### AI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key starting with `sk-`.
- `OPENAI_MODEL`: Set to `gpt-4o-mini` (or whichever model you prefer).

### Email
Configure these if you are sending real emails (password resets, notifications):
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS` (typically `True`)

---

## 3. Deployment Configuration (Render Example)

Render natively supports Django. You can deploy it as a **Web Service**.

1. Connect your GitHub repository to Render.
2. Select **New Web Service** and choose the repository.
3. Use the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn career_copilot.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
4. Add the **Environment Variables** listed in Step 2.

### CRITICAL: Persistent Disk (Media Files)
AI Career Copilot accepts **PDF/DOCX Resume Uploads**. These are saved to the `media/` directory.

Since PaaS providers use ephemeral containers, your `media/` folder will be **wiped** every time you deploy an update or the server restarts.
To prevent this data loss on Render:
1. Go to the **Disks** section of your Web Service configuration.
2. Click **Add Disk**.
3. Set the Mount Path to `/opt/render/project/src/project/career_copilot/media` (or simply `media` relative to your Django root).
4. Size: `1 GB` (or more as needed).

*(Note: If you plan to scale horizontally to multiple servers, you will need to replace `FileSystemStorage` with `django-storages` and AWS S3. Local Disks do not sync across horizontal web instances).*

---

## 4. Zero-Downtime Health Checks

AI Career Copilot includes a dedicated `/health/` endpoint.
- In your PaaS Health Check settings, set the **Health Check Path** to `/health/`.
- The platform will not route traffic to the container until this endpoint returns a `200 OK`.

---

## 5. Superuser Creation

Once the application is successfully deployed and running, you will need an admin account to access `/admin/`.

Access your PaaS provider's **Shell** or **Console** for the running Web Service and run:
```bash
python manage.py createsuperuser
```
Follow the prompts to set up your email and password.

---

## 6. Verifying Deployment

1. Visit `https://your-app-domain.com/health/` -> Should return `{"status": "ok"}`
2. Visit `https://your-app-domain.com/` -> Should load the landing page and have HTTPS enforced automatically.
3. Register a test account.
4. Upload a test Resume to verify the Persistent Disk and AI integration are functioning properly.

**Congratulations, AI Career Copilot is live!**
