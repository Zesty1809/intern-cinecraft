import uuid

from django.conf import settings
from django.db import models


class DepartmentProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dept_profiles",
        null=True, blank=True
    )

    # Identity and system fields
    application_id = models.CharField(max_length=16, blank=True, null=True, db_index=True, unique=True)
    guid = models.UUIDField(editable=False, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Domain fields
    department_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)

    # Professional information
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    key_skills = models.TextField(blank=True)
    previous_projects = models.TextField(blank=True)
    availability = models.CharField(max_length=50, blank=True)
    expected_salary_range = models.CharField(max_length=50, blank=True)
    performed_work_location = models.CharField(max_length=100, blank=True)

    # Education & certifications
    educational_qualification = models.TextField(blank=True)
    certifications_training = models.TextField(blank=True)
    awards_recognition = models.TextField(blank=True)

    # Portfolio & links
    portfolio_link = models.URLField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    imdb_profile = models.URLField(blank=True)

    # Additional information & uploads
    additional_information = models.TextField(blank=True)
    resume_upload = models.FileField(upload_to="uploads/", blank=True, null=True)

    # new approval state: default pending, optional for forms
    APPROVAL_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("inactive", "Inactive"),
        ("draft", "Draft"),
    )
    approval_status = models.CharField(
        max_length=16,
        choices=APPROVAL_CHOICES,
        default="pending",
        db_index=True,
        blank=True,
    )

    # optional convenience: ensure guid/application_id populated
    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = uuid.uuid4()
        super().save(*args, **kwargs)
        if not self.application_id:
            self.application_id = f"24CC{self.pk:05d}"
            super().save(update_fields=["application_id"])

    def __str__(self):
        return f"{self.full_name} - {self.department_name}"
