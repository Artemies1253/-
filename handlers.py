"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True если шаг пройден, False если данные введены неправильно.
Если шаг пройден записывает в баззу данных ответ пользователю и информацию, которую он дал
"""
import calendar
import re
from datetime import date
from convert_date import convert_data_to_str, convert_str_to_data
from generate_ticket import generate_ticket

POSITIVE_RESPONSE = ["да", "продол", "регистр", "даль", "next", "yes", "ok"]
NEGATIVE_RESPONSE = ["не", "верн", "измен"]


def handler_departure_cities(text, state):
    if len(text) < 3:
        return False
    for city in state.context["departure_cities"]:
        if city[:-1].lower() in text:
            state.context["departure_citi_of_user"] = city
            data_destination_cities_of_user = give_destination_cities_of_user(
                departure_citi_of_user=city,
                flight_schedule=convert_str_to_data(state.context["flight_schedule"])
            )
            destination_cities_of_user = data_destination_cities_of_user["destination_cities"]
            destination_cities_of_user_to_write = data_destination_cities_of_user["destination_cities_to_write"]
            state.context["destination_cities_of_user_to_write"] = destination_cities_of_user_to_write
            state.context["destination_cities_of_user"] = destination_cities_of_user
            return True
    return False


def handler_destination_city(text, state):
    destination_cities = state.context["destination_cities_of_user"]
    if len(text) < 3:
        return False
    for city in destination_cities:
        if city[:-1].lower() in text:
            state.context["destination_cities_of_user"] = city
            flight_schedule = convert_str_to_data(state.context["flight_schedule"])
            all_possible_flights_of_user = give_all_possible_flights_of_user(
                state=state,
                flight_schedule=flight_schedule
            )
            state.context["all_possible_flights_of_user"] = convert_data_to_str(all_possible_flights_of_user)
            return True
    return False


def handler_data(text, state):
    if not re.match(r'\d{2}-\d{2}-\d{4}', text):
        return False
    if not len(text) == 10:
        return False
    today = date.today()
    min_year = int(today.year)
    max_year = give_max_year(state=state)
    day, month, year = text.split("-")
    day, month, year = int(day), int(month), int(year)
    max_day = calendar.monthrange(year=year, month=month)[1]
    if not 1 <= day <= max_day:
        return False
    if not 1 <= month <= 12:
        return False
    if not min_year <= year <= max_year:
        return False
    data_flights = date(year=year, month=month, day=day)
    data_flights_str = f'{day}.{month}.{year}'
    state.context["data_flights"] = data_flights_str
    all_possible_flights_of_user = convert_str_to_data(state.context["all_possible_flights_of_user"])
    nearest_5_flights = give_5_nearest_flights(data_flight_user=data_flights,
                                               flight_schedule=all_possible_flights_of_user)
    state.context["nearest_5_flights"] = convert_data_to_str(nearest_5_flights)
    state.context["nearest_5_flights_to_write_user"] = change_to_write(nearest_5_flights)
    return True


def handler_choice_flight(text, state):
    if not text.isdigit():
        return False
    text = int(text)
    if not 1 <= text <= 5:
        return False
    user_flight = state.context["nearest_5_flights"][text - 1]
    departure_city = user_flight[0]
    destination_city = user_flight[1]
    date_flight = user_flight[2]
    state.context["user_flight"] = user_flight
    state.context["destination_city"] = departure_city
    state.context["user_flight_of_write"] = f'{departure_city} - {destination_city}' \
                                            f' - {date_flight}'
    return True


def handler_choice_number_seats(text, state):
    if not text.isdigit():
        return False
    text = int(text)
    if not 1 <= text <= 5:
        return False
    user_number_seats = str(text)
    state.context["user_number_seats"] = user_number_seats
    return True


def handler_comment(text, state):
    state.context["comment"] = text
    return True


def handler_check_data(text, state):
    if any(response in text for response in POSITIVE_RESPONSE):
        return True
    if any(response in text for response in NEGATIVE_RESPONSE):
        state.step_name = "step1"
        return False
    return False


def handler_number_phone(text, state):
    if not re.findall(r'\d{10}$', text):
        return False
    phone = re.findall(r'(\d{10})$', text)
    state.context["phone"] = "+7" + phone[0]
    return True


def generate_ticket_handler(text, state):
    return generate_ticket(
        first_name=state.first_name,
        last_name=state.last_name,
        city_from=state.context["destination_cities_of_user_to_write"],
        city_to=state.context["destination_city"],
        data=state.context["data_flights"]
        )


def give_destination_cities_of_user(departure_citi_of_user, flight_schedule):
    destination_cities = []
    for flight in flight_schedule:
        departure_citi = flight[0]
        destination_city = flight[1]
        if departure_citi == departure_citi_of_user:
            destination_cities.append(destination_city)
    destination_cities = set(destination_cities)
    destination_cities = list(destination_cities)
    destination_cities_to_write = "\n"
    if len(destination_cities) == 1:
        destination_cities_to_write += destination_cities[0]
    else:
        for city in destination_cities:
            destination_cities_to_write += city
    data_destination_cities = {
        'destination_cities': destination_cities,
        'destination_cities_to_write': destination_cities_to_write
    }
    return data_destination_cities


def give_max_year(state):
    flights = convert_str_to_data(state.context["all_possible_flights_of_user"])
    date_last_flight = flights[-1][2]
    max_year = date_last_flight.year
    return max_year


def give_all_possible_flights_of_user(state, flight_schedule):
    from_city_user = state.context["departure_citi_of_user"]
    to_city_user = state.context["destination_cities_of_user"]
    all_possible_flights_of_user = []
    for flight in flight_schedule:
        from_city = flight[0]
        to_city = flight[1]
        if from_city == from_city_user:
            if to_city == to_city_user:
                all_possible_flights_of_user.append(flight)
    return all_possible_flights_of_user


def give_5_nearest_flights(data_flight_user, flight_schedule):
    flight_schedule = flight_schedule
    flight_schedule_with_flight_user = []
    flight_schedule_with_flight_user.extend(flight_schedule)
    flight_schedule_with_flight_user.append(["", "", data_flight_user])
    flight_schedule_with_flight_user.sort(key=lambda x: x[2])
    data_flight_with_data_user = []
    for town_from, town_to, data_flight in flight_schedule_with_flight_user:
        data_flight_with_data_user.append(data_flight)
    index_data_user = data_flight_with_data_user.index(data_flight_user)
    nearest_5_flights = []
    index_neatest_flight = index_data_user
    count = 0
    for _ in range(len(flight_schedule) - index_data_user - 1):
        nearest_5_flights.append(flight_schedule[index_neatest_flight])
        index_neatest_flight += 1
        count += 1
        if count == 5:
            break
    return nearest_5_flights


def change_to_write(list_flights):
    text_to_sent = "\n"
    number_offer = 1
    for city_from, city_to, data_flight in list_flights:
        data_flight = data_flight.strftime("%d-%m-%Y")
        text_to_sent += str(f'{number_offer}.{city_from} - {city_to} - {data_flight} \n')
        number_offer += 1
    return text_to_sent
