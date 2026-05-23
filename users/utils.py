import io
import random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


AVATAR_COLORS = [
    "#5B8DB8",
    "#6AAB8E",
    "#B87C5B",
    "#8B6BAB",
]


def hex_to_rgb(hex_color):
    # Конвертирует HEX-цвет в кортеж RGB
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def generate_avatar(name):
    # Генерирует PNG-аватарку: первая буква имени на цветном фоне
    size = 200
    bg_color = hex_to_rgb(random.choice(AVATAR_COLORS))
    letter = name[0].upper() if name else "?"

    image = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "static/fonts/Jost-Regular.ttf", size=100
        )
    except (IOError, OSError):
        font = ImageFont.load_default(size=100)

    # Центрируем букву. textbbox даёт координаты прямоугольника текста,
    # но отсчёт идёт от базовой линии, поэтому вычитаем bbox[0] и bbox[1],
    # чтобы поправить смещение. Без этого буква уезжает вправо-вниз
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]

    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    filename = f"avatar_{letter}_{random.randint(1000, 9999)}.png"
    return ContentFile(buffer.read(), name=filename)


def normalize_phone(phone):
    # Приводит номер телефона к формату +7XXXXXXXXXX
    # Нужно чтобы 8... и +7... считались одинаковыми при проверке уникальности
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone
