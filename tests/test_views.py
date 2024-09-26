from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from task_manager.models import Position, TaskType, Task
from django.utils import timezone

User = get_user_model()


class TaskViewsTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.user = User.objects.create_user(
            username="testuser",
            password="password",
            first_name="Test",
            last_name="User",
            position=self.position
        )
        self.task_type = TaskType.objects.create(name="Feature")
        self.task = Task.objects.create(
            name="Test Task",
            description="Task description",
            deadline=timezone.now() + timezone.timedelta(days=7),
            is_completed=False,
            priority="Medium",
            task_type=self.task_type,
        )

    def test_task_with_assignees(self):
        self.task.assignees.add(self.user)
        self.assertEqual(self.task.assignees.count(), 1)
        self.assertIn(self.user, self.task.assignees.all())

    def test_index_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("task_manager:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/index.html")

    def test_my_tasks_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("task_manager:my-tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_tasks.html")

    def test_all_tasks_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("task_manager:all-tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_tasks.html")

    def test_team_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("task_manager:team"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "team.html")
