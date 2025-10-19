import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


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


class TOTPDevice(models.Model):
    """Stores a per-user TOTP secret and counters for rate-limiting/attempts."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='totp_device'
    )
    secret = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    # rate-limiting and attempt counters
    last_sent_at = models.DateTimeField(null=True, blank=True)
    send_count_hour = models.PositiveIntegerField(default=0)
    last_send_count_reset = models.DateTimeField(null=True, blank=True)

    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    def reset_send_counts(self):
        self.send_count_hour = 0
        self.last_send_count_reset = timezone.now()
        self.save(update_fields=['send_count_hour', 'last_send_count_reset'])

    def increment_send(self):
        now = timezone.now()
        if not self.last_send_count_reset or (now - self.last_send_count_reset).total_seconds() > 3600:
            self.send_count_hour = 1
            self.last_send_count_reset = now
        else:
            self.send_count_hour += 1
        self.last_sent_at = now
        self.save(update_fields=['send_count_hour', 'last_sent_at', 'last_send_count_reset'])

    def record_failed_attempt(self, lock_after=5, lock_minutes=15):
        self.failed_attempts += 1
        if self.failed_attempts >= lock_after:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lock_minutes)
        self.save(update_fields=['failed_attempts', 'locked_until'])

    def reset_attempts(self):
        self.failed_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_attempts', 'locked_until'])
