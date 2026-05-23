import pytest
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import User


def _fake_avatar():
    # Минимальная PNG-заглушка для тестов
    return SimpleUploadedFile("av.png", b"\x89PNG\r\n\x1a\n", content_type="image/png")


@pytest.mark.django_db
def test_register_creates_user_and_redirects_to_main(client):
    with patch("users.models.generate_avatar", return_value=_fake_avatar()):
        response = client.post("/users/register/", {
            "name": "Anya", "surname": "Nova",
            "email": "anya@test.com", "password": "secret123",
        })
    assert response.status_code == 302
    assert response["Location"] == "/projects/list/"
    assert User.objects.filter(email="anya@test.com").exists()


@pytest.mark.django_db
def test_login_wrong_password_shows_error(client, user):
    response = client.post("/users/login/", {
        "email": "ivan@test.com", "password": "wrongpass",
    })
    assert response.status_code == 200
    assert "Неверный email или пароль" in response.content.decode()


@pytest.mark.django_db
def test_filter_ignored_for_anonymous(client):
    response = client.get("/users/list/?filter=owners-of-favorite-projects")
    assert response.context["active_filter"] == ""
