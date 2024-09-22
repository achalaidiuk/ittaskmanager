from django.urls import path
from django.contrib.auth import views as auth_views

from task_manager.views import (
    MyTasksListView,
    AllTasksListView,
    TeamListView,
    index,
    TaskDeleteView,
    TaskUpdateView,
    WorkerCreateView,
    WorkerUpdateView,
    TaskDetailView,
    TaskCreateView,
    manage_task,
)

app_name = "task_manager"

urlpatterns = [
    path("", index, name="index"),
    path("my/", MyTasksListView.as_view(), name="my-tasks"),
    path("all/", AllTasksListView.as_view(), name="all-tasks"),
    path("team/", TeamListView.as_view(), name="team"),
    path("task/create/", TaskCreateView.as_view(), name="task-create"),
    path("task/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("task/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("worker/create/", WorkerCreateView.as_view(), name="worker-create"),
    path("worker/update/<int:pk>/", WorkerUpdateView.as_view(), name="worker-update"),
    path("task/<int:task_id>/manage/<str:action>/", manage_task, name="manage-task"),
    path("task/<int:task_id>/", TaskDetailView.as_view(), name="task-detail"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
]
