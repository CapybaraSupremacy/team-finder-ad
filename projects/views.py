from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from team_finder.utils import paginate

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
    page_obj = paginate(request, queryset, PROJECTS_PER_PAGE)
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
    page_obj = paginate(request, queryset, PROJECTS_PER_PAGE)
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
        return redirect(reverse("projects:detail", kwargs={"project_id": project.pk}))
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        raise PermissionDenied
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(reverse("projects:detail", kwargs={"project_id": project.pk}))
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
def toggle_favorite(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    user = request.user
    was_favorited = user.favorites.filter(pk=project.pk).exists()
    if was_favorited:
        user.favorites.remove(project)
    else:
        user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not was_favorited})


@login_required
def toggle_participate(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    user = request.user
    was_participating = project.participants.filter(pk=user.pk).exists()
    if was_participating:
        project.participants.remove(user)
    else:
        project.participants.add(user)
    return JsonResponse({"status": "ok", "participating": not was_participating})


@login_required
def complete_project(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"},
            status=HTTPStatus.FORBIDDEN,
        )
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже закрыт"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})
