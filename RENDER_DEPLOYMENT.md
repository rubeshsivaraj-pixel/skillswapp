# Deploying Skillswapp to Render

This guide walks you through deploying your Django application to **Render.com**.

## Prerequisites

1. ✅ GitHub account with your project pushed
2. ✅ Render.com account (free)
3. ✅ All files committed to GitHub

## Step 1: Prepare Your Project

Your project is already configured! The following files have been updated:

- ✅ `settings.py` - Environment-based configuration
- ✅ `requirements.txt` - All dependencies
- ✅ `render.yaml` - Render deployment configuration
- ✅ `.env.example` - Environment variable template
- ✅ `Procfile` - Start command
- ✅ `runtime.txt` - Python version

## Step 2: Generate SECRET_KEY

You need a secure SECRET_KEY for production. Run this command:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output for later use.

## Step 3: Deploy to Render

### Option A: Using render.yaml (Recommended)

1. Commit all changes:
   ```bash
   git add .
   git commit -m "Configure for Render deployment"
   git push origin main
   ```

2. Go to [render.com](https://render.com) and sign in

3. Click **"New +"** → **"Blueprint"**

4. Connect your GitHub repository:
   - Select your GitHub account
   - Choose `skillswapp` repo
   - Confirm connection

5. Render will detect `render.yaml` and create services automatically

6. Set environment variables after deployment

### Option B: Manual Setup (Alternative)

If render.yaml doesn't work, do this manually:

1. **Create Web Service**
   - Dashboard → **New +** → **Web Service**
   - Connect GitHub repo
   - Name: `skillswapp`
   - Region: Choose closest to you
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn peer_skill_swap.wsgi`
   - Plan: **Free** (good for testing)

2. **Create PostgreSQL Database**
   - Dashboard → **New +** → **PostgreSQL**
   - Name: `skillswapp-db`
   - Database: `skillswapp_db`
   - User: `skillswapp_user`
   - Region: Same as web service
   - Plan: **Free**

3. **Connect Web Service to Database**
   - After PostgreSQL is created, copy the **Internal Database URL**
   - Go to Web Service → **Environment**
   - Add environment variable:
     - Key: `DATABASE_URL`
     - Value: Paste the PostgreSQL URL

4. **Add Other Environment Variables**
   - In Web Service Environment, add:
     - `SECRET_KEY`: Your generated secret key
     - `DEBUG`: `False`
     - `ALLOWED_HOSTS`: `skillswapp.onrender.com` (replace with your actual domain)

## Step 4: Configure Environment Variables

Go to Web Service → **Environment** and add:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost
DATABASE_URL=postgresql://... (auto-set if using Render PostgreSQL)
DJANGO_DEBUG=False
```

## Step 5: Run Migrations

After deployment, run migrations on Render:

1. Go to Web Service → **Shell**
2. Run: `python manage.py migrate`
3. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Step 6: Access Your App

Your app will be available at: `https://your-app-name.onrender.com`

To find your domain:
- Go to Render Dashboard
- Click your Web Service
- Check **Settings** for the URL

## Troubleshooting

### Static files not loading?
- Run: `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` in settings.py (should be `staticfiles/`)

### Database connection error?
- Verify `DATABASE_URL` environment variable is set
- Check database is running
- Run migrations: `python manage.py migrate`

### Build failures?
- Check the Render logs for errors
- Ensure all packages in `requirements.txt` are compatible
- Try building locally first: `pip install -r requirements.txt`

### App crashes after deploy?
- Check Web Service logs
- Verify `SECRET_KEY` is set
- Ensure `ALLOWED_HOSTS` includes your domain
- Check database migrations ran successfully

## Useful Commands

### View Logs
```bash
# In Render dashboard, click Web Service → Logs
```

### SSH into App
```bash
# In Render dashboard, click Web Service → Shell
python manage.py shell  # Django shell
python manage.py migrate --noop  # Check migrations
```

### Update Code
Just push to GitHub and Render auto-deploys:
```bash
git add .
git commit -m "Your message"
git push origin main
```

## Environment Variables Reference

```
SECRET_KEY              = Your Django secret key
DEBUG                   = False (production) / True (dev)
ALLOWED_HOSTS           = your-app-name.onrender.com, localhost
DATABASE_URL            = PostgreSQL connection string
DJANGO_DEBUG            = False (production) / True (dev)
```

## Need Help?

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/6.0/howto/deployment/
- Common Issues: Check Render logs in dashboard

---

**Your app is now production-ready! 🚀**
