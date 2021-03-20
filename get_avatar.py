from io import BytesIO
from bs4 import BeautifulSoup
import requests
from pprint import pprint
from PIL import Image


def get_avatar(size=(95, 95)):
    """Загрузка случайного аватара"""
    response_to_random = requests.get('https://avatarko.ru/random')
    if response_to_random.status_code == 200:
        html_doc = BeautifulSoup(response_to_random.content, features="html.parser")
        list_img = html_doc.find('div', {'class': "mb-2 img-thumbnail position-relative"})
        image_data = list_img.find('img')
        image_name = image_data.get("src")
        image_url = "https://avatarko.ru/" + image_name
        response_to_image = requests.get(image_url)
        avatar_file_like = BytesIO(response_to_image.content)
        avatar = Image.open(avatar_file_like)
        avatar = avatar.resize(size=size)
        return avatar