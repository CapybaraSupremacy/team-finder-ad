import json

import pytest

from projects.models import Project


@pytest.mark.django_db
def test_create_project_sets_owner_and_participant(auth_client, user):
    # Автор проекта автоматически добавляется в участники
    auth_client.post("/projects/create-project/", {
        "name": "Новый проект",
        "description": "Описание",
        "github_url": "https://github.com/test/repo",
        "status": Project.STATUS_OPEN,
    })
    project = Project.objects.get(name="Новый проект")
    assert project.owner == user
    assert user in project.participants.all()


@pytest.mark.django_db
def test_owner_can_complete_project(auth_client, project):
    # Завершение проекта: JSON-ответ и смена статуса
    response = auth_client.post(f"/projects/{project.pk}/complete/")
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["project_status"] == "closed"
    project.refresh_from_db()
    assert project.status == Project.STATUS_CLOSED


@pytest.mark.django_db
def test_toggle_favorite_adds_project(auth_client, user, project):
    # добавление проекта в избранное через JSON-эндпоинт
    response = auth_client.post(f"/projects/{project.pk}/toggle-favorite/")
    data = json.loads(response.content)
    assert data["status"] == "ok"
    assert data["favorited"] is True
    assert project in user.favorites.all()


@pytest.mark.django_db
def test_favorites_page_requires_login(client):
    # страница избранного доступна только авторизованным
    response = client.get("/projects/favorites/")
    assert response.status_code == 302
