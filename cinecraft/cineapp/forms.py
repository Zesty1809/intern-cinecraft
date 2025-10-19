from django import forms

from cineapp.models import DepartmentProfile


class DepartmentProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"],
        required=False,
    )

    class Meta:
        model = DepartmentProfile
        exclude = [
            "department_name",
            "approval_status",
            "application_id",
            "guid",
            "user",
        ]

    def __init__(self, *args, draft: bool = False, **kwargs):
        self.draft_mode = bool(draft)
        super().__init__(*args, **kwargs)
        # Show logged-in email, but don't require it from POST because the input is disabled
        self.fields["email"].disabled = True
        self.fields["email"].required = False

        # If draft mode, relax required constraints for fields except minimal identity
        if self.draft_mode:
            for name, field in self.fields.items():
                field.required = False

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.draft_mode:
            obj.approval_status = 'draft'
        else:
            # normal submit sets to pending
            obj.approval_status = 'pending'
        if commit:
            obj.save()
        return obj
