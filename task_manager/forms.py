from django import forms
from django.contrib.auth import get_user_model
from django.forms import DateInput
from .models import Task


class TaskCreationForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "priority",
            "task_type",
            "description",
            "deadline",
            "assignees",
        ]

        widgets = {
            "deadline": DateInput(attrs={"type": "date"}),
        }
