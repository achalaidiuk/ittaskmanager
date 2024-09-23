from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Value, QuerySet
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic, View

from task_manager.forms import TaskCreationForm
from task_manager.models import Worker, Task


@login_required
def index(request: HttpRequest) -> HttpResponse:
    num_workers = Worker.objects.count()
    num_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(is_completed=True).count()
    last_added_task = Task.objects.order_by("-created_at").first()

    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    context = {
        "num_workers": num_workers,
        "num_tasks": num_tasks,
        "completed_tasks": completed_tasks,
        "last_added_task": last_added_task,
        "num_visits": num_visits,
    }

    return render(
        request, "task_manager/index.html", context=context
    )


class MyTasksListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "my_tasks.html"

    def get_queryset(self):
        return (
            Task.objects.filter(assignees=self.request.user)
                .prefetch_related("assignees")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        task_queryset = self.get_queryset()

        count_tasks = task_queryset.aggregate(
            completed_tasks_count=Count(
                "id", filter=Q(is_completed=True)
            ),
            unfinished_tasks_count=Count(
                "id", filter=Q(is_completed=False)
            ),
        )

        context["completed_tasks_count"] = count_tasks["completed_tasks_count"]
        context["incomplete_tasks_count"] = (
            count_tasks["unfinished_tasks_count"]
        )
        context["completed_tasks"] = task_queryset.filter(is_completed=True)
        context["incomplete_tasks"] = task_queryset.filter(is_completed=False)

        return context


class AllTasksListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "all_tasks.html"
    paginate_by = 8

    def get_queryset(self) -> QuerySet:
        return Task.objects.prefetch_related("assignees").annotate(
            responsible=Coalesce(
                Value("Not assigned"),
                "assignees__username",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_possible_tasks"] = self.model.objects.count()
        return context


@login_required
def manage_task(request, task_id, action):
    task = get_object_or_404(Task, id=task_id)

    if action == "complete":
        if request.user in task.assignees.all():
            task.is_completed = True
            task.status = "Completed"
            task.done_at = timezone.now()
            task.save()
            messages.success(request, "Task marked as completed.")
        else:
            messages.warning(request, "You cannot complete this task because you are not assigned to it.")

    elif action == "take":
        if task.is_completed or task.assignees.filter(id=request.user.id).exists():
            messages.warning(request, "This task has already been taken or completed.")
        else:
            task.assignees.add(request.user)
            task.status = "In progress"
            task.save()
            messages.success(request, "You have taken the task for completion.")

    return redirect("task_manager:all-tasks")


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    context_object_name = "team_members"
    template_name = "team.html"
    paginate_by = 8

    def get_queryset(self):
        return Worker.objects.select_related("position").prefetch_related("tasks").order_by("first_name", "last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_members"] = self.get_queryset().count()
        context["title"] = "Our Team"
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    fields = ["first_name", "last_name", "position", "password"]
    success_url = reverse_lazy("task_manager:team")


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    fields = ["first_name", "last_name", "username", "position"]
    success_url = reverse_lazy("task_manager:team")


class TaskCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = TaskCreationForm()
        return render(request, "task_manager/task_form.html", {"form": form, "object": None})

    def post(self, request):
        form = TaskCreationForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            form.save_m2m()
            messages.success(request, "Task has been created successfully.")
            return redirect("task_manager:all-tasks")
        return render(request, "task_manager/task_form.html", {"form": form, "object": None})


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("task_manager:all-tasks")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "task_manager/task_confirm_delete.html"
    success_url = reverse_lazy("task_manager:all-tasks")

    def test_func(self):
        return self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.object
        return context


class TaskDetailView(generic.DetailView):
    model = Task
    context_object_name = "task"
    template_name = "task_manager/task_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
