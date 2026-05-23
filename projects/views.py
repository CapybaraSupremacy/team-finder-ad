from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = 12


def project_list_view(request):
    queryset = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "projects/project_list.html", {
        "page_obj": page_obj,
        "projects": page_obj.object_list,
    })


@login_required
def favorites_view(request):
    queryset = (
        request.user.favorites
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "projects/favorite_projects.html", {
        "page_obj": page_obj,
        "projects": page_obj.object_list,
    })


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(f"/projects/{project.pk}/")
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        raise PermissionDenied
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"/projects/{project.pk}/")
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
def toggle_favorite(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if project in user.favorites.all():
        user.favorites.remove(project)
        favorited = False
    else:
        user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def toggle_participate(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if user in project.participants.all():
        project.participants.remove(user)
        participating = False
    else:
        project.participants.add(user)
        participating = True
    return JsonResponse({"status": "ok", "participating": participating})


@login_required
def complete_project(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "Нет прав"}, status=403)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error", "message": "Проект уже закрыт"}, status=400)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})
