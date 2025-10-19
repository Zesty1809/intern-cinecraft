import random
import string

import pyotp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DepartmentProfileForm
from .models import DepartmentProfile, TOTPDevice


# Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        # Create the user (only inside POST)
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True  # Ensure user is active on registration
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    # GET or other methods: render registration form
    return render(request, 'register.html')

# Login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login')


        # If the account is staff/superuser, route them to the Django admin instead
        if user_obj.is_staff or user_obj.is_superuser:
            messages.info(request, "Please use the Django Admin to sign in as an administrator.")
            return redirect('/admin/login/?next=/admin/')

        # Prevent login if user is inactive
        if not user_obj.is_active:
            messages.error(request, "Your account has been deactivated. Please contact support or the administrator.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid email or password.")
        return redirect('login')

    return render(request, 'login.html')


def _generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def request_otp_view(request):
    """Step 1: user submits email to request an OTP for login."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found for that email.")
            return redirect('login')

        if user.is_staff or user.is_superuser:
            messages.info(request, "Please use the Django Admin to sign in as an administrator.")
            return redirect('/admin/login/?next=/admin/')

        if not user.is_active:
            messages.error(request, "Your account has been deactivated.")
            return redirect('login')

        # ensure user has a TOTPDevice
        device, created = TOTPDevice.objects.get_or_create(user=user, defaults={
            'secret': pyotp.random_base32()
        })

        # rate-limit: allow max 6 sends per hour
        now = timezone.now()
        if device.last_send_count_reset and (now - device.last_send_count_reset).total_seconds() > 3600:
            device.reset_send_counts()

        if device.send_count_hour >= 6:
            messages.error(request, "Too many OTP requests. Please try again later.")
            return redirect('login')

        device.increment_send()

        totp = pyotp.TOTP(device.secret)
        code = totp.now()

        # send email with OTP
        try:
            send_mail(
                'Your CineCraft login code',
                f'Your one-time login code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        request.session['otp_user_id'] = user.id
        messages.success(request, "OTP sent to your email. Please enter the code to continue.")
        return redirect('verify_otp')
    return redirect('login')


def verify_otp_view(request):
    """Step 2: verify the OTP and log the user in."""
    if request.method == 'POST':
        user_id = request.session.get('otp_user_id')
        code = request.POST.get('code', '').strip()
        if not user_id:
            messages.error(request, "Session expired. Please request a new code.")
            return redirect('login')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Invalid session. Please request a new code.")
            return redirect('login')

        # check TOTP and record failed attempts if necessary
        device = getattr(user, 'totp_device', None)
        if not device:
            messages.error(request, "No OTP device found for this account. Request a new code.")
            return redirect('login')

        if device.locked_until and device.locked_until > timezone.now():
            messages.error(request, "Account temporarily locked due to repeated failed attempts. Try later.")
            return redirect('login')

        totp = pyotp.TOTP(device.secret)
        if not totp.verify(code, valid_window=1):
            device.record_failed_attempt()
            messages.error(request, "Invalid or expired code.")
            return redirect('verify_otp')

        # success - reset counters and log in
        device.reset_attempts()
        login(request, user)
        request.session.pop('otp_user_id', None)
        messages.success(request, "Logged in successfully.")
        return redirect('dashboard')

    return render(request, 'verify_otp.html')

# Dashboard
@login_required(login_url='login')
def dashboard_view(request):
    # Prevent staff/superusers from using the front-end dashboard
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, "Admin users should use the Django Admin dashboard.")
        return redirect('/admin/')
    # Get all department drafts for the current user
    drafts = DepartmentProfile.objects.filter(user=request.user, approval_status='draft')
    draft_list = [
        {
            'department_name': d.department_name,
            'created_at': d.created_at,
            'application_id': d.application_id,
        }
        for d in drafts
    ]

    # Get all submitted (non-draft) profiles for the user
    submitted_profiles = DepartmentProfile.objects.filter(
        user=request.user,
        approval_status__in=['pending', 'approved', 'rejected', 'inactive']
    ).order_by('-created_at')

    submitted_list = [
        {
            'department_name': p.department_name,
            'approval_status': p.approval_status,
            'created_at': p.created_at,
            'application_id': p.application_id,
        }
        for p in submitted_profiles
    ]

    return render(request, 'dashboard.html', {
        'user': request.user,
        'drafts': draft_list,
        'submitted_profiles': submitted_list,
    })

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# Submit department profile
@login_required(login_url='login')
def dynamic_form(request, department_name):
    if request.method == "POST":
        is_draft = request.POST.get('action') == 'save_draft'
        # If saving a draft, try to load existing draft for this user+department
        instance = None
        if is_draft:
            try:
                instance = DepartmentProfile.objects.filter(
                    user=request.user,
                    department_name=department_name,
                    approval_status='draft'
                ).order_by('-created_at').first()
            except Exception:
                instance = None
        form = DepartmentProfileForm(request.POST, request.FILES, draft=is_draft, instance=instance)
        if form.is_valid():
            # ENFORCE: Only one pending/active form per department per user
            if not is_draft:
                existing = DepartmentProfile.objects.filter(
                    user=request.user,
                    department_name=department_name,
                    approval_status__in=['pending', 'approved']
                ).exclude(id=getattr(instance, 'id', None)).first()
                if existing:
                    messages.error(request, "You already have a pending or active submission for this department. You can only submit again if your previous application is rejected or inactive.")
                    form.fields["email"].initial = request.user.email
                    return render(request, "dynamic_form.html", {"form": form, "department_name": department_name.capitalize()})

            profile = form.save(commit=False)
            profile.department_name = department_name
            profile.user = request.user
            profile.email = request.user.email  # supply value server-side
            profile.save()
            
            # Send confirmation email
            try:
                subject = "Profile Submission Received - 24 Cine Crafts"
                message = f"""
Hello {profile.full_name},

Thank you for submitting your profile to 24 Cine Crafts!

Your {profile.department_name} profile has been received and is now under review.

Application Details:
- Application ID: {profile.application_id}
- Department: {profile.department_name}
- Submitted: {profile.created_at.strftime('%B %d, %Y')}

What happens next?
1. Our team will review your submission and verify the provided details
2. You'll receive a confirmation within 2-3 business days at this email
3. Once approved, your profile will be visible to industry professionals

Important reminders:
• Check your inbox and spam folder for updates
• Review typically takes 2-3 business days
• Keep your contact information up to date

If you have any questions, please don't hesitate to contact us.

Best regards,
The 24 Cine Crafts Team
                """
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [profile.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            if is_draft:
                messages.success(request, "Draft saved successfully. You can resume it anytime from the same department form.")
                return redirect('dynamic_form', department_name=department_name)
            else:
                return redirect("success_page", application_id=profile.application_id)
        else:
            # make the email show again after a failed POST (since the field is disabled)
            form.fields["email"].initial = request.user.email
    else:
        # Prefill with existing draft if available for this user and department
        instance = DepartmentProfile.objects.filter(
            user=request.user,
            department_name=department_name,
            approval_status='draft'
        ).order_by('-created_at').first()
        if instance:
            form = DepartmentProfileForm(instance=instance, initial={"email": request.user.email}, draft=True)
        else:
            form = DepartmentProfileForm(initial={"email": request.user.email})

    return render(
        request,
        "dynamic_form.html",
        {"form": form, "department_name": department_name.capitalize()},
    )

@login_required(login_url='login')
def success_page(request, application_id):
    profile = get_object_or_404(
        DepartmentProfile,
        application_id=application_id,
        user=request.user   # only the owner can view
    )
    return render(request, "success.html", {"profile": profile})