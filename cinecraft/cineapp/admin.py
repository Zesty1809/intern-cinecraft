from django.contrib import admin

from .models import DepartmentProfile


@admin.register(DepartmentProfile)
class DepartmentProfileAdmin(admin.ModelAdmin):
	list_display = (
		"full_name",
		"department_name",
		"approval_status",
		"created_at",
	)
	list_filter = ("approval_status", "department_name")
	search_fields = (
		"full_name",
		"email",
		"phone_number",
		"application_id",
	)
	readonly_fields = ("application_id", "guid", "created_at")
