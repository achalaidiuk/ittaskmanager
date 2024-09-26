from django.test import TestCase
from task_manager.models import Position, Worker, TaskType, Task


class PositionModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")

    def test_position_str(self):
        self.assertEqual(str(self.position), "Developer")


class WorkerModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker = Worker.objects.create(
            username="testuser",
            first_name="Test",
            last_name="User",
            position=self.position
        )

    def test_worker_str(self):
        self.assertEqual(
            str(self.worker), "Test User working as Developer"
        )


class TaskTypeModelTest(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug Fix")

    def test_task_type_str(self):
        self.assertEqual(str(self.task_type), "Bug Fix")


class TaskModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker = Worker.objects.create(
            username="testuser",
            first_name="Test",
            last_name="User",
            position=self.position
        )
        self.task_type = TaskType.objects.create(name="Bug Fix")
        self.task = Task.objects.create(
            name="Fix Issue",
            description="Fix the bug in the application.",
            deadline="2024-12-31",
            priority="High",
            task_type=self.task_type,
        )
        self.task.assignees.add(self.worker)

    def test_task_str(self):
        self.assertIn("Fix Issue assigned to", str(self.task))
        self.assertIn("with High priority", str(self.task))
