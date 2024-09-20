from django.urls import path
from django.contrib.auth import views as auth_views


from task_manager.views import (
    MineTasksListView,
    AllTasksListView,
    TeamListView,
    index,
    TaskDeleteView,
    TaskUpdateView,
    WorkerCreateView,
    WorkerUpdateView, take_to_work
)


app_name = "task_manager"

urlpatterns = [
    path("", index, name="index"),
    path("mine/", MineTasksListView.as_view(), name="mine-tasks"),
    path("all/", AllTasksListView.as_view(), name="all-tasks"),
    path("team/", TeamListView.as_view(), name="team"),
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
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('task/<int:task_id>/take/', take_to_work, name='take-to-work'),
]