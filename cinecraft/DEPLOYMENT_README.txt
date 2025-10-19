# 24 Cine Crafts - Deployment Instructions

## Quick Setup Guide

This package contains a ready-to-deploy Django project. Follow these steps to set it up on your machine.

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

#### 1. Unzip the Package
```bash
unzip cinecraft_deployment_*.zip
cd cinecraft
```

#### 2. Create Virtual Environment
**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install Django==5.2.7
pip install Pillow
```

#### 4. Run Database Migrations
```bash
python manage.py migrate
```

#### 5. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

#### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### 7. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

### Default URLs
- **Homepage/Login**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Dashboard**: http://127.0.0.1:8000/dashboard/

### Project Structure
```
cinecraft/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3               # SQLite database (if included)
├── cinecraft/               # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── cineapp/                 # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Form definitions
│   └── urls.py              # URL routing
├── admin_frontend/          # Admin interface
├── static/                  # Static files (CSS, JS)
└── templates/               # HTML templates
```

### Features
- User registration and authentication
- Department profile forms (24 cinema crafts)
- Draft save functionality
- Admin dashboard for profile management
- Status tracking (pending, approved, rejected)

### Creating Sample Users (Optional)
If you want to create sample profiles for testing:
```bash
python manage.py create_sample_profiles
```

### Troubleshooting

**Issue: "No module named 'django'"**
- Make sure your virtual environment is activated
- Run: `pip install -r requirements.txt`

**Issue: "django.db.utils.OperationalError"**
- Run migrations: `python manage.py migrate`

**Issue: Static files not loading**
- Run: `python manage.py collectstatic`
- Check STATIC_ROOT in settings.py

**Issue: Permission denied**
- Linux/Mac: Make sure you have execute permissions
- Run: `chmod +x manage.py`

### Production Deployment

For production deployment, you should:
1. Set `DEBUG = False` in `cinecraft/settings.py`
2. Set proper `ALLOWED_HOSTS` in settings.py
3. Use a production-grade database (PostgreSQL, MySQL)
4. Use a proper web server (Gunicorn, uWSGI)
5. Set up a reverse proxy (Nginx, Apache)
6. Use environment variables for sensitive settings
7. Enable HTTPS/SSL

### Support
For issues or questions, refer to the Django documentation:
https://docs.djangoproject.com/

---
**Project**: 24 Cine Crafts
**Version**: 1.0
**Django Version**: 5.2.7
