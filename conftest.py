from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from projects.models import Project
from users.models import User


@pytest.fixture(autouse=True)
def _media_root(tmp_path, settings):
    # Перенаправляет MEDIA_ROOT во временную папку, чтобы тесты
    # не сорили файлами в реальной media/avatars
    settings.MEDIA_ROOT = tmp_path / "media"
    Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)


def _fake_avatar():
    """Минимальный PNG-байт — подменяет PIL-генерацию в тестах.

    Генерировать реальную картинку через PIL в тестах долго и не нужно,
    поэтому подсовываем "заглушку" — первые байты настоящего PNG.
    Django проверяет content_type, а не содержимое.
    """
    return SimpleUploadedFile("av.png", b"\x89PNG\r\n\x1a\n", content_type="image/png")


def _create_user(email, name, surname, password="pass1234"):
    with patch("users.models.generate_avatar", return_value=_fake_avatar()):
        return User.objects.create_user(
            email=email, name=name, surname=surname, password=password,
            phone="+79001234567",
        )


@pytest.fixture
def user(db):
    return _create_user("ivan@test.com", "Ivan", "Petrov")


@pytest.fixture
def other_user(db):
    return _create_user("maria@test.com", "Maria", "Sidorova")


@pytest.fixture
def project(user):
    return Project.objects.create(
        name="Тестовый проект",
        description="Описание тестового проекта",
        owner=user,
        status=Project.STATUS_OPEN,
    )


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def auth_client(client, user):
    """Клиент, авторизованный от имени основного пользователя."""
    client.force_login(user)
    return client


@pytest.fixture
def other_client(other_user):
    """Клиент, авторизованный от имени второго пользователя."""
    c = Client()
    c.force_login(other_user)
    return c
