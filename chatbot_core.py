# -*- coding: utf-8 -*-, Python 3,8

import random
import logging

import requests
import vk_api
import handlers
import settings
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from generate_flights import GenerateFlights
from models import UserState, Registration
from convert_date import convert_data_to_str

try:
    from local_settings import TOKEN, GROUP_ID
except:
    raise ImportError("Поместите в модуль local_settings TOKEN и GROUP_ID вашей группы вк")

SPECIAL_COMMANDS = ["/ticket", "/help"]

log = logging.getLogger("bot")


def configere_loging():
    stream_handler = logging.StreamHandler()
    formater_for_stream = logging.Formatter(" %(levelname)s %(message)s")
    stream_handler.setFormatter(formater_for_stream)
    stream_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename="log_vk_log", encoding="utf-8", mode="a")
    formater_for_file_write = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%d-%m-%Y %H:%M")
    file_handler.setFormatter(formater_for_file_write)
    file_handler.setLevel(logging.INFO)

    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    log.setLevel(logging.DEBUG)


class Bot:
    """
    Сценарий рецистрации пользователя при приобретение белета на перелёты через vk.com
    Use python 3.8

    Поддерживает дефолтные фразы, выдучу общей информации по использованию бота и сценарий регистрации:
    Команды для вызова:
    /help выдает справку о том, как работает робот
    /ticket - начинает сценарий заказа билетов
    """

    def __init__(self, token, group_id):
        self.token = token
        self.group_id = group_id
        self.user_dalay = []
        self.need_delete_scenario = None
        self.vk_session = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk_session, self.group_id)
        self.api = self.vk_session.get_api()
        self.data_about_flights = GenerateFlights().run()
        self.flight_schedule = self.data_about_flights["timetable_flights"]
        self.departure_cities = self.data_about_flights["departure_cities"]
        self.departure_cities_for_write = self.data_about_flights["departure_cities_for_write"]

    def run(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            log.info("Событие было получено")
            try:
                self.on_event(event)
            except Exception:
                log.exception("Ошибка в обработке события")

    @db_session
    def on_event(self, event):
        """Обработка полученного события"""
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.debug("Мы пока не умеем обрабатывать событие такого типа %s", event.type)
            return
        user_id = event.object.peer_id
        text = event.object.text.lower()
        log.info(f'Пользователь написал {text}')
        state = UserState.get(user_id=user_id)
        if state is not None:
            if checking_special_commands(text):
                state.delete()
                self.sent_unswer_without_scenario(text=text, user_id=user_id)
            else:
                self.continue_scenario(text, state)
        else:
            self.sent_unswer_without_scenario(text=text, user_id=user_id)

    def sent_unswer_without_scenario(self, text, user_id):
        """Обработка ответа вне сценария"""
        for intent in settings.INTENTS:
            if any(token in text for token in intent["tokens"]):
                if intent["answer"]:
                    self.sent_text(text_to_sent=intent["answer"], user_id=user_id)
                else:
                    self.start_scenario(user_id, intent["scenario"], text)
                break
        else:
            self.sent_text(text_to_sent=settings.DEFAULT_ANSWER, user_id=user_id)

    def sent_text(self, text_to_sent, user_id):
        """Отправка текста пользователю"""
        self.api.messages.send(message=text_to_sent,
                               random_id=random.randint(0, 2 ** 20),
                               peer_id=user_id
                               )
        log.info(f'Ответ пользователю :{text_to_sent}')

    def sent_image(self, image, user_id):
        """Отправка изображения пользователю"""
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ("image.png", image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(attachment=attachment,
                               random_id=random.randint(0, 2 ** 20),
                               peer_id=user_id
                               )

    def sent_step(self, step, user_id, text, state):
        """отправка сообщения на текущем шаге"""
        if "text" in step:
            self.sent_text(step["text"].format(**state.context), user_id)
        if "image" in step:
            handler = getattr(handlers, step["image"])
            image = handler(text, state)
            self.sent_image(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        """Начало сценария и выполнения первого шага"""
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario["first_step"]
        step = scenario["steps"][first_step]
        info_user = self.api.users.get(user_ids=user_id)[0]
        first_name = info_user["first_name"]
        last_name = info_user["last_name"]
        UserState(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            scenario_name=scenario_name,
            step_name=first_step,
            context={}
        )
        state = UserState.get(user_id=user_id)
        state.context["departure_cities_for_write"] = self.departure_cities_for_write
        state.context["departure_cities"] = self.departure_cities
        state.context["flight_schedule"] = convert_data_to_str(self.flight_schedule)
        self.sent_step(
            step=step,
            user_id=user_id,
            text=text,
            state=state
        )

    def continue_scenario(self, text, state):
        steps = settings.SCENARIOS[state.scenario_name]["steps"]
        step = steps[state.step_name]
        handler = getattr(handlers, step["handler"])
        if handler(text=text, state=state):
            next_step = steps[step["next_step"]]
            self.sent_step(step=next_step, user_id=state.user_id, text=text, state=state)
            if next_step["next_step"]:
                state.step_name = step["next_step"]
            else:
                Registration(
                    user_id=state.user_id,
                    first_name=state.first_name,
                    last_name=state.last_name,
                    user_flight=state.context['user_flight_of_write'],
                    user_flight_data=state.context["data_flights"],
                    user_number_seats=state.context['user_number_seats'],
                    comment=state.context['comment'],
                    number_phone=state.context["phone"]
                )
                state.delete()
        else:
            self.sent_text(text_to_sent=step["failure_text"].format(**state.context), user_id=state.user_id)


def checking_special_commands(text):
    for spicial_command in SPECIAL_COMMANDS:
        if text == spicial_command:
            return True


if __name__ == "__main__":
    configere_loging()
    bot = Bot(token=TOKEN, group_id=GROUP_ID)
    bot.run()
