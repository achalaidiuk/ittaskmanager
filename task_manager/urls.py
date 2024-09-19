from django.urls import path


from task_manager.views import (
    MineTasksListView,
    AllTasksListView,
    TeamListView,
    index
)


app_name = "task_manager"

urlpatterns = [
    path("", index, name="index"),
    path("mine/", MineTasksListView.as_view(), name="mine-tasks"),
    path("all/", AllTasksListView.as_view(), name="all-tasks"),
    path("team/", TeamListView.as_view(), name="team"),
]