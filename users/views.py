from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from team_finder.utils import paginate

from .forms import ChangePasswordForm, LoginForm, ProfileEditForm, RegisterForm
from .models import User

USERS_PER_PAGE = 12

FILTER_OWNERS_OF_FAVORITE = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY = "participants-of-my-projects"


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(reverse("projects:list"))
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect(reverse("projects:list"))
            form.add_error(None, "Неверный email или пароль")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(reverse("projects:list"))


def user_detail_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile_view(request):
    user = request.user
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
        current_user=user,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(reverse("users:detail", kwargs={"user_id": user.pk}))
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    user = request.user
    form = ChangePasswordForm(request.POST or None, user=user)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["new_password1"])
        user.save()
        login(request, user)
        return redirect(reverse("users:detail", kwargs={"user_id": user.pk}))
    return render(request, "users/change_password.html", {"form": form})


def users_list_view(request):
    queryset = User.objects.order_by("-id")
    active_filter = ""
    query_prefix = ""

    if request.user.is_authenticated:
        active_filter = request.GET.get("filter", "")
        if active_filter == FILTER_OWNERS_OF_FAVORITE:
            owner_ids = request.user.favorites.values_list("owner_id", flat=True)
            queryset = queryset.filter(pk__in=owner_ids)
        elif active_filter == FILTER_OWNERS_OF_PARTICIPATING:
            owner_ids = request.user.participated_projects.values_list("owner_id", flat=True)
            queryset = queryset.filter(pk__in=owner_ids)
        elif active_filter == FILTER_INTERESTED_IN_MY:
            queryset = queryset.filter(
                favorites__owner=request.user
            ).distinct()
        elif active_filter == FILTER_PARTICIPANTS_OF_MY:
            queryset = queryset.filter(
                participated_projects__owner=request.user
            ).distinct()
        else:
            active_filter = ""

        if active_filter:
            query_prefix = f"filter={active_filter}&"

    page_obj = paginate(request, queryset, USERS_PER_PAGE)

    return render(request, "users/participants.html", {
        "page_obj": page_obj,
        "participants": page_obj.object_list,
        "active_filter": active_filter,
        "query_prefix": query_prefix,
    })
