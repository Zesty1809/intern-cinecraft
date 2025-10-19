# Email Configuration Guide - 24 Cine Crafts

## Current Setup (Development)

The system is currently configured to use Django's **Console Email Backend** for development. This means:
- Emails are **printed to the terminal/console** where your Django server is running
- No actual emails are sent
- Perfect for development and testing

### How to See Emails During Development

1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. When a user submits a profile or an admin approves/rejects, watch the terminal where the server is running

3. You'll see output like:
   ```
   Content-Type: text/plain; charset="utf-8"
   MIME-Version: 1.0
   Content-Transfer-Encoding: 7bit
   Subject: Profile Submission Received - 24 Cine Crafts
   From: 24 Cine Crafts <noreply@24cinecrafts.com>
   To: user@example.com
   Date: Sun, 19 Oct 2025 10:30:00 -0000
   Message-ID: <...>

   Hello John Doe,
   
   Thank you for submitting your profile...
   ```

## Email Flow

### 1. User Submits Profile
When a user completes and submits their department profile:
- **Immediate**: Confirmation email sent to user's email
- **Contains**: Application ID, Department, Next steps
- **View**: `cineapp/views.py` - `dynamic_form()` function

### 2. Admin Approves/Rejects
When an admin approves or rejects a submission:
- **Immediate**: Status update email sent to user
- **Contains**: Application ID, Status (Approved/Rejected), Next steps
- **View**: `admin_frontend/views.py` - `submission_action()` function

## Production Setup (Real Emails)

To send actual emails in production, you need to configure an SMTP server. Here are the most common options:

### Option 1: Gmail (Recommended for Small Scale)

1. **Get a Gmail App Password**:
   - Go to your Google Account settings
   - Enable 2-Step Verification
   - Go to "App passwords" section
   - Generate an app password for "Mail"
   - Save the 16-character password

2. **Update `settings.py`**:
   ```python
   # Comment out the console backend
   # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

   # Add these settings
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-16-char-app-password'
   DEFAULT_FROM_EMAIL = '24 Cine Crafts <your-email@gmail.com>'
   ```

3. **Important**: Never commit your email password to Git! Use environment variables:
   ```python
   import os
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
   ```

### Option 2: SendGrid (Recommended for Production)

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Get your API key
3. Install: `pip install sendgrid`
4. Update `settings.py`:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.sendgrid.net'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'apikey'
   EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
   DEFAULT_FROM_EMAIL = '24 Cine Crafts <noreply@24cinecrafts.com>'
   ```

### Option 3: AWS SES (Best for Large Scale)

1. Set up AWS SES in your AWS account
2. Verify your domain or email
3. Get SMTP credentials
4. Update `settings.py` with your SES SMTP settings

## Testing Emails

### Test in Development (Console)
1. Start server: `python manage.py runserver`
2. Submit a profile form
3. Check the terminal for email output

### Test with Real SMTP
1. Configure Gmail or SendGrid as shown above
2. Submit a profile form
3. Check your inbox (and spam folder)

## Email Templates

### Current Email Content

**Profile Submission Email** (sent when user submits):
- Application ID
- Department name
- Next steps (review process)
- Timeline (2-3 business days)
- Contact reminders

**Approval Email** (sent when admin approves):
- Congratulations message
- Application ID
- Access information
- Next steps

**Rejection Email** (sent when admin rejects):
- Application ID
- Resubmission option
- Contact information

## Troubleshooting

### Emails not appearing in console
- Make sure `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` is in settings.py
- Check you're looking at the correct terminal window (where `runserver` is active)
- Look for any error messages in the console

### Emails not sending with SMTP
- Verify your SMTP credentials are correct
- Check firewall settings (port 587 or 465 must be open)
- For Gmail: ensure "Less secure app access" is ON or use App Password
- Check spam folder
- Look for error messages in Django console

### Common Errors
- `SMTPAuthenticationError`: Wrong username/password
- `SMTPServerDisconnected`: Wrong host or port
- `gaierror`: Network connection issue

## Security Best Practices

1. **Never commit credentials**: Use environment variables
2. **Use App Passwords**: Don't use your main email password
3. **Rate limiting**: Consider adding rate limits for email sending
4. **Email validation**: Validate email formats before sending
5. **Unsubscribe option**: Add unsubscribe links for marketing emails

## Current Files with Email Logic

- `cinecraft/settings.py`: Email configuration
- `cineapp/views.py`: User submission email (line ~85)
- `admin_frontend/views.py`: Admin approval/rejection emails (line ~30)
- `cinecraft/templates/success.html`: Success page showing email confirmation

## Next Steps for Production

1. ✅ Email configuration is ready (console backend for dev)
2. ⚠️ Before going live: Configure real SMTP (Gmail/SendGrid/SES)
3. ⚠️ Set up environment variables for credentials
4. ⚠️ Test with real emails in staging environment
5. ⚠️ Set up email monitoring/logging
6. ⚠️ Consider HTML email templates for better design

## Support

For email-related issues:
- Check Django docs: https://docs.djangoproject.com/en/5.2/topics/email/
- Gmail SMTP: https://support.google.com/mail/answer/7126229
- SendGrid: https://docs.sendgrid.com/for-developers
