# Quick Reference - Email System

## 🚀 Quick Test Commands

```bash
# Start Django server (watch for emails in terminal)
cd /home/zesty/CodeFiles/Django/cinecraft
python manage.py runserver

# Run email test script
python test_email.py

# Create a test profile submission
python manage.py shell
>>> from cineapp.models import DepartmentProfile
>>> profile = DepartmentProfile.objects.create(
...     full_name="Test User",
...     email="test@example.com",
...     department_name="Testing",
...     phone_number="1234567890",
...     years_of_experience=5
... )
```

## 📧 Where Emails Are Sent

| Action | File | Function | Line |
|--------|------|----------|------|
| User submits form | `cineapp/views.py` | `dynamic_form()` | ~85 |
| Admin approves | `admin_frontend/views.py` | `submission_action()` | ~35 |
| Admin rejects | `admin_frontend/views.py` | `submission_action()` | ~60 |

## 🔍 How to Find Email in Console

When you see this in terminal after an action:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Subject: Profile Submission Received - 24 Cine Crafts
From: 24 Cine Crafts <noreply@24cinecrafts.com>
To: user@example.com
Date: ...

[Email body here]
```
**That's the email!** It's working correctly.

## ⚙️ Email Configuration Location

**File**: `cinecraft/settings.py`

**Current (Development)**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = '24 Cine Crafts <noreply@24cinecrafts.com>'
```

**For Production (Gmail)**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = '24 Cine Crafts <your-email@gmail.com>'
```

## 🎯 Common Tasks

### Change Email Sender Name/Address
Edit `cinecraft/settings.py`:
```python
DEFAULT_FROM_EMAIL = 'Your Name <your-email@domain.com>'
```

### Modify Email Content
- **Submission email**: Edit `cineapp/views.py` line ~85
- **Approval email**: Edit `admin_frontend/views.py` line ~35
- **Rejection email**: Edit `admin_frontend/views.py` line ~60

### Add HTML Emails
Replace `send_mail()` with `send_html_mail()` or `EmailMultiAlternatives`

### Test Real SMTP
1. Get Gmail App Password
2. Update settings.py with SMTP config
3. Restart server
4. Submit form - check your actual inbox

## 📚 Documentation Files

- `EMAIL_SETUP.md` - Full setup guide for production
- `EMAIL_IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `test_email.py` - Test script to verify configuration

## 🐛 Troubleshooting Quick Fixes

**No email in console?**
```bash
# Check if EMAIL_BACKEND is set
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
# Should show: django.core.mail.backends.console.EmailBackend
```

**Want to disable emails temporarily?**
```python
# In settings.py, change to dummy backend
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
```

**Want to save emails to files?**
```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-emails'
```

## ✅ Status Check

Run this to verify everything:
```bash
cd /home/zesty/CodeFiles/Django/cinecraft
python test_email.py
```

If you see "✅ Email sent successfully!" - everything is working!
