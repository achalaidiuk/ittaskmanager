from django import forms
from django.forms import DateInput
from .models import Task, Worker


class TaskCreationForm(forms.ModelForm):
    responsible = forms.ModelChoiceField(
        queryset=Worker.objects.all(), required=True
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "priority",
            "task_type",
            "description",
            "deadline",
            "responsible",
        ]

        widgets = {
            "deadline": DateInput(attrs={"type": "date"}),
        }
