INTENTS = [
    {
        "name": "Приветсвие пользователя",
        "tokens": ("прив", "здравствуйте", "ку", "хай"),
        "scenario": None,
        "answer": "Здравствуйте"
    },
    {
        "name": "Благодарность",
        "tokens": ("спасиб", "ty", "спс", "благодарю"),
        "scenario": None,
        "answer": "Всегда пожалуйста, рад был помочь"
    },
    {
        "name": "Помощь",
        "tokens": ("/help", "помощь"),
        "scenario": None,
        "answer": "Я бот, который с удовольствием поможет вам заказать билет,"
                  " для этого напишите специальную команду /ticket или просто слово регистрация"
    },
    {
        "name": "Регистрация",
        "tokens": ("/ticket", "регистр"),
        "scenario": "registration",
        "answer": None
    }
]
SCENARIOS = {
    "registration": {
        "first_step": "step1",
        "steps": {
            "step1": {
                "text": "Ведите город отправления, есть в наличии билеты из {departure_cities_for_write}",
                "failure_text": "Мы предоставляем вылеты только из следующиго"
                                " списка городов {departure_cities_for_write}",
                "handler": "handler_departure_cities",
                "next_step": "step2"

            },
            "step2": {
                "text": "Ведите город назначения, вы можете полететь в {destination_cities_of_user_to_write}",
                "failure_text": "Из {departure_citi_of_user} вы можете попасть"
                                " только в {destination_cities_of_user_to_write}, проверьте правильность написания",
                "handler": "handler_destination_city",
                "next_step": "step3"
            },
            "step3": {
                "text": "Ведите желаемую дату вылета в формате 20-01-2030",
                "failure_text": "Ведите дату в формате день,месяц, год, наприме 20-01-2030,"
                                "дата не может быть раньше сегодняшнего числа",
                "handler": "handler_data",
                "next_step": "step4"
            },
            "step4": {
                "text": "Вам на выбор предложено несколько ближайших рейсов,"
                        " ведите номер подходящего для вас {nearest_5_flights_to_write_user}",
                "failure_text": "Введите число от 1 до 5",
                "handler": "handler_choice_flight",
                "next_step": "step5"
            },
            "step5": {
                "text": "Сколько мест вы хотите забронировать (до 5)",
                "failure_text": "Введите число от 1 до 5",
                "handler": "handler_choice_number_seats",
                "next_step": "step6"
            },
            "step6": {
                "text": "Напишите комментарий к заказу ",
                "failure_text": "Сообщение должно быть не пустым",
                "handler": "handler_comment",
                "next_step": "step7"
            },
            "step7": {
                "text": "Проверьте правильность веденных данных:\n"
                        "1: Вы выбрали рейс {user_flight_of_write} \n"
                        "2: Вы забронировали {user_number_seats} билетов\n"
                        "3: Вы оставили комментий: {comment}.\n"
                        "Продолжить регистрацию",
                "failure_text": "напишите да или нет",
                "handler": "handler_check_data",
                "next_step": "step8"
            },
            "step8": {
                "text": "Введите пожалуйста номер телефона",
                "failure_text": "Введите пожалуйста номер телефона в формате 89xxxxxxxxx",
                "handler": "handler_number_phone",
                "next_step": "step9"
            },
            "step9": {
                "text": "Спасибо за заказ, с вами свяжуться в ближайшее время по указаному вами номеру телефона,"
                        " для подтверждения заказа и оплаты, вот ваш билет, не забудьте его распечатать",
                "image": "generate_ticket_handler",
                "failure_text": None,
                "handler": None,
                "next_step": None
            }
        }
    }
}

DEFAULT_ANSWER = "Я не могу ответить на этот вопрос " \
                 "Для получения справки о моих возможностях ведите {/help}, для регистрации билела ведите {/ticket}"

DB_CONFIG = dict(
    provider="sqlite",
    filename="vk_chat_bot.db",
    create_db=True
)
