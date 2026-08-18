import psycopg2
from faker import Faker
from random import choice
from datetime import date, time

def gender_assignment(gen):
    if gen == "мужской":
        first_name = fake_ru.first_name_male()
        last_name = fake_ru.last_name_male()
    else:
        first_name = fake_ru.first_name_female()
        last_name = fake_ru.last_name_female()

    return first_name, last_name


fake_ru = Faker("ru_RU")
potential_clients = []


data_diagnosis = (
    'Моторная алалия',
    'Артикуляционная диспраксия',
    'Сенсорная алалия',
    'Дизартрия',
    'Заикание',
    'Дислексия',
    'Дисграфия',
    'Дислалия',
    'Общее недоразвитие речи',
    'Фонетико-фонематическое недоразвитие речи'
)

for _ in range(20):

    gender = fake_ru.random_element(["мужской","женский"])

    [first_name, last_name] = gender_assignment(gender)


    potential_clients.append({
        "first_name": first_name,
        "last_name": last_name,
        "child_name": fake_ru.first_name(),
        "phone_number": fake_ru.phone_number(),
        "diagnosis": choice(data_diagnosis),
        "desired_time":time(
            hour=choice(range(10, 21)),
            minute=choice([0, 30])
        ),
        "request_date":fake_ru.date_between(
            start_date=date(2026, 8, 6),
            end_date=date(2026, 12, 1)
        ),
        "notes": fake_ru.text(max_nb_chars=15),
    })

with psycopg2.connect(
    dbname="db_logoped",
    user="postgres",
    password="root1234",
    host="localhost"
) as conn:
    with conn.cursor() as cursor:
        cursor.executemany("""INSERT INTO potential_clients (
        first_name,
        last_name,
        child_name,
        phone_number,
        diagnosis,
        desired_time,
        request_date,
        notes) 
        VALUES(
        %(first_name)s, 
        %(last_name)s, 
        %(child_name)s,  
        %(phone_number)s, 
        %(diagnosis)s, 
        %(desired_time)s, 
        %(request_date)s, 
        %(notes)s)""", potential_clients)
    conn.commit()



print(*potential_clients, sep ="\n")
print('Success')