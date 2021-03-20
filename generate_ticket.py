from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from get_avatar import get_avatar

BLACK = (0, 0, 0, 255)
FONT_PATH = "files/ofont_ru_Primus.ttf"
TEMPLATE_PATH = "files/ticket_template.png"
COLOR = BLACK


def generate_ticket(first_name, last_name, city_from, city_to, data) -> object:
    """Создание билета для отправки пользователю"""
    base = Image.open(f"{TEMPLATE_PATH}").convert("RGBA")
    font = ImageFont.truetype(f"{FONT_PATH}", 18)
    draw = ImageDraw.Draw(base)
    name = last_name + " " + first_name
    avatar = get_avatar()
    draw.text((47, 124), name, font=font, fill=COLOR)
    draw.text((47, 194), city_from, font=font, fill=COLOR)
    draw.text((47, 260), city_to, font=font, fill=COLOR)
    draw.text((286, 260), data, font=font, fill=COLOR)
    base.paste(avatar, (287, 70))
    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)
    return temp_file


# generate_ticket("Лирооой", "Дженкинс", 'Воронеж', 'Мухосранск', "20-01-2021")

