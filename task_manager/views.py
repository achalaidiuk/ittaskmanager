from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from task_manager.models import Worker, Task


@login_required
def index(request: HttpRequest) -> HttpResponse:
    num_workers = Worker.objects.count()
    num_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(is_completed=True).count()
    last_added_task = Task.objects.order_by('-created_at').first()

    context = {
        "num_workers": num_workers,
        "num_tasks": num_tasks,
        "completed_tasks": completed_tasks,
        "last_added_task": last_added_task.name if last_added_task else "None",
        "num_visits": request.session.get("num_visits", 0) + 1,
    }

    return render(request, "task_manager/index.html", context=context)


class MineTasksListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "mine_tasks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        count_tasks = self.get_queryset().aggregate(
            completed_tasks_count=Count("id", filter=Q(is_completed=True)),
            unfinished_tasks_count=Count("id", filter=Q(is_completed=False))
        )

        context["completed_tasks_count"] = count_tasks["completed_tasks_count"]
        context["incomplete_tasks_count"] = count_tasks["unfinished_tasks_count"]

        for task in self.get_queryset():
            if task.is_completed:
                context['done_at'] = task.done_at

        return context


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

    def manage_task(request: HttpRequest, task_id: int,
                    action: str) -> HttpResponse:
        task = get_object_or_404(Task, id=task_id)

        if action == "complete":
            if request.user in task.assignees.all():
                task.is_completed = True
                task.status = "Done"
                task.done_at = timezone.now()
                task.save()
                messages.success(request, "Task has been marked as completed.")
            else:
                messages.warning(request,
                                 "You cannot complete this task because you are not assigned to it.")
            return redirect("task_manager:all-tasks")

        elif action == "take":
            if task.is_completed or task.assignees.filter(
                    id=request.user.id).exists():
                messages.warning(request,
                                 "This task has already been taken or completed.")
            else:
                task.assignees.add(request.user)
                task.status = "In Progress"
                task.save()
                messages.success(request, "You have taken the task to work.")
            return redirect("task_manager:all-tasks")

        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER",
                             reverse_lazy("task_manager:mine-tasks"))
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


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    fields = ["first_name", "last_name", "position", "password"]
    success_url = reverse_lazy("task_manager:team")


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    fields = ["first_name", "last_name", "username", "position"]
    success_url = reverse_lazy("task_manager:team")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("task_manager:all-tasks")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("task_manager:all-tasks")

    def test_func(self):
        return self.request.user.is_admin


class TaskDetailView(generic.DetailView):
    model = Task
    template_name = "task_manager/task_detail.html"
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def work_done(request: HttpRequest, task_id: int) -> HttpResponse:
    task = get_object_or_404(Task, id=task_id)
    task.is_completed = True
    task.done_at = timezone.now()
    task.save()
    return HttpResponseRedirect(
        request.META.get(
            "HTTP_REFERER",
            reverse_lazy(viewname="task_manager:mine-tasks"))
    )


@login_required
def take_to_work(request: HttpRequest, task_id: int) -> HttpResponse:
    task = get_object_or_404(Task, id=task_id)

    if task.is_completed or task.assignees.filter(id=request.user.id).exists():
        messages.warning(request, "This task has already been taken or completed.")
        return redirect("task_manager:all-tasks")

    task.assignees.add(request.user)
    task.status = "In Progress"
    task.save()
    messages.success(request, "You have taken the task to work.")
    return redirect("task_manager:all-tasks")

def complete_task(request: HttpRequest, task_id: int) -> HttpResponse:
    task = get_object_or_404(Task, id=task_id)

    if request.user in task.assignees.all():
        task.is_completed = True
        task.status = "Done"
        task.done_at = timezone.now()
        task.save()
        messages.success(request, "Task has been marked as completed.")
    else:
        messages.warning(request, "You cannot complete this task because you are not assigned to it.")

    return redirect("task_manager:all-tasks")


@login_required
def assign_task(request, member_id):
    member = Worker.objects.get(id=member_id)
    tasks = Task.objects.filter(is_completed=False)

    if request.method == "POST":
        task_id = request.POST.get('task_id')
        task = Task.objects.get(id=task_id)
        task.assignees.add(member)
        task.save()
        return redirect('task_manager:team')

    return render(request, 'assign_task.html', {'member': member, 'tasks': tasks})