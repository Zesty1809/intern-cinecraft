#!/usr/bin/env python
"""
Test script to verify email configuration
Run with: python test_email.py
"""
import os

import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinecraft.settings')
django.setup()

# Import Django modules after setup (required for standalone scripts)
from django.conf import settings  # noqa: E402
from django.core.mail import send_mail  # noqa: E402


def test_email():
    """Test email sending with current configuration"""
    print("=" * 60)
    print("Testing Email Configuration")
    print("=" * 60)
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Test email
    subject = "Test Email - 24 Cine Crafts"
    message = """
This is a test email from 24 Cine Crafts application.

If you're seeing this in the console, the email backend is working!

Application ID: TEST-001
Department: Testing
Status: Success
"""
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['test@example.com']
    
    print("Sending test email...")
    print(f"To: {recipient_list[0]}")
    print(f"Subject: {subject}")
    print()
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
        print()
        if 'console' in settings.EMAIL_BACKEND.lower():
            print("📧 Check the output above for the email content")
            print("   (Console backend prints emails to terminal)")
        else:
            print("📧 Check the recipient inbox")
            print(f"   Backend: {settings.EMAIL_BACKEND}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    test_email()
