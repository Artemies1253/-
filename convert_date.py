from datetime import date


def convert_data_to_str(timetable_flights):
    """Конвертирования даты в строку, для записи в базу данных"""
    all_flights = []
    for city_from, city_to, data in timetable_flights:
        data = f'{data.day}-{data.month}-{data.year}'
        fligts = [city_from, city_to, data]
        all_flights.append(fligts)
    return all_flights


def convert_str_to_data(timetable_flights):
    """Конвертирование строку в дату, для работы с данными"""
    all_flights = []
    for city_from, city_to, data in timetable_flights:
        day, month, year = data.split("-")
        data = date(year=int(year), month=int(month), day=int(day))
        fligts = [city_from, city_to, data]
        all_flights.append(fligts)
    return all_flights
