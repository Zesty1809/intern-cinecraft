import traceback

from django.apps import apps
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token


DEFAULT_DEPARTMENTS = [
    {"title": "Direction Department", "subtitle": "Directors, Assistant Directors, Script Supervisors", "status": "Active"},
    {"title": "Cinematography", "subtitle": "DOPs, Camera Operators, Gaffers", "status": "Active"},
    {"title": "Editing Department", "subtitle": "Editors, Colorists, VFX Editors", "status": "Active"},
    {"title": "Sound Department", "subtitle": "Sound Designers, Recordists, Foley Artists", "status": "Active"},
    {"title": "Music Department", "subtitle": "Composers, Music Directors, Sound Producers", "status": "Active"},
    {"title": "Art Department", "subtitle": "Production Designers, Set Designers, Props", "status": "Active"},
    {"title": "Production Design", "subtitle": "Art Directors, Set Fabricators, Scenic Artists", "status": "Active"},
    {"title": "Costume Department", "subtitle": "Costume Designers, Wardrobe Supervisors", "status": "Active"},
    {"title": "Make Up Department", "subtitle": "Make-up Artists, Hair Stylists, Prosthetics", "status": "Active"},
    {"title": "Lighting Department", "subtitle": "Chief Lighting Technician, Best Boy, Lighting Assistants", "status": "Active"},
    {"title": "VFX & Animation", "subtitle": "VFX Supervisors, CG Artists, Animators", "status": "Active"},
    {"title": "Script & Screenplay", "subtitle": "Screenwriters, Script Doctors, Script Supervisors", "status": "Active"},
    {"title": "Casting Department", "subtitle": "Casting Directors, Talent Coordinators", "status": "Active"},
    {"title": "Production Management", "subtitle": "Line Producers, Unit Production Managers", "status": "Active"},
    {"title": "Location Management", "subtitle": "Location Managers, Scouts, Permits", "status": "Active"},
    {"title": "Post Production", "subtitle": "Post Supervisors, DI Producers, Deliverables", "status": "Active"},
    {"title": "Marketing & Promotions", "subtitle": "Marketing Strategists, Promo Producers", "status": "Active"},
    {"title": "Public Relations", "subtitle": "PR Managers, Press Coordinators, Media Liaisons", "status": "Active"},
    {"title": "Distribution & Sales", "subtitle": "Distribution Executives, Sales Agents", "status": "Active"},
    {"title": "Choreography Department", "subtitle": "Choreographers, Movement Coaches, Dance Directors", "status": "Active"},
    {"title": "Stunts & Action", "subtitle": "Stunt Coordinators, Fight Masters, Safety Officers", "status": "Active"},
    {"title": "Set Decoration", "subtitle": "Set Decorators, Prop Masters, Buyers", "status": "Active"},
    {"title": "Color Grading", "subtitle": "Colorists, DI Operators, Finish Artists", "status": "Active"},
    {"title": "Documentary & Research", "subtitle": "Researchers, Archival Producers, Fact Checkers", "status": "Active"},
]


class CustomAdminSite(AdminSite):
    site_header = "24 Cine Crafts"
    site_title = "Cinecraft Admin"
    index_title = "Overview"

    def _safe_get_model(self, app_label, model_name):
        try:
            return apps.get_model(app_label, model_name)
        except Exception:
            return None

    def _extract_status(self, obj):
        # Always use approval_status for DepartmentProfile
        status_val = getattr(obj, 'approval_status', None)
        if status_val is None:
            return ("Unknown", "unknown")
        s = str(status_val).strip().lower()
        if s == "approved":
            return ("Active", "active")
        if s == "pending":
            return ("Pending", "pending")
        if s == "rejected":
            return ("Reject", "rejected")
        if s == "inactive":
            return ("Inactive", "inactive")
        if s == "draft":
            return ("Draft", "draft")
        return (str(status_val).capitalize(), s)

    def index(self, request, extra_context=None):
        stats = {
            'total_submissions': 0,
            'pending_review': 0,
            'approved': 0,
            'active_users': get_user_model().objects.filter(is_active=True).count(),
        }
        recent_items = []
        submissions_list = []
        submissions_by_department = {}  # Group submissions by department
        departments_list = []
        users_list = []
        users_active_list = []
        users_inactive_list = []

        try:
            Submission = self._safe_get_model('cineapp', 'DepartmentProfile')
            Department = self._safe_get_model('cineapp', 'Department')

            if Submission is not None:
                qs = Submission.objects.all().order_by('-created_at')[:200]
                stats['total_submissions'] = Submission.objects.count()

                pending_count = 0
                approved_count = 0

                for s in qs:
                    label, key = self._extract_status(s)
                    if key == "pending":
                        pending_count += 1
                    if key in ("approved", "active"):
                        approved_count += 1

                    department = getattr(s, 'department_name', None) or 'Unknown Department'

                    submission_data = {
                        'name': getattr(s, 'full_name', str(s)),
                        'contact': getattr(s, 'phone_number', ''),
                        'email': getattr(s, 'email', ''),
                        'join_date': getattr(s, 'created_at', None),
                        'experience': getattr(s, 'years_of_experience', None),
                        'status_label': label,
                        'status_key': key,
                        'craft': department,
                        'obj_pk': getattr(s, 'pk', None),
                        'application_id': getattr(s, 'application_id', ''),
                    }

                    submissions_list.append(submission_data)

                    # Group by department
                    if department not in submissions_by_department:
                        submissions_by_department[department] = []
                    submissions_by_department[department].append(submission_data)

                recent_items = []
                for s_obj, s_data in zip(qs[:8], submissions_list[:8]):
                    recent_items.append({
                        'name': s_data['name'],
                        'department': s_data['craft'],
                        'date': getattr(s_obj, 'created_at', None),
                        'experience': s_data.get('experience'),
                        'status': s_data['status_label'],
                        'status_key': s_data['status_key'],
                    })

                stats['pending_review'] = pending_count
                stats['approved'] = approved_count

                # Build Users lists from DepartmentProfile entries
                for s in qs:
                    label, key = self._extract_status(s)
                    user_item = {
                        'source': 'submission',
                        'name': getattr(s, 'full_name', 'Unknown'),
                        'role': getattr(s, 'department_name', ''),
                        'experience': getattr(s, 'years_of_experience', None),
                        'email': getattr(s, 'email', ''),
                        'obj_pk': getattr(s, 'pk', None),
                        'application_id': getattr(s, 'application_id', ''),
                        'status': label,
                        'status_key': key,
                    }
                    if key in ('active', 'approved'):
                        users_active_list.append(user_item)
                    elif key == 'inactive':
                        users_inactive_list.append(user_item)

                # Prepare departments list
                department_lookup = {item["title"]: dict(item) for item in DEFAULT_DEPARTMENTS}
                if Department is not None:
                    dept_qs = Department.objects.all()
                    for d in dept_qs:
                        title = getattr(d, 'name', str(d))
                        department_lookup[title] = {
                            'title': title,
                            'subtitle': getattr(d, 'description', ''),
                            'status': 'Active' if getattr(d, 'is_active', True) else 'Inactive'
                        }
                elif submissions_list:
                    for s in submissions_list:
                        craft = s.get('craft') or 'Unknown'
                        department_lookup.setdefault(craft, {'title': craft, 'subtitle': '', 'status': 'Active'})

                default_titles = [item['title'] for item in DEFAULT_DEPARTMENTS]
                departments_list = []
                for item in DEFAULT_DEPARTMENTS:
                    title = item['title']
                    departments_list.append(department_lookup.get(title, dict(item)))

                extra_titles = set(department_lookup.keys()) - set(default_titles)
                for title in sorted(extra_titles):
                    departments_list.append(department_lookup[title])

            else:
                # Fallback when DepartmentProfile doesn't exist
                stats['total_submissions'] = LogEntry.objects.count()
                recent = LogEntry.objects.select_related('user').order_by('-action_time')[:8]
                for e in recent:
                    user = getattr(e, 'user', None)
                    name = None
                    if user is not None:
                        get_full = getattr(user, 'get_full_name', None)
                        if callable(get_full):
                            try:
                                name = get_full()
                            except Exception:
                                name = getattr(user, 'username', str(user))
                        else:
                            name = getattr(user, 'username', str(user))
                    recent_items.append({
                        'name': name or 'Unknown',
                        'department': '',
                        'date': getattr(e, 'action_time', None),
                        'experience': None,
                        'status': None,
                        'status_key': 'unknown',
                    })
                departments_list = []
                users_list = []

        except Exception:
            traceback.print_exc()

        # Sort department sections by most recent submission in that department
        def _group_latest_ts(group):
            # group is (department_name, submissions_in_dept)
            items = group[1]
            latest = None
            for it in items:
                ts = it.get('join_date')  # created_at
                if ts and (latest is None or ts > latest):
                    latest = ts
            return latest or 0

        sorted_departments = sorted(
            submissions_by_department.items(),
            key=_group_latest_ts,
            reverse=True
        )

        extra = extra_context or {}
        extra.update({
            'stats': stats,
            'recent_items': recent_items,
            'submissions_list': submissions_list,
            'submissions_by_department': sorted_departments,  # Pass grouped data
            'departments_list': departments_list,
            'users_list': users_list,
            'users_active_list': users_active_list,
            'users_inactive_list': users_inactive_list,
            'csrf_token_value': get_token(request),
        })
        return super().index(request, extra_context=extra)


# instantiate custom admin site with name 'admin' so existing admin:url names keep working
admin_site = CustomAdminSite(name='admin')

# re-register existing models onto custom admin site defensively
for model, model_admin in list(admin.site._registry.items()):
    try:
        # prefer registering the ModelAdmin class so Django constructs it for the new site
        admin_site.register(model, model_admin.__class__)
    except admin.sites.AlreadyRegistered:
        pass
    except Exception:
        traceback.print_exc()
