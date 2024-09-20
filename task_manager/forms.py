from django import forms
from django.forms import DateInput
from .models import Task


class TaskCreationForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = [
            "task_name",
            "priority",
            "task_type",
            "description",
            "deadline",
        ]

        widgets = {
            "deadline": DateInput(attrs={"type": "date"}),
        }