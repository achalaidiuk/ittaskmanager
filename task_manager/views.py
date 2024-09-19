from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from task_manager.models import Worker, Task


@login_required
def index(request: HttpRequest) -> HttpResponse:

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


class MineTasksListView(LoginRequiredMixin, generic.ListView):
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


class AllTasksListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "all_tasks.html"
    paginate_by = 8

    def get_queryset(self):
        return Task.objects.annotate(
            responsible=Coalesce(
                Subquery(
                    Task.assignees.through.objects.filter(task_id=OuterRef("pk")).values("worker__username")[:1]
                ),
                Value("Not assigned")
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_possible_tasks"] = Task.objects.count()
        return context


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    template_name = "team.html"
    paginate_by = 8
    context_object_name = "team_members"

    def get_queryset(self):
        return Worker.objects.all().order_by("first_name", "last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_members"] = Worker.objects.count()
        context["title"] = "Our Team"
        return context
