from datetime import date, timedelta
from pprint import pprint
import random


class GenerateFlights:
    """
    Генерирует список списков перелетов из 2 списков на заданое количество  месяцов(стандартно 2)
    C первого списка будет формироваться список списков перелетов, последовательно от 1 к 2, от 2 к 3,
    время между перелётами 7 дней, первый полёт генерируется случайно в ближайшую неделю
    Второй список формирует 2 вылета в определенный день месяца между собой подобно первому
    Подаваемые списки не могут сождержать количество городов меньше 3
    1 индекс город отправки, 2 индекс город назначения, дата вылета
    """

    def __init__(self, period_week=None, same_numbers_in_month=None, month=2 ** 10):
        self.period_week = period_week or ["Москва", "Петербург", "Воронеж", "Мухосранск"]
        self.same_numbers_in_month = same_numbers_in_month or ["Анна", "Нижневартовск", "Таганрок", "Челябинск"]
        self.month = month
        self.timetable_flights = []
        self.departure_cities = []
        self.departure_cities_for_write = []
        self.data_about_flights = {}

    def run(self):
        """Генерация полотов"""
        self.generate_flights_period_7_day()
        self.generate_flights_period_month()
        self.timetable_flights.sort(key=lambda x: x[2])
        self.departure_cities = self.give_departure_cities()
        self.departure_cities_for_write = self.change_to_write(self.departure_cities)
        self.data_about_flights["timetable_flights"] = self.timetable_flights
        self.data_about_flights["departure_cities_for_write"] = self.departure_cities_for_write
        self.data_about_flights["departure_cities"] = self.departure_cities
        return self.data_about_flights

    def generate_flights_period_7_day(self):
        """Генерация случайных еженедельных полётов"""
        city_to = None
        for city in self.period_week:
            if not city_to:
                city_to = city
                continue
            city_from = city_to
            city_to = city
            today = date.today()
            random_plus_start_day = timedelta(days=random.randint(1, 7))
            date_of_flight = today + random_plus_start_day
            self.timetable_flights.append([city_from, city_to, date_of_flight])
            week_1 = timedelta(days=7)
            for _ in range(self.month * 2 - 1):
                date_of_flight += week_1
                self.timetable_flights.append([city_from, city_to, date_of_flight])
        self.timetable_flights.sort(key=lambda x: x[2])

    def generate_flights_period_month(self):
        """Генерация случайных месячных полётов"""
        city_to = None
        for city in self.same_numbers_in_month:
            if not city_to:
                city_to = city
                continue
            city_from = city_to
            city_to = city
            today = date.today()
            day_flight_number_1 = random.randint(1, 28)
            day_flight_number_2 = random.randint(1, 28)
            flight_number_1 = date(year=today.year, month=today.month, day=day_flight_number_1)
            flight_number_2 = date(year=today.year, month=today.month, day=day_flight_number_2)
            if today < flight_number_1:
                self.timetable_flights.append([city_from, city_to, flight_number_1])
            if today < flight_number_2:
                self.timetable_flights.append([city_from, city_to, flight_number_2])
            for _ in range(self.month - 1):
                month_flight = flight_number_1.month + 1
                if month_flight == 12:
                    flight_number_1 = date(
                        year=flight_number_1.year + 1,
                        month=1,
                        day=day_flight_number_1
                    )
                    flight_number_2 = date(
                        year=flight_number_2.year + 1,
                        month=1,
                        day=day_flight_number_2
                    )
                    self.timetable_flights.append([city_from, city_to, flight_number_1])
                    self.timetable_flights.append([city_from, city_to, flight_number_2])
                else:
                    flight_number_1 = date(
                        year=flight_number_1.year,
                        month=flight_number_1.month + 1,
                        day=day_flight_number_1
                    )
                    flight_number_2 = date(
                        year=flight_number_2.year,
                        month=flight_number_1.month + 1,
                        day=day_flight_number_2
                    )
                    self.timetable_flights.append([city_from, city_to, flight_number_1])
                    self.timetable_flights.append([city_from, city_to, flight_number_2])

    def give_departure_cities(self):
        """Создание списка городов отправления"""
        departure_cities = []
        for flight in self.timetable_flights:
            departure_city = flight[0]
            departure_cities.append(departure_city)
        departure_cities = set(departure_cities)
        departure_cities = list(departure_cities)
        departure_cities.sort()
        return departure_cities

    def change_to_write(self, list_flights):
        """Преобразования списка в сообщение, которое можно будет отправить пользователю"""
        text_to_sent = "\n"
        for city in list_flights:
            text_to_sent += str(f'{city}, ')
        return text_to_sent


if __name__ == "__main__":
    genetator = GenerateFlights()
    genetator.run()

# today = date.today()
# print(today)
# print(today.day)
