from collections import defaultdict

from django.apps import apps
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST


@staff_member_required
def admin_overview(request):
    """
    Renders the custom admin dashboard (overview.html) with:
    - recent_items: newest submissions globally (Overview tab)
    - submissions_by_department: grouped, each department recent-first (Submission tab)
    """
    DepartmentProfile = apps.get_model("cineapp", "DepartmentProfile")
    if DepartmentProfile is None:
        return render(request, "admin_frontend/overview.html", {
            "recent_items": [],
            "submissions_by_department": [],
            "stats": {"total_submissions": 0, "pending_review": 0, "approved": 0, "active_users": 0},
            "site_title": "Overview",
        })

    # Choose a reliable ordering field
    order_field = "-created_at" if hasattr(DepartmentProfile, "created_at") else "-id"

    # Base queryset: newest first
    qs = DepartmentProfile.objects.all().order_by(order_field)

    # Stats (adjust if you already compute elsewhere)
    stats = {
        "total_submissions": qs.count(),
        "pending_review": qs.filter(approval_status="pending").count(),
        "approved": qs.filter(approval_status__in=["approved", "active"]).count(),
        "active_users": qs.filter(approval_status__in=["approved", "active"]).count(),
    }

    # Overview tab: latest N global submissions
    recent_items = qs[:10]

    # Submission tab: group rows by department, each group recent-first
    grouped = defaultdict(list)
    for s in qs:
        dept = getattr(s, "department_name", "Unknown")
        grouped[dept].append({
            "obj_pk": s.pk,
            "status_key": getattr(s, "approval_status", "unknown") or "unknown",
            "status_label": (getattr(s, "approval_status", "unknown") or "unknown").capitalize(),
            "name": getattr(s, "full_name", "") or getattr(s, "name", ""),
            "contact": getattr(s, "phone_number", "") or getattr(s, "email", ""),
            "join_date": getattr(s, "created_at", None),
            "experience": getattr(s, "years_of_experience", None),
            "craft": getattr(s, "department_name", ""),
        })

    # Turn into list of (department, submissions) for template loop
    submissions_by_department = list(grouped.items())

    context = {
        "recent_items": recent_items,
        "submissions_by_department": submissions_by_department,
        "stats": stats,
        "site_title": "Overview",
    }
    return render(request, "admin_frontend/overview.html", context)


@staff_member_required
@require_POST
def submission_action(request, pk):
    """
    POST: action=approve|reject|deactivate|activate
    Updates DepartmentProfile.approval_status and returns JSON {ok: True, status: 'approved'}
    """
    action = request.POST.get("action")
    Submission = apps.get_model("cineapp", "DepartmentProfile")
    if Submission is None:
        return JsonResponse({"ok": False, "error": "model not found"}, status=404)

    qs = Submission.objects.filter(pk=pk)
    if not qs.exists():
        return JsonResponse({"ok": False, "error": "not found"}, status=404)

    if action == "approve":
        qs.update(approval_status="approved")
    elif action == "reject":
        qs.update(approval_status="rejected")
    elif action == "deactivate":
        qs.update(approval_status="inactive")
    elif action == "activate":
        qs.update(approval_status="approved")
    else:
        return JsonResponse({"ok": False, "error": "invalid action"}, status=400)

    obj = qs.first()
    status = getattr(obj, "approval_status", None) or "unknown"

    # Send email notification (fail silently if email backend isn't configured)
    try:
        to_email = getattr(obj, 'email', None)
        app_id = getattr(obj, 'application_id', None) or ''
        if to_email:
            subject = "Your 24 Cine Crafts profile status"
            if status == 'approved':
                msg = (
                    f"Hello {getattr(obj, 'full_name', '')},\n\n"
                    f"Your profile has been APPROVED.\n"
                    f"Application ID: {app_id}\n\n"
                    f"You can now access approved features on the platform.\n\n"
                    f"Regards,\n24 Cine Crafts Team"
                )
            elif status == 'rejected':
                msg = (
                    f"Hello {getattr(obj, 'full_name', '')},\n\n"
                    f"We regret to inform you that your profile was REJECTED.\n"
                    f"Application ID: {app_id}\n\n"
                    f"You may revise your details and apply again.\n\n"
                    f"Regards,\n24 Cine Crafts Team"
                )
            else:
                msg = (
                    f"Hello {getattr(obj, 'full_name', '')},\n\n"
                    f"Your profile status is now: {status.upper()}.\n"
                    f"Application ID: {app_id}\n\n"
                    f"Regards,\n24 Cine Crafts Team"
                )
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@cinecraft.local')
            send_mail(subject, msg, from_email, [to_email], fail_silently=True)
    except Exception:
        # Do not break the request due to email errors
        pass

    return JsonResponse({"ok": True, "status": status})


def custom_admin_logout(request):
    """
    Logs out the admin user and shows a success message, then redirects to login.
    """
    logout(request)
    return render(request, "admin_frontend/logout_success.html")


@staff_member_required
@require_POST
def submission_delete(request, pk):
    """
    Deletes a DepartmentProfile by pk.
    Returns JSON {ok: True}
    """
    Submission = apps.get_model("cineapp", "DepartmentProfile")
    if Submission is None:
        return JsonResponse({"ok": False, "error": "model not found"}, status=404)
    try:
        obj = Submission.objects.get(pk=pk)
    except Submission.DoesNotExist:
        return JsonResponse({"ok": False, "error": "not found"}, status=404)

    obj.delete()
    return JsonResponse({"ok": True})


@staff_member_required
def submission_edit(request, pk):
    """
    Edit a DepartmentProfile submission.
    GET: Show edit form
    POST: Update the profile
    """
    DepartmentProfile = apps.get_model("cineapp", "DepartmentProfile")
    if DepartmentProfile is None:
        return JsonResponse({"ok": False, "error": "model not found"}, status=404)

    profile = get_object_or_404(DepartmentProfile, pk=pk)

    if request.method == 'POST':
        # Update profile fields from POST data using setattr to avoid type checking issues
        field_mappings = {
            'full_name': 'full_name',
            'email': 'email',
            'phone_number': 'phone_number',
            'department_name': 'department_name',
            'address': 'address',
            'city': 'city',
            'state': 'state',
            'pin_code': 'pin_code',
            'key_skills': 'key_skills',
            'previous_projects': 'previous_projects',
            'availability': 'availability',
            'expected_salary_range': 'expected_salary_range',
            'performed_work_location': 'performed_work_location',
            'educational_qualification': 'educational_qualification',
            'certifications_training': 'certifications_training',
            'awards_recognition': 'awards_recognition',
            'portfolio_link': 'portfolio_link',
            'linkedin_profile': 'linkedin_profile',
            'imdb_profile': 'imdb_profile',
            'additional_information': 'additional_information',
            'approval_status': 'approval_status',
        }

        for post_field, model_field in field_mappings.items():
            value = request.POST.get(post_field)
            if value is not None:
                setattr(profile, model_field, value)

        # Handle years_of_experience separately (integer field)
        years_exp = request.POST.get('years_of_experience')
        if years_exp:
            try:
                setattr(profile, 'years_of_experience', int(years_exp))
            except (ValueError, TypeError):
                setattr(profile, 'years_of_experience', None)
        else:
            setattr(profile, 'years_of_experience', None)

        try:
            profile.save()
            # Get approval choices using getattr
            approval_choices = getattr(DepartmentProfile, 'APPROVAL_CHOICES', [])
            full_name = getattr(profile, 'full_name', 'User')

            context = {
                'profile': profile,
                'site_title': 'Edit Profile',
                'approval_choices': approval_choices,
                'success_message': f'Profile updated successfully for {full_name}'
            }
            return render(request, 'admin_frontend/edit_profile_success.html', context)
        except Exception as e:
            approval_choices = getattr(DepartmentProfile, 'APPROVAL_CHOICES', [])
            context = {
                'profile': profile,
                'site_title': 'Edit Profile',
                'approval_choices': approval_choices,
                'error_message': f'Error updating profile: {str(e)}'
            }
            return render(request, 'admin_frontend/edit_profile.html', context)

    # GET request - show form
    approval_choices = getattr(DepartmentProfile, 'APPROVAL_CHOICES', [])
    context = {
        'profile': profile,
        'site_title': 'Edit Profile',
        'approval_choices': approval_choices,
    }
    return render(request, 'admin_frontend/edit_profile.html', context)
