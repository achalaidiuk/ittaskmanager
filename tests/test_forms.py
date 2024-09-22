from django.test import TestCase
from django.contrib.auth import get_user_model
from task_manager.forms import TaskCreationForm
from task_manager.models import TaskType, Position

User = get_user_model()


class TaskCreationFormTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.user1 = User.objects.create_user(
            username="testuser1",
            password="password",
            first_name="Test",
            last_name="User",
            position=self.position
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="password",
            first_name="Another",
            last_name="User",
            position=self.position
        )
        self.task_type = TaskType.objects.create(name="Bug Fix")

    def test_task_creation_form_valid(self):
        form_data = {
            "name": "Fix Issue",
            "priority": "High",
            "task_type": self.task_type.id,
            "description": "Fix the bug in the application.",
            "deadline": "2024-12-31",
            "assignees": [self.user1.id, self.user2.id],
        }
        form = TaskCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_task_creation_form_invalid_without_name(self):
        form_data = {
            "name": "",
            "priority": "High",
            "task_type": self.task_type.id,
            "description": "Fix the bug in the application.",
            "deadline": "2024-12-31",
            "assignees": [self.user1.id, self.user2.id],
        }
        form = TaskCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_task_creation_form_invalid_without_assignees(self):
        form_data = {
            "name": "Fix Issue",
            "priority": "High",
            "task_type": self.task_type.id,
            "description": "Fix the bug in the application.",
            "deadline": "2024-12-31",
            "assignees": [],
        }
        form = TaskCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("assignees", form.errors)
