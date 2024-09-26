from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, null=True, default=None
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} working as {self.position}"

    class Meta:
        verbose_name_plural = "Workers"
        ordering = ["last_name", "first_name", "position"]


class TaskType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    STATUS_CHOICES = [
        ("New", "New"),
        ("In Progress", "In Progress"),
        ("Done", "Done"),
    ]

    done_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=6)
    task_type = models.ForeignKey(
        "TaskType", on_delete=models.CASCADE, related_name="tasks"
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="tasks", blank=True
    )
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=12, default="New"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs) -> None:
        if self.is_completed:
            self.status = Task.STATUS_CHOICES[2][0]
        else:
            self.status = Task.STATUS_CHOICES[1][0]

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        assignee_names = ", ".join(
            str(assignee) for assignee in self.assignees.all())
        return (
            f"{self.name} assigned to {assignee_names} "
            f"with {self.priority} priority, Status: {self.status}"
        )
