# Deploying Peer Skill Swap Platform

This guide explains how to deploy the Django Peer Skill Swap Platform online using a cloud platform like Render or Heroku.

## Prerequisites

1.  A GitHub repository containing your project code.
2.  An account on Render or Heroku.
3.  A PostgreSQL database (offered as an add-on by these cloud providers).

## Steps Required

### 1. Secure the project using environment variables
Never upload your `SECRET_KEY` or database credentials to GitHub.
- Install `python-dotenv` or `dj-database-url`.
    ```bash
    pip install python-dotenv dj-database-url
    ```
- In `settings.py`, load variables from the environment:
    ```python
    import os
    import dj_database_url
    
    # Load SECRET_KEY safely
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-unsafe-secret-key-for-local')
    
    # Set DEBUG based on environment
    DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'False'
    
    # Allowed hosts
    ALLOWED_HOSTS = ['your-app-domain.herokuapp.com', 'your-app-name.onrender.com', 'localhost', '127.0.0.1']
    ```

### 2. Configure PostgreSQL database
Replace your default SQLite configuration with `dj_database_url` to parse the `DATABASE_URL` environment variable:
```python
# settings.py
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///' + str(BASE_DIR / 'db.sqlite3')),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```
*Note: Make sure to install `psycopg2-binary` to allow Django to talk to PostgreSQL.*
```bash
pip install psycopg2-binary
```

### 3. Set up static files
Cloud platforms don't serve static files directly like the local development server does. We need `WhiteNoise` for serving static assets.
1. Install WhiteNoise:
   ```bash
   pip install whitenoise
   ```
2. Add it to `MIDDLEWARE` in `settings.py` (right after `SecurityMiddleware`):
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware', # Add this line
       # ...
   ]
   ```
3. Set up static file locations:
   ```python
   STATIC_URL = 'static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   # Avoid finding non-existent dirs in production
   # STATICFILES_DIRS = [BASE_DIR / "static"]
   ```

### 4. Use Gunicorn
Django’s built-in `runserver` is not suitable for production. We must use a WSGI HTTP Server like Gunicorn.
1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```
2. Freeze your dependencies into a `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

### 5. Deploy on a Cloud Platform

#### Heroku
1. Create a `Procfile` at the root of your project:
   ```Procfile
   web: gunicorn peer_skill_swap.wsgi
   ```
2. Login using Heroku CLI and create a new project.
3. Add a PostgreSQL add-on to your Heroku app.
4. Set the `SECRET_KEY` environment variable in Heroku Settings.
5. Disable `COLLECTSTATIC` temporarily during the first build if needed:
   ```bash
   heroku config:set DISABLE_COLLECTSTATIC=1
   ```
6. Push to Heroku: `git push heroku main`
7. Run migrations on Heroku: `heroku run python manage.py migrate`

#### Render
1. In your Render dashboard, create a new "Web Service" linked to your GitHub repo.
2. Set the Build Command:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
3. Set the Start Command:
   ```bash
   gunicorn peer_skill_swap.wsgi
   ```
4. Create a "PostgreSQL" service on Render, get the Internal Database URL, and add it to your Web Service's Environment Variables as `DATABASE_URL`.
5. Add your `SECRET_KEY` and set `DJANGO_DEBUG` to `False`.
6. Deploy!
