from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DepartmentProfileForm
from .models import DepartmentProfile


# Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

    user = User.objects.create_user(username=username, email=email, password=password)
    user.is_active = True  # Ensure user is active on registration
    user.save()
    messages.success(request, "Account created successfully! Please log in.")
    return redirect('login')

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