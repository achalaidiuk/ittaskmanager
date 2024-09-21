from django import forms
from django.forms import DateInput
from .models import Task, Worker


class TaskCreationForm(forms.ModelForm):

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
