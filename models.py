from pony.orm import Database, Required, Json
from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состояние пользователя внутри сценария"""
    user_id = Required(int, unique=True)
    first_name = Required(str)
    last_name = Required(str)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    """Информация о зарегистрированных пользователях"""
    user_id = Required(int)
    first_name = Required(str)
    last_name = Required(str)
    user_flight = Required(str)
    user_flight_data = Required(str)
    user_number_seats = Required(str)
    comment = Required(str)
    number_phone = Required(str)


db.generate_mapping(create_tables=True)