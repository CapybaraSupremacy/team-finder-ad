from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "surname", "is_staff", "is_active")
    search_fields = ("email", "name", "surname")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")}
        ),
        (
            "Права",
            {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}
        ),
        ("Избранное", {"fields": ("favorites",)}),
    )
