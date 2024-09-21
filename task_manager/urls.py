from django.urls import path
from django.contrib.auth import views as auth_views

from task_manager import views
from task_manager.views import (
    MyTasksListView,
    AllTasksListView,
    TeamListView,
    index,
    TaskDeleteView,
    TaskUpdateView,
    WorkerCreateView,
    WorkerUpdateView,
    take_to_work,
    TaskDetailView,
    assign_task,
    TaskCreateView
)


app_name = "task_manager"

urlpatterns = [
    path("", index, name="index"),
    path("my/", MyTasksListView.as_view(), name="my-tasks"),
    path("all/", AllTasksListView.as_view(), name="all-tasks"),
    path("team/", TeamListView.as_view(), name="team"),
    path("task/create/", TaskCreateView.as_view(), name="task-create"),
    path("task-delete/<int:pk>/delete/",
         TaskDeleteView.as_view(),
         name="task-delete"),
    path("task-update/<int:pk>/update",
         TaskUpdateView.as_view(),
         name="task-update"),
    path("worker_create/",
         WorkerCreateView.as_view(),
         name="worker-create"),
    path("worker_update/<int:pk>/update",
         WorkerUpdateView.as_view(),
         name="worker-update"),
    path("task/<int:task_id>/take/", take_to_work, name="take-to-work"),
    path("task/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("task/<int:task_id>/complete/",
         views.complete_task,
         name="complete-task"
         ),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path('assign-task/<int:member_id>/', assign_task, name='assign_task'),
]