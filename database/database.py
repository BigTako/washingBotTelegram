import psycopg2
from logger import log_func, logger
import config as c
import datetime as dt


@log_func
def connect_to_db():
    """Начальная ф-ия соединения с базой данный(не принимает параметров)
        Данные БД указаны в файле config.py"""
    connection = psycopg2.connect(host=c.host,
                                  user=c.user,
                                  password=c.password,
                                  database=c.db_name
                                  )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {c.table_name}(id SERIAL PRIMARY KEY,
                                                      username VARCHAR(50),
                                                      machine VARCHAR(30),
                                                      start INTEGER,
                                                      finish INTEGER)""")
    logger.info("DataBase connected successfully!")
    print("DataBase connected successfully!")
    cursor.close()
    return connection

@log_func
def write_to_db(data:tuple):
    """Записать данные в БД"""
    connection = connect_to_db()
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO {c.table_name} VALUES(DEFAULT,%s,%s,%s,%s)", data)


@log_func
def read_data_from_db():
    connection = connect_to_db()
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT * FROM {c.table_name} ORDER BY start DESC""")
        return cursor.fetchall()

@log_func
def check_time_itersection(time:str, date:str, char:str):
    """Функция проверки пересечения введеного време и времени в уже
    существующих записях. Параметры -->time(Введенное время) date(Ранее введенная дата)
    char(обозначение времени --> 's' - время начала 'f' - время конца )"""
    connection = connect_to_db()
    connection.autocommit = True
    with connection.cursor() as cursor:
        user_time = int(dt.datetime.timestamp(
            dt.datetime.strptime(date + " " + time, "%d/%m/%Y %H:%M")))
        # превратить строку времени пользователя в таймстемп для сравнения

        cursor.execute(f"SELECT start FROM {c.table_name}") # взять начальное время из всех записей(таймстемп)
        time_s = cursor.fetchall()

        cursor.execute(f"SELECT finish FROM {c.table_name}")  # взять конечное время из всех записей(таймстемп)
        time_f = cursor.fetchall()

        for t in range(len(time_s)):
            if char == "s" and int(time_f[t][0]) > user_time >= int(time_s[t][0]):
                # если время начальное и находтся в промежутке между начальным и конечным временем
                # какой-то записи(может равнятся конечному)
                return False
            elif char == "f" and int(time_f[t][0]) >= user_time > int(time_s[t][0]):
                # если время конечное и находтся в промежутке между начальным и конечным временем
                # какой-то записи(может равнятся начальному)
                return False
        return True

def delete_old():
    """Функция удаления записей, таймстемп которых меньше сегодняшнего"""
    connection = connect_to_db()
    connection.autocommit = True
    with connection.cursor() as cursor:
        today = dt.datetime.timestamp(dt.datetime.today()) # расчитать таймстемп данного момента
        cursor.execute(f"SELECT id, start FROM {c.table_name}") # взять айди и время начала из таблицы
        data = cursor.fetchall()
        for item in data:
            if int(item[1]) < today:
                cursor.execute(f"""DELETE FROM test WHERE id = {item[0]}""")
