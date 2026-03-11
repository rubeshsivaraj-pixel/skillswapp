# Setup Instructions

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/rubeshsivaraj-pixel/skillswapp.git
cd skillswapp
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# Mac/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your local settings
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

## Production Deployment

### For Heroku:
1. Install Heroku CLI
2. `heroku login`
3. `heroku create your-app-name`
4. `heroku addons:create heroku-postgresql:hobby-dev`
5. Set config vars: `heroku config:set SECRET_KEY=your-secret-key`
6. `git push heroku main`
7. `heroku run python manage.py migrate`

### For Render:
1. Connect GitHub repo to Render
2. Create Web Service
3. Set Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. Set Start Command: `gunicorn peer_skill_swap.wsgi`
5. Add PostgreSQL database and set DATABASE_URL
6. Deploy!

## Running Tests
```bash
python manage.py test
```

## Collecting Static Files (Production)
```bash
python manage.py collectstatic --noinput
```
