from django import forms
from django.core.exceptions import ValidationError

from .models import Project


def validate_github_url(value):
    if value and "github.com" not in value:
        raise ValidationError("Ссылка должна вести на GitHub (github.com).")


class ProjectForm(forms.ModelForm):

    github_url = forms.URLField(
        label="Ссылка на GitHub",
        required=False,
        assume_scheme="https",
        validators=[validate_github_url],
    )
    status = forms.ChoiceField(
        label="Статус",
        choices=[
            (Project.STATUS_OPEN, "Открыт"),
            (Project.STATUS_CLOSED, "Закрыт"),
        ],
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
