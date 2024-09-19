from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from task_manager.models import Worker, Task


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View function for the home page of the site."""

    num_workers = Worker.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_workers": num_workers,
        "num_visits": num_visits + 1,
    }

    return render(
        request, "task_manager/index.html", context=context
    )


class MineTasksView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "mine_tasks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        count_tasks = self.get_queryset().aggregate(
            completed_tasks_count=Count(
                "id", filter=Q(is_completed=True)
            ),
            unfinished_tasks_count=Count(
                "id", filter=Q(is_completed=False)
            )
        )

        context["completed_tasks_count"] = count_tasks["completed_tasks_count"]
        context["unfinished_tasks_count"] = count_tasks[
            "unfinished_tasks_count"
        ]

        return context

    def get_queryset(self):
        return Task.objects.filter(assignees=self.request.user)
