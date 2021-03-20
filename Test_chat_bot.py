from copy import deepcopy
import datetime
from io import BytesIO
from unittest.mock import patch, Mock
import unittest

from PIL import Image
from pony.orm import db_session, rollback
import settings
from vk_api.bot_longpoll import VkBotMessageEvent
from chatbot_core import Bot
from generate_ticket import generate_ticket


def isolate_bd(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()

    return wrapper


class TestChatBot(unittest.TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'date': 1610896096, 'from_id': 88834020, 'id': 805, 'out': 0, 'peer_id': 88834020,
                   'text': 'привет', 'conversation_message_id': 805, 'fwd_messages': [], 'important': False,
                   'random_id': 0, 'attachments': [], 'is_hidden': False}, 'group_id': 198351888,
        'event_id': '1f139a1708e47819cc2ccc2956f3408ec815e996'}

    def test_run(self):
        count = 5
        event = [{}] * count  # [{}, {} ... ]
        long_pooler_mock = Mock(return_value=event)
        long_pooler_listen_mock = Mock()
        long_pooler_listen_mock.listen = long_pooler_mock
        with patch("vk_api.VkApi"):
            with patch("chatbot_core.VkBotLongPoll", return_value=long_pooler_listen_mock):
                bot = Bot(" ", " ")
                bot.on_event = Mock()
                bot.sent_image = Mock()
                bot.run()
                bot.on_event.assert_called()
                bot.on_event.assert_any_call({})
                assert bot.on_event.call_count == count

    timetable_flights = [
        ['Питербург', 'Воронеж', datetime.date(2021, 1, 18)], ['Москва', 'Питербург', datetime.date(2021, 1, 20)],
        ['Воронеж', 'Мухосранск', datetime.date(2021, 1, 20)], ['Москва', 'Питербург', datetime.date(2021, 1, 22)],
        ['Питербург', 'Воронеж', datetime.date(2021, 1, 25)], ['Москва', 'Питербург', datetime.date(2021, 1, 27)],
        ['Воронеж', 'Мухосранск', datetime.date(2021, 1, 27)], ['Питербург', 'Воронеж', datetime.date(2021, 2, 1)],
        ['Москва', 'Питербург', datetime.date(2021, 2, 3)], ['Воронеж', 'Мухосранск', datetime.date(2021, 2, 3)],
        ['Питербург', 'Воронеж', datetime.date(2021, 2, 8)], ['Москва', 'Питербург', datetime.date(2021, 2, 10)],
        ['Воронеж', 'Мухосранск', datetime.date(2021, 2, 10)], ['Питербург', 'Воронеж', datetime.date(2021, 2, 15)],
        ['Воронеж', 'Мухосранск', datetime.date(2021, 2, 15)], ['Москва', 'Питербург', datetime.date(2021, 2, 22)],
        ['Питербург', 'Воронеж', datetime.date(2021, 3, 3)], ['Воронеж', 'Мухосранск', datetime.date(2021, 3, 12)],
        ['Москва', 'Питербург', datetime.date(2021, 3, 13)]
    ]
    departure_cities_for_write = '\nВоронеж, Москва, Питербург, '
    departure_cities = ['Воронеж', 'Москва', 'Питербург']
    data_about_flights = {"timetable_flights": timetable_flights,
                          "departure_cities_for_write": departure_cities_for_write,
                          "departure_cities": departure_cities}
    IMPUTS = [
        "Здравствуйте",
        "Зарегистрируй меня",
        "Воронеж",
        "Мухосранск",
        "20-01-2021",
        "3",
        "3",
        "а",
        "да",
        "89715483246"
    ]
    EXPECTED_OUTPUTS = [
        settings.INTENTS[0]["answer"],
        settings.SCENARIOS["registration"]["steps"]["step1"]["text"].format
        (departure_cities_for_write="\nВоронеж, Москва, Питербург, "),
        settings.SCENARIOS["registration"]["steps"]["step2"]["text"].format
        (destination_cities_of_user_to_write="\nМухосранск"),
        settings.SCENARIOS["registration"]["steps"]["step3"]["text"],
        settings.SCENARIOS["registration"]["steps"]["step4"]["text"].format
        (nearest_5_flights_to_write_user="\n1.Воронеж - Мухосранск - 20-01-2021 \n"
                                         "2.Воронеж - Мухосранск - 27-01-2021 \n"
                                         "3.Воронеж - Мухосранск - 03-02-2021 \n"
                                         "4.Воронеж - Мухосранск - 10-02-2021 \n"
                                         "5.Воронеж - Мухосранск - 15-02-2021 \n"),
        settings.SCENARIOS["registration"]["steps"]["step5"]["text"],
        settings.SCENARIOS["registration"]["steps"]["step6"]["text"],
        settings.SCENARIOS["registration"]["steps"]["step7"]["text"].format
        (user_flight_of_write="Воронеж - Мухосранск - 3-2-2021", user_number_seats="3",
         comment="а"),
        settings.SCENARIOS["registration"]["steps"]["step8"]["text"],
        settings.SCENARIOS["registration"]["steps"]["step9"]["text"]
    ]
    info_user = [{'first_name': 'Лирооой', 'id': 88834020,
                   'last_name': 'Дженкинс', 'can_access_closed': True,
                   'is_closed': False}]

    @isolate_bd
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock
        api_mock.users.get = Mock(return_value=self.info_user)

        events = []
        for input_text in self.IMPUTS:
            event = deepcopy(self.RAW_EVENT)
            event["object"]['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        generate_flights_mock = Mock()
        self.data_about_flights = {}
        self.data_about_flights["timetable_flights"] = self.timetable_flights
        self.data_about_flights["departure_cities_for_write"] = self.departure_cities_for_write
        self.data_about_flights["departure_cities"] = self.departure_cities
        generate_flights_mock.run = Mock(return_value=self.data_about_flights)
        with patch("chatbot_core.VkBotLongPoll", return_value=long_poller_mock):
            with patch("chatbot_core.GenerateFlights", return_value=generate_flights_mock):
                bot = Bot("", "")
                bot.api = api_mock
                bot.flight_schedule = self.timetable_flights
                bot.sent_image = Mock()
                bot.run()
        assert send_mock.call_count == len(self.IMPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        index = 0
        for _ in range(len(self.EXPECTED_OUTPUTS)):
            self.assertEqual(real_outputs[index], self.EXPECTED_OUTPUTS[index], f"{real_outputs[index]}")
            index += 1
