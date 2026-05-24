import io
import random
import re

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

COLOR_BLUE = "#5B8DB8"
COLOR_GREEN = "#6AAB8E"
COLOR_ORANGE = "#B87C5B"
COLOR_PURPLE = "#8B6BAB"

AVATAR_COLORS = [
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_PURPLE,
]

AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 100
FONT_PATH = "static/fonts/Jost-Regular.ttf"
FILL_COLOR = "white"

RANDOM_MIN = 1000
RANDOM_MAX = 9999


HEX_PREFIX = "#"
HEX_SLICE_STEP = 2
HEX_PARTS_START = (0, 2, 4)
BASE_HEX = 16


PHONE_PATTERN = r"^(\+7|8)\d{10}$"


def hex_to_rgb(hex_color):
    # Конвертирует HEX-цвет в кортеж RGB
    hex_color = hex_color.lstrip(HEX_PREFIX)
    return tuple(
        int(hex_color[i:i + HEX_SLICE_STEP], BASE_HEX)
        for i in HEX_PARTS_START
    )


def generate_avatar(name):
    # Генерирует PNG-аватарку: первая буква имени на цветном фоне
    bg_color = hex_to_rgb(random.choice(AVATAR_COLORS))
    letter = name[0].upper() if name else "?"

    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(FONT_PATH, size=AVATAR_FONT_SIZE)
    except (IOError, OSError):
        font = ImageFont.load_default(size=AVATAR_FONT_SIZE)

    # Центрируем букву. textbbox даёт координаты прямоугольника текста,
    # но отсчёт идёт от базовой линии, поэтому вычитаем bbox[0] и bbox[1],
    # чтобы поправить смещение. Без этого буква уезжает вправо-вниз
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (AVATAR_SIZE - text_w) / 2 - bbox[0]
    y = (AVATAR_SIZE - text_h) / 2 - bbox[1]

    draw.text((x, y), letter, fill=FILL_COLOR, font=font)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    filename = f"avatar_{letter}_{random.randint(RANDOM_MIN, RANDOM_MAX)}.png"
    return ContentFile(buffer.read(), name=filename)


def normalize_phone(phone):
    # Приводит номер телефона к формату +7XXXXXXXXXX
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


def validate_github_url(value):
    if value and "github.com" not in value:
        raise ValidationError("Ссылка должна вести на GitHub (github.com).")


def validate_phone(phone, exclude_user=None):
    # Проверяет формат телефона, нормализует и проверяет уникальность
    from users.models import User

    phone = phone.strip()
    if not phone:
        return phone

    if not re.match(PHONE_PATTERN, phone):
        raise ValidationError(
            "Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
        )

    normalized = normalize_phone(phone)

    qs = User.objects.filter(phone__in=[normalized, phone])
    if exclude_user:
        qs = qs.exclude(pk=exclude_user.pk)
    if qs.exists():
        raise ValidationError("Этот номер телефона уже используется.")

    return normalized
