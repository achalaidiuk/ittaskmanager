from django.urls import path

from task_manager.views import (
    index,
    manage_task,
    MyTasksListView,
    AllTasksListView,
    TeamListView,
    TaskDeleteView,
    TaskUpdateView,
    TaskDetailView,
    TaskCreateView,
    WorkerCreateView,
    WorkerUpdateView,
)

app_name = "task_manager"

urlpatterns = [
    path("", index, name="index"),
    path("my_tasks/", MyTasksListView.as_view(), name="my-tasks"),
    path("all_tasks/", AllTasksListView.as_view(), name="all-tasks"),
    path("team/", TeamListView.as_view(), name="team"),
    path("task/create/", TaskCreateView.as_view(), name="task-create"),
    path("task/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "task/<int:pk>/delete/",
        TaskDeleteView.as_view(),
        name="task-delete"
    ),
    path(
        "task/<int:pk>/update/",
        TaskUpdateView.as_view(),
        name="task-update"
    ),
    path("worker/create/", WorkerCreateView.as_view(), name="worker-create"),
    path(
        "worker/update/<int:pk>/",
        WorkerUpdateView.as_view(),
        name="worker-update"
    ),
    path(
        "task/<int:task_id>/manage/<str:action>/",
        manage_task,
        name="manage-task"
    ),
    path("task/<int:task_id>/", TaskDetailView.as_view(), name="task-detail"),
]
